from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db
from app.db import repo
from app.models.staff import FirmUser
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
    sb: Client = Depends(get_db),
):
    c = repo.client_by_id(sb, client_id, current.firm_id)
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    item = repo.checklist_item_by_id(sb, item_id, client_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    repo.update_checklist_item(
        sb,
        item_id,
        {"status": "waived", "waived_reason": body.reason, "waived_by": str(current.id)},
    )
    repo.insert_activity(
        sb,
        client_id=client_id,
        firm_id=current.firm_id,
        action="checklist_waived",
        description=f"Waived: {item['item_name']}",
        performed_by=str(current.id),
    )
    recompute_client_completion(sb, client_id)
    maybe_complete_client(sb, client_id)
    return {"ok": True}


class PatchChecklistItemBody(BaseModel):
    status: str


@router.patch("/checklist/{item_id}")
def patch_checklist_item(
    item_id: uuid.UUID,
    body: PatchChecklistItemBody,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    item = repo.checklist_item_by_id(sb, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    cid = uuid.UUID(str(item["client_id"]))
    c = repo.client_by_id(sb, cid, current.firm_id)
    if not c:
        raise HTTPException(status_code=404, detail="Item not found")
    if body.status == "verified":
        new_st = "verified"
    elif body.status == "pending":
        new_st = "pending"
    else:
        raise HTTPException(status_code=400, detail="Unsupported status")
    repo.update_checklist_item(sb, item_id, {"status": new_st})
    repo.insert_activity(
        sb,
        client_id=cid,
        firm_id=current.firm_id,
        action="checklist_item_updated",
        description=f"Item {item['item_name']} set to {body.status}",
        performed_by=str(current.id),
    )
    recompute_client_completion(sb, cid)
    maybe_complete_client(sb, cid)
    return {"ok": True}
