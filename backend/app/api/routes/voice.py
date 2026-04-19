from __future__ import annotations

import os
import re
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.models.onboarding import (
    ChecklistItem,
    ChecklistItemStatus,
    Client,
    ClientStatus,
    Country,
    EntityType,
    Firm,
    FirmUser,
    FirmUserRole,
    MessageChannel,
    MessageDeliveryStatus,
    OnboardingActivity,
    WhatsAppLog,
)
from app.services import checklist_generator
from app.services.completion import recompute_client_completion
from app.services.email_service import send_slack_alert
from app.services.messaging import send_message
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


def _portal_url(firm: Firm, client: Client) -> str:
    base = get_settings().frontend_url.rstrip("/")
    return f"{base}/portal/{firm.slug}/{client.onboarding_token}"


def _norm_email(s: str) -> str:
    return (s or "").strip().lower()


def _digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


@router.get("/lookup")
def voice_lookup(
    email: str,
    firm_slug: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = db.query(Firm).filter(Firm.slug == firm_slug).first()
    if not firm:
        return {"found": False}
    em = _norm_email(email)
    client = (
        db.query(Client)
        .filter(Client.firm_id == firm.id, Client.email.ilike(em))
        .first()
    )
    if not client:
        return {"found": False}

    pending_items = (
        db.query(ChecklistItem)
        .filter(
            ChecklistItem.client_id == client.id,
            ChecklistItem.status == ChecklistItemStatus.pending,
        )
        .order_by(ChecklistItem.display_order)
        .all()
    )
    uploaded_review = (
        db.query(ChecklistItem)
        .filter(
            ChecklistItem.client_id == client.id,
            ChecklistItem.status == ChecklistItemStatus.uploaded,
        )
        .count()
    )

    assignee_name = None
    if client.assigned_to:
        fu = db.query(FirmUser).filter(FirmUser.id == client.assigned_to).first()
        if fu:
            assignee_name = fu.full_name

    return {
        "found": True,
        "client_name": client.client_name,
        "business_name": client.business_name or client.client_name,
        "status": client.status.value,
        "completion_pct": client.completion_pct,
        "pending_count": len(pending_items),
        "uploaded_awaiting_review": uploaded_review,
        "pending_items": [p.item_name for p in pending_items],
        "portal_link": _portal_url(firm, client),
        "phone": client.phone,
        "assigned_to_name": assignee_name,
    }


class SendPortalLinkBody(BaseModel):
    email: EmailStr
    firm_slug: str


@router.post("/send-portal-link")
def send_portal_link(
    body: SendPortalLinkBody,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = db.query(Firm).filter(Firm.slug == body.firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    client = (
        db.query(Client)
        .filter(Client.firm_id == firm.id, Client.email == str(body.email))
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    portal = _portal_url(firm, client)
    variables = {
        "client_name": client.client_name,
        "firm_name": firm.name,
        "portal_link": portal,
        "doc_count": str(client.completion_pct),
        "deadline": "Soon",
        "completion_pct": str(client.completion_pct),
        "pending_items": "See portal",
    }
    result = send_sms(client.phone, "portal_link_via_voice", variables)
    log = WhatsAppLog(
        client_id=client.id,
        firm_id=firm.id,
        channel=MessageChannel.sms,
        message_type="portal_link_via_voice",
        phone_number=client.phone,
        message_content=portal,
        status=MessageDeliveryStatus.sent if result.get("status") == "sent" else MessageDeliveryStatus.failed,
    )
    db.add(log)
    db.add(
        OnboardingActivity(
            client_id=client.id,
            firm_id=firm.id,
            action="portal_link_sent_by_voice_agent",
            description="Portal link sent via SMS from voice flow",
            performed_by="aria_voice_agent",
        )
    )
    db.commit()
    return {
        "sent": result.get("status") == "sent",
        "phone": client.phone,
        "message": "SMS sent successfully" if result.get("status") == "sent" else (result.get("error") or "SMS failed"),
    }


class LogCallBody(BaseModel):
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
    db: Session = Depends(get_db),
    _: bool = Depends(verify_vapi_secret),
):
    firm = db.query(Firm).filter(Firm.slug == body.firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")

    client: Client | None = None
    if body.caller_email:
        client = (
            db.query(Client)
            .filter(Client.firm_id == firm.id, Client.email.ilike(_norm_email(body.caller_email)))
            .first()
        )
    if not client and body.caller_phone:
        d = _digits(body.caller_phone)
        if d:
            for c in db.query(Client).filter(Client.firm_id == firm.id).all():
                if _digits(c.phone) == d:
                    client = c
                    break

    activity_id: str | None = None
    client_id_out: str | None = None

    if body.call_type == "new_enquiry" and body.outcome == "booked_appointment":
        if not body.caller_email or not body.caller_phone:
            raise HTTPException(status_code=400, detail="caller_email and caller_phone required for new enquiry")
        existing = (
            db.query(Client)
            .filter(Client.firm_id == firm.id, Client.email.ilike(_norm_email(body.caller_email)))
            .first()
        )
        if existing:
            client = existing
        else:
            active_count = db.query(Client).filter(Client.firm_id == firm.id).count()
            if active_count >= firm.plan_client_limit:
                raise HTTPException(status_code=400, detail="Firm client limit reached")
            try:
                co = Country(firm.country)
            except ValueError:
                co = Country.India
            name = (body.caller_name or body.caller_email.split("@")[0]).strip() or "New client"
            nc = Client(
                firm_id=firm.id,
                client_name=name,
                business_name=None,
                email=_norm_email(body.caller_email),
                phone=body.caller_phone,
                country=co,
                entity_type=EntityType.other,
                services=[],
                onboarding_link="",
                status=ClientStatus.invited,
            )
            db.add(nc)
            db.flush()
            nc.onboarding_link = _portal_url(firm, nc)
            specs = checklist_generator.generate_checklist(co.value, EntityType.other.value, [])
            for spec in specs:
                db.add(
                    ChecklistItem(
                        client_id=nc.id,
                        category=spec["category"],
                        item_name=spec["item_name"],
                        description=spec["description"],
                        is_required=spec["is_required"],
                        display_order=spec["display_order"],
                    )
                )
            recompute_client_completion(db, nc)
            client = nc

    if client:
        client.last_activity_at = datetime.utcnow()
        db.add(client)
        act = OnboardingActivity(
            client_id=client.id,
            firm_id=firm.id,
            action=f"voice_call_{body.call_type}",
            description=f"{body.outcome} — {body.notes}".strip(),
            performed_by="aria_voice_agent",
        )
        db.add(act)
        db.flush()
        activity_id = str(act.id)
        client_id_out = str(client.id)

    if body.escalated:
        webhook = os.getenv("SLACK_WEBHOOK_URL") or get_settings().slack_webhook_url
        display = body.caller_name or (client.client_name if client else "Unknown caller")
        send_slack_alert(
            webhook or "",
            (
                f"ESCALATION: {display} called and requested human. "
                f"Call type: {body.call_type}. Notes: {body.notes}"
            ),
        )

    db.commit()
    return {"logged": True, "client_id": client_id_out, "activity_id": activity_id}


@router.post("/trigger-reminders")
def trigger_reminders(_: bool = Depends(verify_vapi_secret)):
    run_daily_reminders()
    return {"ok": True}
