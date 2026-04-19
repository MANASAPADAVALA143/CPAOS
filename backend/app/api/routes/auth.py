from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_firm_user, get_supabase_admin
from app.db import get_db
from app.models.onboarding import Firm, FirmUser, FirmUserRole, Plan

router = APIRouter()


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "firm"


class RegisterFirmBody(BaseModel):
    firm_name: str
    slug: str | None = None
    country: str = "India"
    whatsapp_number: str | None = None
    plan: str | None = Field(default="starter", description="starter | professional | agency")
    owner_email: EmailStr
    owner_name: str
    password: str = Field(min_length=8)


class LoginBody(BaseModel):
    access_token: str


@router.post("/register-firm")
def register_firm(body: RegisterFirmBody, db: Session = Depends(get_db)):
    supabase = get_supabase_admin()
    slug = body.slug or _slugify(body.firm_name)
    if db.query(Firm).filter(Firm.slug == slug).first():
        raise HTTPException(status_code=400, detail="Slug already taken")

    try:
        created = supabase.auth.admin.create_user(
            {"email": str(body.owner_email), "password": body.password, "email_confirm": True}
        )
        owner_id = created.user.id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Supabase user error: {e}") from e

    plan_map = {"starter": Plan.starter, "professional": Plan.pro, "pro": Plan.pro, "agency": Plan.agency}
    chosen = plan_map.get((body.plan or "starter").lower(), Plan.starter)
    firm = Firm(
        name=body.firm_name,
        slug=slug,
        country=body.country,
        plan=chosen,
        whatsapp_number=body.whatsapp_number,
    )
    db.add(firm)
    db.flush()

    fu = FirmUser(
        firm_id=firm.id,
        supabase_user_id=str(owner_id),
        email=str(body.owner_email),
        full_name=body.owner_name,
        role=FirmUserRole.owner,
    )
    db.add(fu)
    db.commit()
    db.refresh(firm)
    db.refresh(fu)

    try:
        sess = supabase.auth.sign_in_with_password(
            {"email": str(body.owner_email), "password": body.password}
        )
        access_token = sess.session.access_token if sess.session else None
    except Exception:
        access_token = None

    return {
        "firm": {"id": str(firm.id), "name": firm.name, "slug": firm.slug},
        "user": {"id": str(fu.id), "email": fu.email, "role": fu.role.value},
        "access_token": access_token,
    }


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    supabase = get_supabase_admin()
    try:
        user_response = supabase.auth.get_user(body.access_token)
        uid = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    fu = db.query(FirmUser).filter(FirmUser.supabase_user_id == str(uid), FirmUser.is_active.is_(True)).first()
    if not fu:
        raise HTTPException(status_code=403, detail="User not registered to any firm")
    firm = db.query(Firm).filter(Firm.id == fu.firm_id).first()
    return {
        "firm_id": str(firm.id),
        "firm_name": firm.name,
        "slug": firm.slug,
        "plan": firm.plan.value,
        "user_role": fu.role.value,
    }


@router.get("/me")
def me(current: FirmUser = Depends(get_current_firm_user), db: Session = Depends(get_db)):
    firm = db.query(Firm).filter(Firm.id == current.firm_id).first()
    return {
        "user": {
            "id": str(current.id),
            "email": current.email,
            "full_name": current.full_name,
            "role": current.role.value,
        },
        "firm": {
            "id": str(firm.id),
            "name": firm.name,
            "slug": firm.slug,
            "country": firm.country,
            "plan": firm.plan.value,
            "primary_color": firm.primary_color,
            "logo_url": firm.logo_url,
        },
    }
