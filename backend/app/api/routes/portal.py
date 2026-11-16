from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr
from supabase import Client

from app.core.config import get_settings
from app.db import get_db, get_supabase
from app.db import repo
from app.db.urls import portal_link
from app.models.enums import (
    ClientStatus,
    Country,
    EntityType,
    MessageChannel,
    MessageDeliveryStatus,
)
from app.services import checklist_generator, storage_service
from app.services.completion import recompute_client_completion
from app.services.document_classifier import classify_document
from app.services.email_service import send_document_alert
from app.services.messaging import send_message

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024


def _notify_staff_after_upload(
    client_id: uuid.UUID,
    firm_id: uuid.UUID,
    document_type: str | None,
    confidence: float | None,
) -> None:
    sb = get_supabase()
    try:
        client = repo.client_by_id(sb, client_id)
        firm = repo.firm_by_id(sb, firm_id)
        if not client or not firm:
            return
        to_email: str | None = None
        if client.get("assigned_to"):
            fu = repo.firm_user_by_id(sb, uuid.UUID(str(client["assigned_to"])))
            if fu:
                to_email = fu["email"]
        if not to_email:
            owner = repo.owner_user_for_firm(sb, firm_id)
            if owner:
                to_email = owner["email"]
        if to_email:
            send_document_alert(
                to_email,
                client["client_name"],
                document_type or "Document",
                float(confidence or 0),
                str(client["id"]),
                firm["name"],
            )
    except Exception:
        pass


class SelfRegisterBody(BaseModel):
    client_name: str
    business_name: str | None = None
    email: EmailStr
    phone: str
    country: str
    entity_type: str
    services: list[str] = []
    financial_year_end: str | None = None


