from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.db import get_db
from app.db import repo
from app.models.enums import FirmUserRole
from app.models.staff import FirmUser

bearer = HTTPBearer()

_supabase_admin: Any = None


def get_supabase_admin() -> Any:
    global _supabase_admin
    s = get_settings()
    if not s.supabase_url or not s.supabase_service_key:
        raise HTTPException(status_code=503, detail="Supabase is not configured")
    if _supabase_admin is None:
        from supabase import create_client

        _supabase_admin = create_client(s.supabase_url, s.supabase_service_key)
    return _supabase_admin


def _row_to_firm_user(row: dict) -> FirmUser:
    return FirmUser(
        id=uuid.UUID(str(row["id"])),
        firm_id=uuid.UUID(str(row["firm_id"])),
        supabase_user_id=str(row["supabase_user_id"]),
        email=str(row["email"]),
        full_name=str(row["full_name"]),
        role=FirmUserRole(row["role"]),
        is_active=bool(row.get("is_active", True)),
    )


def get_current_firm_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    sb=Depends(get_db),
) -> FirmUser:
    token = credentials.credentials
    supabase_admin = get_supabase_admin()
    try:
        user_response = supabase_admin.auth.get_user(token)
        supabase_user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    row = repo.firm_user_by_supabase_id(sb, str(supabase_user_id))
    if not row:
        raise HTTPException(status_code=403, detail="User not registered to any firm")
    return _row_to_firm_user(row)
