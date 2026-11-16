from __future__ import annotations

import os
from typing import Iterator

from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import Client, create_client

load_dotenv()

_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    if not url or not key:
        raise HTTPException(status_code=503, detail="Supabase is not configured (SUPABASE_URL / SUPABASE_SERVICE_KEY)")
    if _supabase is None:
        _supabase = create_client(url, key)
    return _supabase


def get_db() -> Iterator[Client]:
    """FastAPI dependency — yields Supabase client (same as get_supabase)."""
    yield get_supabase()


def init_db() -> None:
    """Schema is applied via Supabase SQL Editor (supabase_schema.sql); no local DDL."""
    return None
