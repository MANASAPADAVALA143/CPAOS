from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.models.onboarding import FirmUser

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


def get_current_firm_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> FirmUser:
    token = credentials.credentials
    supabase_admin = get_supabase_admin()
    try:
        user_response = supabase_admin.auth.get_user(token)
        supabase_user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    firm_user = (
        db.query(FirmUser)
        .filter(FirmUser.supabase_user_id == supabase_user_id, FirmUser.is_active.is_(True))
        .first()
    )
    if not firm_user:
        raise HTTPException(status_code=403, detail="User not registered to any firm")
    return firm_user
