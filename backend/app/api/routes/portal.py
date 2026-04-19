from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import SessionLocal, get_db
from app.models.onboarding import (
    ChecklistItem,
    ChecklistItemStatus,
    Client,
    ClientStatus,
    Country,
    Document,
    EntityType,
    Firm,
    FirmUser,
    FirmUserRole,
    MessageChannel,
    MessageDeliveryStatus,
    OnboardingActivity,
    WhatsAppLog,
)
from app.services import checklist_generator, storage_service
from app.services.completion import recompute_client_completion
from app.services.document_classifier import classify_document
from app.services.email_service import send_document_alert
from app.services.messaging import send_message

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024


def _portal_url(firm: Firm, client: Client) -> str:
    base = get_settings().frontend_url.rstrip("/")
    return f"{base}/portal/{firm.slug}/{client.onboarding_token}"


def _notify_staff_after_upload(
    client_id: uuid.UUID,
    firm_id: uuid.UUID,
    document_type: str | None,
    confidence: float | None,
) -> None:
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        firm = db.query(Firm).filter(Firm.id == firm_id).first()
        if not client or not firm:
            return
        to_email: str | None = None
        if client.assigned_to:
            fu = db.query(FirmUser).filter(FirmUser.id == client.assigned_to).first()
            if fu:
                to_email = fu.email
        if not to_email:
            owner = (
                db.query(FirmUser)
                .filter(FirmUser.firm_id == firm.id, FirmUser.role == FirmUserRole.owner, FirmUser.is_active.is_(True))
                .first()
            )
            if owner:
                to_email = owner.email
        if to_email:
            send_document_alert(
                to_email,
                client.client_name,
                document_type or "Document",
                float(confidence or 0),
                str(client.id),
                firm.name,
            )
    finally:
        db.close()


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
    db: Session = Depends(get_db),
):
    firm = db.query(Firm).filter(Firm.slug == firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    active = db.query(Client).filter(Client.firm_id == firm.id).count()
    if active >= firm.plan_client_limit:
        raise HTTPException(status_code=400, detail="Firm client limit reached")
    try:
        country = Country(body.country)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid country") from e
    try:
        entity = EntityType(body.entity_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid entity_type") from e

    client = Client(
        firm_id=firm.id,
        client_name=body.client_name,
        business_name=body.business_name,
        email=str(body.email),
        phone=body.phone,
        country=country,
        entity_type=entity,
        services=body.services,
        financial_year_end=body.financial_year_end,
        onboarding_link="",
        status=ClientStatus.invited,
    )
    db.add(client)
    db.flush()
    client.onboarding_link = _portal_url(firm, client)
    specs = checklist_generator.generate_checklist(country.value, entity.value, body.services)
    for spec in specs:
        db.add(
            ChecklistItem(
                client_id=client.id,
                category=spec["category"],
                item_name=spec["item_name"],
                description=spec["description"],
                is_required=spec["is_required"],
                display_order=spec["display_order"],
            )
        )
    recompute_client_completion(db, client)
    db.add(
        OnboardingActivity(
            client_id=client.id,
            firm_id=firm.id,
            action="self_registered",
            description="Client self-registered via public link",
            performed_by="client",
        )
    )
    db.commit()
    db.refresh(client)

    doc_count = len(specs)
    variables = {
        "client_name": client.client_name,
        "firm_name": firm.name,
        "portal_link": client.onboarding_link,
        "doc_count": str(doc_count),
        "deadline": "TBD",
        "completion_pct": str(client.completion_pct),
        "pending_items": "See portal",
    }
    send_message(client.phone, "welcome", variables)
    log = WhatsAppLog(
        client_id=client.id,
        firm_id=firm.id,
        channel=MessageChannel.whatsapp,
        message_type="welcome_self_register",
        phone_number=client.phone,
        message_content="welcome",
        status=MessageDeliveryStatus.sent,
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": "Portal link sent to your WhatsApp"}


@router.get("/{firm_slug}/info")
def portal_firm_public_info(firm_slug: str, db: Session = Depends(get_db)):
    """Public firm branding for self-registration (no auth). Safe fields only."""
    firm = db.query(Firm).filter(Firm.slug == firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    logo_url: str | None = None
    if firm.logo_url:
        raw = firm.logo_url.strip()
        if raw.startswith("http://") or raw.startswith("https://"):
            logo_url = raw
        else:
            try:
                logo_url = storage_service.get_signed_url(raw, expires_in=86400)
            except Exception:
                logo_url = None
    return {
        "firm_name": firm.name,
        "firm_slug": firm.slug,
        "primary_color": firm.primary_color,
        "logo_url": logo_url,
        "whatsapp_number": firm.whatsapp_number,
        "country": firm.country,
    }


def _match_item(db: Session, client_id: uuid.UUID, doc_type: str | None) -> ChecklistItem | None:
    if not doc_type:
        return None
    dt = doc_type.strip().lower()
    items = (
        db.query(ChecklistItem)
        .filter(
            ChecklistItem.client_id == client_id,
            ChecklistItem.status == ChecklistItemStatus.pending,
        )
        .all()
    )
    for it in items:
        if it.item_name.strip().lower() == dt:
            return it
    for it in items:
        if dt in it.item_name.lower() or it.item_name.lower() in dt:
            return it
    return None


@router.get("/{firm_slug}/{token}")
def portal_get(firm_slug: str, token: uuid.UUID, db: Session = Depends(get_db)):
    firm = db.query(Firm).filter(Firm.slug == firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Not found")
    client = db.query(Client).filter(Client.onboarding_token == token, Client.firm_id == firm.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Not found")
    items = (
        db.query(ChecklistItem).filter(ChecklistItem.client_id == client.id).order_by(ChecklistItem.display_order).all()
    )
    logo = firm.logo_url
    return {
        "firm_name": firm.name,
        "firm_logo_url": logo,
        "firm_primary_color": firm.primary_color,
        "firm_whatsapp_number": firm.whatsapp_number,
        "client_name": client.client_name,
        "completion_pct": client.completion_pct,
        "checklist_items": [
            {
                "id": str(i.id),
                "category": i.category,
                "item_name": i.item_name,
                "description": i.description,
                "status": i.status.value,
                "is_required": i.is_required,
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
    db: Session = Depends(get_db),
):
    firm = db.query(Firm).filter(Firm.slug == firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Not found")
    client = db.query(Client).filter(Client.onboarding_token == token, Client.firm_id == firm.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Not found")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    mime = file.content_type or "application/octet-stream"
    try:
        meta = storage_service.upload_document(
            data, str(firm.id), str(client.id), file.filename or "upload.bin", mime
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    doc = Document(
        client_id=client.id,
        firm_id=firm.id,
        filename=meta["filename"],
        original_filename=meta["original_filename"],
        storage_path=meta["storage_path"],
        file_size=meta["file_size"],
        mime_type=mime,
        uploaded_by="client",
    )
    db.add(doc)
    db.flush()

    ai = classify_document(
        data, meta["original_filename"], mime, expected_type=None, country=client.country.value
    )
    doc.ai_document_type = ai.get("document_type")
    doc.ai_confidence = float(ai.get("confidence") or 0)
    doc.ai_verified = bool(ai.get("verified"))
    doc.ai_issues = ai.get("issues") or []

    matched = _match_item(db, client.id, doc.ai_document_type)
    if matched:
        matched.status = ChecklistItemStatus.uploaded
        matched.document_id = doc.id
        doc.checklist_item_id = matched.id
        db.add(matched)

    client.last_activity_at = datetime.utcnow()
    db.add(doc)
    recompute_client_completion(db, client)
    db.add(
        OnboardingActivity(
            client_id=client.id,
            firm_id=firm.id,
            action="client_upload",
            description=f"Uploaded {meta['original_filename']}",
            performed_by="client",
        )
    )
    if firm.whatsapp_number:
        log = WhatsAppLog(
            client_id=client.id,
            firm_id=firm.id,
            channel=MessageChannel.whatsapp,
            message_type="client_upload",
            phone_number=firm.whatsapp_number,
            message_content=f"Client {client.client_name} uploaded a document",
            status=MessageDeliveryStatus.sent,
        )
        db.add(log)
    db.commit()

    background_tasks.add_task(
        _notify_staff_after_upload,
        client.id,
        firm.id,
        doc.ai_document_type,
        doc.ai_confidence,
    )

    return {
        "document_type": doc.ai_document_type,
        "confidence": doc.ai_confidence,
        "verified": doc.ai_verified,
        "issues": doc.ai_issues,
        "matched_item": matched.item_name if matched else None,
    }
