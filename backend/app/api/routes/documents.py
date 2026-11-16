from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db
from app.db import repo
from app.models.enums import DocumentReviewStatus
from app.models.staff import FirmUser
from app.services import storage_service
from app.services.completion import recompute_client_completion
from app.services.completion_service import maybe_complete_client
from app.services.document_classifier import classify_document

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024


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


@router.post("/clients/{client_id}/upload")
async def staff_upload(
    client_id: uuid.UUID,
    file: UploadFile = File(...),
    expected_type: str | None = Form(None),
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    c = repo.client_by_id(sb, client_id, current.firm_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    mime = file.content_type or "application/octet-stream"
    try:
        meta = storage_service.upload_document(
            data, str(current.firm_id), str(c["id"]), file.filename or "upload.bin", mime
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    ins = (
        sb.table("documents")
        .insert(
            {
                "client_id": str(c["id"]),
                "firm_id": str(current.firm_id),
                "filename": meta["filename"],
                "original_filename": meta["original_filename"],
                "storage_path": meta["storage_path"],
                "file_size": meta["file_size"],
                "mime_type": mime,
                "uploaded_by": str(current.id),
            }
        )
        .execute()
    )
    if not ins.data:
        raise HTTPException(status_code=500, detail="Document insert failed")
    doc = ins.data[0]
    doc_id = uuid.UUID(str(doc["id"]))

    ai = classify_document(
        data, meta["original_filename"], mime, expected_type=expected_type, country=c["country"]
    )
    patch_doc = {
        "ai_document_type": ai.get("document_type"),
        "ai_confidence": float(ai.get("confidence") or 0),
        "ai_verified": bool(ai.get("verified")),
        "ai_issues": ai.get("issues") or [],
    }
    item = None
    conf = float(patch_doc["ai_confidence"] or 0)
    if conf > 0.8 and patch_doc["ai_verified"]:
        item = _match_item(sb, client_id, patch_doc.get("ai_document_type"))
        if item:
            iid = uuid.UUID(str(item["id"]))
            patch_doc["checklist_item_id"] = str(iid)
            repo.update_checklist_item(
                sb,
                iid,
                {"status": "uploaded", "document_id": str(doc_id)},
            )
    repo.update_document(sb, doc_id, patch_doc)

    recompute_client_completion(sb, client_id)
    doc2 = repo.document_by_id(sb, doc_id, current.firm_id) or doc
    return {
        "document": {
            "id": str(doc2["id"]),
            "filename": doc2["filename"],
            "review_status": doc2.get("review_status", "pending"),
            "ai_document_type": doc2.get("ai_document_type"),
            "ai_confidence": doc2.get("ai_confidence"),
        },
        "classification": ai,
        "matched_item_id": str(item["id"]) if item else None,
    }


@router.get("/clients/{client_id}/documents")
def list_documents(
    client_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    c = repo.client_by_id(sb, client_id, current.firm_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    docs = repo.documents_for_client(sb, client_id, current.firm_id)
    out = []
    for d in docs:
        try:
            signed = storage_service.get_signed_url(d["storage_path"], 3600)
        except Exception:
            signed = None
        out.append(
            {
                "id": str(d["id"]),
                "filename": d["filename"],
                "original_filename": d["original_filename"],
                "uploaded_at": d.get("uploaded_at"),
                "ai_document_type": d.get("ai_document_type"),
                "ai_confidence": d.get("ai_confidence"),
                "review_status": d.get("review_status", "pending"),
                "signed_url": signed,
            }
        )
    return out


@router.get("/documents/{doc_id}/signed-url")
def signed_url(
    doc_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    d = repo.document_by_id(sb, doc_id, current.firm_id)
    if not d:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        url = storage_service.get_signed_url(d["storage_path"], 3600)
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
    sb: Client = Depends(get_db),
):
    d = repo.document_by_id(sb, doc_id, current.firm_id)
    if not d:
        raise HTTPException(status_code=404, detail="Not found")
    cid = uuid.UUID(str(d["client_id"]))
    c = repo.client_by_id(sb, cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    now = datetime.now(timezone.utc).isoformat()
    if body.action == "approved":
        d_patch = {"review_status": DocumentReviewStatus.approved.value, "reviewed_by": str(current.id), "reviewed_at": now}
        if d.get("checklist_item_id"):
            iid = uuid.UUID(str(d["checklist_item_id"]))
            repo.update_checklist_item(
                sb,
                iid,
                {"status": "verified", "document_id": str(doc_id)},
            )
    elif body.action == "rejected":
        d_patch = {
            "review_status": DocumentReviewStatus.rejected.value,
            "rejection_reason": body.rejection_reason,
            "reviewed_by": str(current.id),
            "reviewed_at": now,
        }
        if d.get("checklist_item_id"):
            iid = uuid.UUID(str(d["checklist_item_id"]))
            repo.update_checklist_item(sb, iid, {"status": "rejected"})
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    repo.update_document(sb, doc_id, d_patch)
    recompute_client_completion(sb, cid)
    maybe_complete_client(sb, cid)
    return {"ok": True}
