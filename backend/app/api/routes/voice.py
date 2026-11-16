from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from supabase import Client

from app.core.config import get_settings
from app.db import get_db
from app.db import repo
from app.db.urls import portal_link
from app.models.enums import (
    ClientStatus,
    Country,
    EntityType,
    MessageChannel,
    MessageDeliveryStatus,
)
from app.services import checklist_generator
from app.services.completion import recompute_client_completion
from app.services.email_service import send_slack_alert
from app.services.reminder_engine import run_daily_reminders
from app.services.sms_service import send_sms

router = APIRouter()


def verify_vapi_secret(x_vapi_secret: str | None = Header(None, alias="X-VAPI-Secret")) -> bool:
    expected = os.getenv("VAPI_WEBHOOK_SECRET") or get_settings().vapi_webhook_secret
    if not expected:
        raise HTTPException(status_code=503, detail="VAPI webhook secret not configured")
    if x_vapi_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid VAPI secret")
    return True


def _norm_email(s: str) -> str:
    return (s or "").strip().lower()


def _digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


@router.get("/lookup")
def voice_lookup(
    email: str,
    firm_slug: str,
    sb: Client = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = repo.firm_by_slug(sb, firm_slug)
    if not firm:
        return {"found": False}
    fid = uuid.UUID(str(firm["id"]))
    em = _norm_email(email)
    client = repo.clients_for_firm_email(sb, fid, em)
    if not client:
        return {"found": False}
    cid = uuid.UUID(str(client["id"]))
    pending_items = repo.checklist_pending_for_client(sb, cid)
    uploaded_review = repo.checklist_uploaded_count(sb, cid)

    assignee_name = None
    if client.get("assigned_to"):
        fu = repo.firm_user_by_id(sb, uuid.UUID(str(client["assigned_to"])))
        if fu:
            assignee_name = fu["full_name"]

    pl = portal_link(get_settings().frontend_url, firm["slug"], client["onboarding_token"])
    return {
        "found": True,
        "client_name": client["client_name"],
        "business_name": client.get("business_name") or client["client_name"],
        "status": client["status"],
        "completion_pct": client.get("completion_pct", 0),
        "pending_count": len(pending_items),
        "uploaded_awaiting_review": uploaded_review,
        "pending_items": [p["item_name"] for p in pending_items],
        "portal_link": pl,
        "phone": client["phone"],
        "assigned_to_name": assignee_name,
    }


class SendPortalLinkBody(BaseModel):
    email: EmailStr
    firm_slug: str


@router.post("/send-portal-link")
def send_portal_link(
    body: SendPortalLinkBody,
    sb: Client = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = repo.firm_by_slug(sb, body.firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    fid = uuid.UUID(str(firm["id"]))
    client = repo.clients_for_firm_email(sb, fid, str(body.email))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    portal = portal_link(get_settings().frontend_url, firm["slug"], client["onboarding_token"])
    variables = {
        "client_name": client["client_name"],
        "firm_name": firm["name"],
        "portal_link": portal,
        "doc_count": str(client.get("completion_pct", 0)),
        "deadline": "Soon",
        "completion_pct": str(client.get("completion_pct", 0)),
        "pending_items": "See portal",
    }
    result = send_sms(client["phone"], "portal_link_via_voice", variables)
    cid = uuid.UUID(str(client["id"]))
    repo.insert_whatsapp_log(
        sb,
        client_id=cid,
        firm_id=fid,
        channel=MessageChannel.sms.value,
        message_type="portal_link_via_voice",
        phone_number=client["phone"],
        message_content=portal,
        status=MessageDeliveryStatus.sent.value if result.get("status") == "sent" else MessageDeliveryStatus.failed.value,
    )
    repo.insert_activity(
        sb,
        client_id=cid,
        firm_id=fid,
        action="portal_link_sent_by_voice_agent",
        description="Portal link sent via SMS from voice flow",
        performed_by="aria_voice_agent",
    )
    return {
        "sent": result.get("status") == "sent",
        "phone": client["phone"],
        "message": "SMS sent successfully" if result.get("status") == "sent" else (result.get("error") or "SMS failed"),
    }


class LogCallBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    firm_slug: str
    caller_email: str | None = None
    caller_phone: str | None = None
    caller_name: str | None = None
    call_type: str = Field(pattern="^(document_status|return_status|new_enquiry|appointment|escalation)$")
    outcome: str = Field(pattern="^(resolved|portal_link_sent|booked_appointment|escalated|no_client_found)$")
    duration_seconds: int = 0
    notes: str = ""
    escalated: bool = False
    vapi_call_id: str | None = None


@router.post("/log-call")
def log_call(
    body: LogCallBody,
    sb: Client = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = repo.firm_by_slug(sb, body.firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    fid = uuid.UUID(str(firm["id"]))

    client: dict | None = None
    if body.caller_email:
        client = repo.clients_for_firm_email(sb, fid, _norm_email(body.caller_email))
    if not client and body.caller_phone:
        d = _digits(body.caller_phone)
        if d:
            for c in repo.all_clients_firm_phone_match(sb, fid):
                if _digits(c.get("phone", "")) == d:
                    client = c
                    break

    activity_id: str | None = None
    client_id_out: str | None = None

    if body.call_type == "new_enquiry" and body.outcome == "booked_appointment":
        if not body.caller_email or not body.caller_phone:
            raise HTTPException(status_code=400, detail="caller_email and caller_phone required for new enquiry")
        existing = repo.clients_for_firm_email(sb, fid, _norm_email(body.caller_email))
        if existing:
            client = existing
        else:
            if repo.count_clients_firm(sb, fid) >= int(firm.get("plan_client_limit") or 10):
                raise HTTPException(status_code=400, detail="Firm client limit reached")
            try:
                co = Country(firm["country"])
            except ValueError:
                co = Country.India
            name = (body.caller_name or body.caller_email.split("@")[0]).strip() or "New client"
            tok = uuid.uuid4()
            link = portal_link(get_settings().frontend_url, firm["slug"], tok)
            ins = (
                sb.table("clients")
                .insert(
                    {
                        "firm_id": str(fid),
                        "client_name": name,
                        "business_name": None,
                        "email": _norm_email(body.caller_email),
                        "phone": body.caller_phone,
                        "country": co.value,
                        "entity_type": EntityType.other.value,
                        "services": [],
                        "onboarding_link": link,
                        "onboarding_token": str(tok),
                        "status": ClientStatus.invited.value,
                    }
                )
                .execute()
            )
            if not ins.data:
                raise HTTPException(status_code=500, detail="Failed to create client")
            nc = ins.data[0]
            ncid = uuid.UUID(str(nc["id"]))
            specs = checklist_generator.generate_checklist(co.value, EntityType.other.value, [])
            rows = [
                {
                    "client_id": str(ncid),
                    "category": spec["category"],
                    "item_name": spec["item_name"],
                    "description": spec["description"],
                    "is_required": spec["is_required"],
                    "display_order": spec["display_order"],
                }
                for spec in specs
            ]
            if rows:
                sb.table("checklist_items").insert(rows).execute()
            recompute_client_completion(sb, ncid)
            client = repo.client_by_id(sb, ncid, fid)

    if client:
        cid = uuid.UUID(str(client["id"]))
        repo.update_client(sb, cid, {"last_activity_at": datetime.now(timezone.utc).isoformat()})
        act = repo.insert_activity(
            sb,
            client_id=cid,
            firm_id=fid,
            action=f"voice_call_{body.call_type}",
            description=f"{body.outcome} — {body.notes}".strip(),
            performed_by="aria_voice_agent",
        )
        if act:
            activity_id = str(act["id"])
        client_id_out = str(cid)

    if body.escalated:
        webhook = os.getenv("SLACK_WEBHOOK_URL") or get_settings().slack_webhook_url
        display = body.caller_name or (client["client_name"] if client else "Unknown caller")
        send_slack_alert(
            webhook or "",
            (
                f"ESCALATION: {display} called and requested human. "
                f"Call type: {body.call_type}. Notes: {body.notes}"
            ),
        )

    return {"logged": True, "client_id": client_id_out, "activity_id": activity_id}


@router.post("/trigger-reminders")
def trigger_reminders(_: bool = Depends(verify_vapi_secret)):
    run_daily_reminders()
    return {"ok": True}
