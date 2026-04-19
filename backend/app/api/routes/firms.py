from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import get_current_firm_user, get_supabase_admin
from app.db import get_db
from app.models.onboarding import Firm, FirmUser, FirmUserRole
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
def get_firm(current: FirmUser = Depends(get_current_firm_user), db: Session = Depends(get_db)):
    firm = db.query(Firm).filter(Firm.id == current.firm_id).first()
    return {
        "id": str(firm.id),
        "name": firm.name,
        "slug": firm.slug,
        "country": firm.country,
        "logo_url": firm.logo_url,
        "primary_color": firm.primary_color,
        "whatsapp_number": firm.whatsapp_number,
        "plan": firm.plan.value,
        "plan_client_limit": firm.plan_client_limit,
    }


@router.patch("/firm")
def patch_firm(
    body: FirmPatch,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    firm = db.query(Firm).filter(Firm.id == current.firm_id).first()
    if body.name is not None:
        firm.name = body.name
    if body.whatsapp_number is not None:
        firm.whatsapp_number = body.whatsapp_number
    if body.primary_color is not None:
        firm.primary_color = body.primary_color
    db.add(firm)
    db.commit()
    db.refresh(firm)
    return {"ok": True, "firm": {"id": str(firm.id), "name": firm.name}}


@router.post("/firm/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    data = await file.read()
    mime = file.content_type or "image/png"
    try:
        url = storage_service.upload_logo(data, str(current.firm_id), mime)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    firm = db.query(Firm).filter(Firm.id == current.firm_id).first()
    firm.logo_url = url
    db.add(firm)
    db.commit()
    return {"logo_url": url}


@router.get("/firm/users")
def list_users(current: FirmUser = Depends(get_current_firm_user), db: Session = Depends(get_db)):
    users = db.query(FirmUser).filter(FirmUser.firm_id == current.firm_id).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
        }
        for u in users
    ]


@router.post("/firm/invite-user")
def invite_user(
    body: InviteUserBody,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
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
    role = FirmUserRole.staff
    if body.role == "admin" and current.role == FirmUserRole.owner:
        role = FirmUserRole.admin
    u = FirmUser(
        firm_id=current.firm_id,
        supabase_user_id=str(uid),
        email=str(body.email),
        full_name=body.full_name,
        role=role,
    )
    db.add(u)
    db.commit()
    return {"id": str(u.id), "email": u.email}


@router.patch("/firm/users/{user_id}")
def patch_user(
    user_id: uuid.UUID,
    body: UserPatch,
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    if current.role not in (FirmUserRole.owner, FirmUserRole.admin):
        raise HTTPException(status_code=403, detail="Not allowed")
    u = db.query(FirmUser).filter(FirmUser.id == user_id, FirmUser.firm_id == current.firm_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role is not None:
        try:
            u.role = FirmUserRole(body.role)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid role") from e
    if body.is_active is not None:
        u.is_active = body.is_active
    db.add(u)
    db.commit()
    return {"ok": True}