@router.post("/{firm_slug}/self-register")
def self_register(
    firm_slug: str,
    body: SelfRegisterBody,
    sb: Client = Depends(get_db),
):
    firm = repo.firm_by_slug(sb, firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    fid = uuid.UUID(str(firm["id"]))
    if repo.count_clients_firm(sb, fid) >= int(firm.get("plan_client_limit") or 10):
        raise HTTPException(status_code=400, detail="Firm client limit reached")
    try:
        country = Country(body.country)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid country") from e
    try:
        entity = EntityType(body.entity_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid entity_type") from e

    tok = uuid.uuid4()
    link = portal_link(get_settings().frontend_url, firm_slug, tok)
    cr = (
        sb.table("clients")
        .insert(
            {
                "firm_id": str(fid),
                "client_name": body.client_name,
                "business_name": body.business_name,
                "email": str(body.email).lower(),
                "phone": body.phone,
                "country": country.value,
                "entity_type": entity.value,
                "services": body.services,
                "financial_year_end": body.financial_year_end,
                "onboarding_link": link,
                "onboarding_token": str(tok),
                "status": ClientStatus.invited.value,
            }
        )
        .execute()
    )
    if not cr.data:
        raise HTTPException(status_code=500, detail="Failed to create client")
    client = cr.data[0]
    cid = uuid.UUID(str(client["id"]))

    specs = checklist_generator.generate_checklist(country.value, entity.value, body.services)
    rows = [
        {
            "client_id": str(cid),
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
    recompute_client_completion(sb, cid)
    repo.insert_activity(
        sb,
        client_id=cid,
        firm_id=fid,
        action="self_registered",
        description="Client self-registered via public link",
        performed_by="client",
    )

    doc_count = len(specs)
    variables = {
        "client_name": client["client_name"],
        "firm_name": firm["name"],
        "portal_link": client["onboarding_link"],
        "doc_count": str(doc_count),
        "deadline": "TBD",
        "completion_pct": str(client.get("completion_pct", 0)),
        "pending_items": "See portal",
    }
    send_message(client["phone"], "welcome", variables)
    repo.insert_whatsapp_log(
        sb,
        client_id=cid,
        firm_id=fid,
        channel=MessageChannel.whatsapp.value,
        message_type="welcome_self_register",
        phone_number=client["phone"],
        message_content="welcome",
        status=MessageDeliveryStatus.sent.value,
    )

    return {"success": True, "message": "Portal link sent to your WhatsApp"}


@router.get("/{firm_slug}/info")
def portal_firm_public_info(firm_slug: str, sb: Client = Depends(get_db)):
    firm = repo.firm_by_slug(sb, firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    logo_url: str | None = None
    raw = (firm.get("logo_url") or "").strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        logo_url = raw
    elif raw:
        try:
            logo_url = storage_service.get_signed_url(raw, expires_in=86400)
        except Exception:
            logo_url = None
    return {
        "firm_name": firm["name"],
        "firm_slug": firm["slug"],
        "primary_color": firm["primary_color"],
        "logo_url": logo_url,
        "whatsapp_number": firm.get("whatsapp_number"),
        "country": firm["country"],
    }


def _match_item(sb, client_id: uuid.UUID, doc_type: str | None) -> dict | None:
    if not doc_type:
        return None
    dt = doc_type.strip().lower()
    items = repo.checklist_pending_for_client(sb, client_id)
    for it in items:
        if it["item_name"].strip().lower() == dt:
            return it
    for it in items:
        inn = it["item_name"].lower()
        if dt in inn or inn in dt:
            return it
    return None


@router.get("/{firm_slug}/{token}")
def portal_get(firm_slug: str, token: uuid.UUID, sb: Client = Depends(get_db)):
    firm = repo.firm_by_slug(sb, firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Not found")
    fid = uuid.UUID(str(firm["id"]))
    client = repo.client_by_token(sb, fid, token)
    if not client:
        raise HTTPException(status_code=404, detail="Not found")
    cid = uuid.UUID(str(client["id"]))
    items = repo.checklist_items_for_client(sb, cid)
    logo = firm.get("logo_url")
    return {
        "firm_name": firm["name"],
        "firm_logo_url": logo,
        "firm_primary_color": firm["primary_color"],
        "firm_whatsapp_number": firm.get("whatsapp_number"),
        "client_name": client["client_name"],
        "completion_pct": client.get("completion_pct", 0),
        "checklist_items": [
            {
                "id": str(i["id"]),
                "category": i["category"],
                "item_name": i["item_name"],
                "description": i.get("description", ""),
                "status": i["status"],
                "is_required": i.get("is_required", True),
            }
            for i in items
        ],
    }


@router.post("/{firm_slug}/{token}/upload")
async def portal_upload(
    firm_slug: str,
    token: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    sb: Client = Depends(get_db),
):
    firm = repo.firm_by_slug(sb, firm_slug)
    if not firm:
        raise HTTPException(status_code=404, detail="Not found")
    fid = uuid.UUID(str(firm["id"]))
    client = repo.client_by_token(sb, fid, token)
    if not client:
        raise HTTPException(status_code=404, detail="Not found")
    cid = uuid.UUID(str(client["id"]))

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    mime = file.content_type or "application/octet-stream"
    try:
        meta = storage_service.upload_document(
            data, str(fid), str(cid), file.filename or "upload.bin", mime
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    ins = (
        sb.table("documents")
        .insert(
            {
                "client_id": str(cid),
                "firm_id": str(fid),
                "filename": meta["filename"],
                "original_filename": meta["original_filename"],
                "storage_path": meta["storage_path"],
                "file_size": meta["file_size"],
                "mime_type": mime,
                "uploaded_by": "client",
            }
        )
        .execute()
    )
    if not ins.data:
        raise HTTPException(status_code=500, detail="Upload failed")
    doc = ins.data[0]
    doc_id = uuid.UUID(str(doc["id"]))

    ai = classify_document(
        data, meta["original_filename"], mime, expected_type=None, country=client["country"]
    )
    patch = {
        "ai_document_type": ai.get("document_type"),
        "ai_confidence": float(ai.get("confidence") or 0),
        "ai_verified": bool(ai.get("verified")),
        "ai_issues": ai.get("issues") or [],
    }
    matched = _match_item(sb, cid, patch.get("ai_document_type"))
    if matched:
        mid = uuid.UUID(str(matched["id"]))
        patch["checklist_item_id"] = str(mid)
        repo.update_checklist_item(sb, mid, {"status": "uploaded", "document_id": str(doc_id)})
    repo.update_document(sb, doc_id, patch)

    repo.update_client(sb, cid, {"last_activity_at": datetime.now(timezone.utc).isoformat()})
    recompute_client_completion(sb, cid)
    repo.insert_activity(
        sb,
        client_id=cid,
        firm_id=fid,
        action="client_upload",
        description=f"Uploaded {meta['original_filename']}",
        performed_by="client",
    )
    wn = firm.get("whatsapp_number")
    if wn:
        repo.insert_whatsapp_log(
            sb,
            client_id=cid,
            firm_id=fid,
            channel=MessageChannel.whatsapp.value,
            message_type="client_upload",
            phone_number=wn,
            message_content=f"Client {client['client_name']} uploaded a document",
            status=MessageDeliveryStatus.sent.value,
        )

    background_tasks.add_task(
        _notify_staff_after_upload,
        cid,
        fid,
        patch.get("ai_document_type"),
        patch.get("ai_confidence"),
    )

    doc_row = repo.document_by_id(sb, doc_id, fid) or doc
    return {
        "document_type": doc_row.get("ai_document_type"),
        "confidence": doc_row.get("ai_confidence"),
        "verified": doc_row.get("ai_verified"),
        "issues": doc_row.get("ai_issues") or [],
        "matched_item": matched["item_name"] if matched else None,
    }
