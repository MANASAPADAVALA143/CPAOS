from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_firm_user
from app.db import get_db
from app.models.onboarding import ChecklistItem, ChecklistItemStatus, Client, FirmUser, OnboardingActivity
from app.services.completion import recompute_client_completion
from app.services.completion_service import maybe_complete_client

router = APIRouter()


class WaiveBody(BaseModel):
    reason: str


@router.patch("/clients/{client_id}/checklist-items/{item_id}")
def waive_item(
    client_id: uuid.UUID,
    item_id: uuid.UUID,
    body: WaiveBody,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    c = db.query(Client).filter(Client.id == client_id, Client.firm_id == current.firm_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id, ChecklistItem.client_id == c.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ChecklistItemStatus.waived
    item.waived_reason = body.reason
    item.waived_by = current.id
    db.add(item)
    db.add(
        OnboardingActivity(
            client_id=c.id,
            firm_id=current.firm_id,
            action="checklist_waived",
            description=f"Waived: {item.item_name}",
            performed_by=str(current.id),
        )
    )
    recompute_client_completion(db, c)
    maybe_complete_client(db, c)
    db.commit()
    return {"ok": True}


class PatchChecklistItemBody(BaseModel):
    status: str


@router.patch("/checklist/{item_id}")
def patch_checklist_item(
    item_id: uuid.UUID,
    body: PatchChecklistItemBody,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(ChecklistItem)
        .join(Client, Client.id == ChecklistItem.client_id)
        .filter(ChecklistItem.id == item_id, Client.firm_id == current.firm_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if body.status == "verified":
        item.status = ChecklistItemStatus.verified
    elif body.status == "pending":
        item.status = ChecklistItemStatus.pending
    else:
        raise HTTPException(status_code=400, detail="Unsupported status")
    db.add(item)
    c = db.query(Client).filter(Client.id == item.client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    db.add(
        OnboardingActivity(
            client_id=c.id,
            firm_id=current.firm_id,
            action="checklist_item_updated",
            description=f"Item {item.item_name} set to {body.status}",
            performed_by=str(current.id),
        )
    )
    recompute_client_completion(db, c)
    maybe_complete_client(db, c)
    db.commit()
    return {"ok": True}
