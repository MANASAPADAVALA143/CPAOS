from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db
from app.db import repo
from app.models.staff import FirmUser
from app.services.signature_service import check_signature_status, handle_docusign_webhook

router = APIRouter()


@router.get("/clients/{client_id}/signature-status")
def signature_status(
    client_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    c = repo.client_by_id(sb, client_id, current.firm_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    env = c.get("signature_envelope_id")
    return {"envelope_id": env, "status": check_signature_status(env or "")}


@router.post("/webhook")
async def webhook(request: Request, sb: Client = Depends(get_db)):
    payload = await request.json()
    handle_docusign_webhook(payload, sb)
    return {"ok": True}
