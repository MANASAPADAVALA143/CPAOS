from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from supabase import Client

from app.core.security import get_current_firm_user, get_supabase_admin
from app.db import get_db
from app.db import repo
from app.models.enums import FirmUserRole, Plan
from app.models.staff import FirmUser

router = APIRouter()

PLAN_LIMITS = {"starter": 10, "pro": 50, "agency": 999999}


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
def register_firm(body: RegisterFirmBody, sb: Client = Depends(get_db)):
    supabase = get_supabase_admin()
    slug = body.slug or _slugify(body.firm_name)
    if repo.firm_by_slug(sb, slug):
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
    plan_str = chosen.value
    limit = PLAN_LIMITS.get(plan_str, 10)

    fr = (
        sb.table("firms")
        .insert(
            {
                "name": body.firm_name,
                "slug": slug,
                "country": body.country,
                "plan": plan_str,
                "plan_client_limit": limit,
                "whatsapp_number": body.whatsapp_number,
            }
        )
        .execute()
    )
    if not fr.data:
        raise HTTPException(status_code=500, detail="Failed to create firm")
    firm = fr.data[0]
    firm_id = uuid.UUID(str(firm["id"]))

    fu_r = (
        sb.table("firm_users")
        .insert(
            {
                "firm_id": str(firm_id),
                "supabase_user_id": str(owner_id),
                "email": str(body.owner_email),
                "full_name": body.owner_name,
                "role": FirmUserRole.owner.value,
            }
        )
        .execute()
    )
    if not fu_r.data:
        raise HTTPException(status_code=500, detail="Failed to create firm user")
    fu = fu_r.data[0]

    try:
        sess = supabase.auth.sign_in_with_password(
            {"email": str(body.owner_email), "password": body.password}
        )
        access_token = sess.session.access_token if sess.session else None
    except Exception:
        access_token = None

    return {
        "firm": {"id": str(firm["id"]), "name": firm["name"], "slug": firm["slug"]},
        "user": {"id": str(fu["id"]), "email": fu["email"], "role": fu["role"]},
        "access_token": access_token,
        "firm_slug": firm["slug"],
    }


@router.post("/login")
def login(body: LoginBody, sb: Client = Depends(get_db)):
    supabase = get_supabase_admin()
    try:
        user_response = supabase.auth.get_user(body.access_token)
        uid = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    fu = repo.firm_user_by_supabase_id(sb, str(uid))
    if not fu:
        raise HTTPException(status_code=403, detail="User not registered to any firm")
    firm = repo.firm_by_id(sb, uuid.UUID(str(fu["firm_id"])))
    if not firm:
        raise HTTPException(status_code=403, detail="Firm missing")
    return {
        "firm_id": str(firm["id"]),
        "firm_name": firm["name"],
        "slug": firm["slug"],
        "plan": firm["plan"],
        "user_role": fu["role"],
    }


@router.get("/me")
def me(current: FirmUser = Depends(get_current_firm_user), sb: Client = Depends(get_db)):
    firm = repo.firm_by_id(sb, current.firm_id)
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    return {
        "user": {
            "id": str(current.id),
            "email": current.email,
            "full_name": current.full_name,
            "role": current.role.value,
        },
        "firm": {
            "id": str(firm["id"]),
            "name": firm["name"],
            "slug": firm["slug"],
            "country": firm["country"],
            "plan": firm["plan"],
            "primary_color": firm["primary_color"],
            "logo_url": firm.get("logo_url"),
        },
    }
