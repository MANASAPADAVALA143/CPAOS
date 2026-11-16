from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr
from supabase import Client

from app.core.security import get_current_firm_user, get_supabase_admin
from app.db import get_db
from app.db import repo
from app.models.enums import FirmUserRole
from app.models.staff import FirmUser
from app.services import storage_service

router = APIRouter()


class FirmPatch(BaseModel):
    name: str | None = None
    whatsapp_number: str | None = None
    primary_color: str | None = None


class InviteUserBody(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "staff"


class UserPatch(BaseModel):
    role: str | None = None
    is_active: bool | None = None


@router.get("/firm")
def get_firm(current: FirmUser = Depends(get_current_firm_user), sb: Client = Depends(get_db)):
    firm = repo.firm_by_id(sb, current.firm_id)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    return {
        "id": str(firm["id"]),
        "name": firm["name"],
        "slug": firm["slug"],
        "country": firm["country"],
        "logo_url": firm.get("logo_url"),
        "primary_color": firm["primary_color"],
        "whatsapp_number": firm.get("whatsapp_number"),
        "plan": firm["plan"],
        "plan_client_limit": firm["plan_client_limit"],
    }


@router.patch("/firm")
def patch_firm(
    body: FirmPatch,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    patch: dict = {}
    if body.name is not None:
        patch["name"] = body.name
    if body.whatsapp_number is not None:
        patch["whatsapp_number"] = body.whatsapp_number
    if body.primary_color is not None:
        patch["primary_color"] = body.primary_color
    if patch:
        repo.update_firm(sb, current.firm_id, patch)
    firm = repo.firm_by_id(sb, current.firm_id)
    return {"ok": True, "firm": {"id": str(firm["id"]), "name": firm["name"]} if firm else {}}


@router.post("/firm/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    data = await file.read()
    mime = file.content_type or "image/png"
    try:
        url = storage_service.upload_logo(data, str(current.firm_id), mime)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    repo.update_firm(sb, current.firm_id, {"logo_url": url})
    return {"logo_url": url}


@router.get("/firm/users")
def list_users(current: FirmUser = Depends(get_current_firm_user), sb: Client = Depends(get_db)):
    users = repo.firm_users_for_firm(sb, current.firm_id)
    return [
        {
            "id": str(u["id"]),
            "email": u["email"],
            "full_name": u["full_name"],
            "role": u["role"],
            "is_active": u.get("is_active", True),
        }
        for u in users
    ]


@router.post("/firm/invite-user")
def invite_user(
    body: InviteUserBody,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    if current.role not in (FirmUserRole.owner, FirmUserRole.admin):
        raise HTTPException(status_code=403, detail="Not allowed")
    supabase = get_supabase_admin()
    try:
        created = supabase.auth.admin.create_user(
            {"email": str(body.email), "password": body.password, "email_confirm": True}
        )
        uid = created.user.id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    role = FirmUserRole.staff.value
    if body.role == "admin" and current.role == FirmUserRole.owner:
        role = FirmUserRole.admin.value
    u_r = (
        sb.table("firm_users")
        .insert(
            {
                "firm_id": str(current.firm_id),
                "supabase_user_id": str(uid),
                "email": str(body.email),
                "full_name": body.full_name,
                "role": role,
            }
        )
        .execute()
    )
    if not u_r.data:
        raise HTTPException(status_code=500, detail="Failed to invite user")
    u = u_r.data[0]
    return {"id": str(u["id"]), "email": u["email"]}


@router.patch("/firm/users/{user_id}")
def patch_user(
    user_id: uuid.UUID,
    body: UserPatch,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    if current.role not in (FirmUserRole.owner, FirmUserRole.admin):
        raise HTTPException(status_code=403, detail="Not allowed")
    u = sb.table("firm_users").select("*").eq("id", str(user_id)).eq("firm_id", str(current.firm_id)).limit(1).execute()
    if not u.data:
        raise HTTPException(status_code=404, detail="User not found")
    patch: dict = {}
    if body.role is not None:
        try:
            FirmUserRole(body.role)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid role") from e
        patch["role"] = body.role
    if body.is_active is not None:
        patch["is_active"] = body.is_active
    if patch:
        repo.update_firm_user(sb, user_id, patch)
    return {"ok": True}
