from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_firm_user
from app.db import get_db
from app.models.onboarding import (
    ChecklistItem,
    ChecklistItemStatus,
    Client,
    Document,
    DocumentReviewStatus,
    FirmUser,
    OnboardingActivity,
)
from app.services import storage_service
from app.services.completion import recompute_client_completion
from app.services.completion_service import maybe_complete_client
from app.services.document_classifier import classify_document

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024


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


@router.post("/clients/{client_id}/upload")
async def staff_upload(
    client_id: uuid.UUID,
    file: UploadFile = File(...),
    expected_type: str | None = Form(None),
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    c = db.query(Client).filter(Client.id == client_id, Client.firm_id == current.firm_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    mime = file.content_type or "application/octet-stream"
    try:
        meta = storage_service.upload_document(
            data, str(current.firm_id), str(c.id), file.filename or "upload.bin", mime
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    doc = Document(
        client_id=c.id,
        firm_id=current.firm_id,
        filename=meta["filename"],
        original_filename=meta["original_filename"],
        storage_path=meta["storage_path"],
        file_size=meta["file_size"],
        mime_type=mime,
        uploaded_by=str(current.id),
    )
    db.add(doc)
    db.flush()

    ai = classify_document(data, meta["original_filename"], mime, expected_type=expected_type, country=c.country.value)
    doc.ai_document_type = ai.get("document_type")
    doc.ai_confidence = float(ai.get("confidence") or 0)
    doc.ai_verified = bool(ai.get("verified"))
    doc.ai_issues = ai.get("issues") or []

    item = None
    if doc.ai_confidence > 0.8 and doc.ai_verified:
        item = _match_item(db, c.id, doc.ai_document_type)
        if item:
            item.status = ChecklistItemStatus.uploaded
            item.document_id = doc.id
            doc.checklist_item_id = item.id
    db.add(doc)
    recompute_client_completion(db, c)
    db.commit()
    db.refresh(doc)
    return {
        "document": {
            "id": str(doc.id),
            "filename": doc.filename,
            "review_status": doc.review_status.value,
            "ai_document_type": doc.ai_document_type,
            "ai_confidence": doc.ai_confidence,
        },
        "classification": ai,
        "matched_item_id": str(item.id) if item else None,
    }


@router.get("/clients/{client_id}/documents")
def list_documents(
    client_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    c = db.query(Client).filter(Client.id == client_id, Client.firm_id == current.firm_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    docs = db.query(Document).filter(Document.client_id == c.id, Document.firm_id == current.firm_id).all()
    out = []
    for d in docs:
        try:
            signed = storage_service.get_signed_url(d.storage_path, 3600)
        except Exception:
            signed = None
        out.append(
            {
                "id": str(d.id),
                "filename": d.filename,
                "original_filename": d.original_filename,
                "uploaded_at": d.uploaded_at.isoformat(),
                "ai_document_type": d.ai_document_type,
                "ai_confidence": d.ai_confidence,
                "review_status": d.review_status.value,
                "signed_url": signed,
            }
        )
    return out


@router.get("/documents/{doc_id}/signed-url")
def signed_url(
    doc_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    d = db.query(Document).filter(Document.id == doc_id, Document.firm_id == current.firm_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        url = storage_service.get_signed_url(d.storage_path, 3600)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return {"signed_url": url}


class VerifyBody(BaseModel):
    action: str
    rejection_reason: str | None = None


@router.post("/documents/{doc_id}/verify")
def verify_doc(
    doc_id: uuid.UUID,
    body: VerifyBody,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    d = db.query(Document).filter(Document.id == doc_id, Document.firm_id == current.firm_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Not found")
    c = db.query(Client).filter(Client.id == d.client_id).first()
    if body.action == "approved":
        d.review_status = DocumentReviewStatus.approved
        if d.checklist_item_id:
            item = db.query(ChecklistItem).filter(ChecklistItem.id == d.checklist_item_id).first()
            if item:
                item.status = ChecklistItemStatus.verified
                item.document_id = d.id
    elif body.action == "rejected":
        d.review_status = DocumentReviewStatus.rejected
        d.rejection_reason = body.rejection_reason
        if d.checklist_item_id:
            item = db.query(ChecklistItem).filter(ChecklistItem.id == d.checklist_item_id).first()
            if item:
                item.status = ChecklistItemStatus.rejected
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    d.reviewed_by = current.id
    d.reviewed_at = datetime.utcnow()
    db.add(d)
    recompute_client_completion(db, c)
    maybe_complete_client(db, c)
    db.commit()
    return {"ok": True}
