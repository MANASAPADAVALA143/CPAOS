from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.models.enums import FirmUserRole


@dataclass
class FirmUser:
    """Authenticated staff row (from firm_users via Supabase)."""

    id: uuid.UUID
    firm_id: uuid.UUID
    supabase_user_id: str
    email: str
    full_name: str
    role: FirmUserRole
    is_active: bool
