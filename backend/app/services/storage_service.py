"""Supabase Storage — upload, signed URLs, delete, logo."""

from __future__ import annotations

import os
import uuid

from typing import Any

from app.core.config import get_settings

_client: Any = None


def _get_client() -> Any:
    global _client
    if _client is None:
        from supabase import create_client

        s = get_settings()
        if not s.supabase_url or not s.supabase_service_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required for storage")
        _client = create_client(s.supabase_url, s.supabase_service_key)
    return _client


def bucket() -> str:
    return get_settings().supabase_storage_bucket


def upload_document(
    file_bytes: bytes,
    firm_id: str,
    client_id: str,
    original_filename: str,
    mime_type: str,
) -> dict:
    supabase = _get_client()
    b = bucket()
    unique_name = f"{uuid.uuid4().hex}_{original_filename}"
    storage_path = f"{firm_id}/{client_id}/{unique_name}"
    supabase.storage.from_(b).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": mime_type},
    )
    return {
        "storage_path": storage_path,
        "file_size": len(file_bytes),
        "filename": unique_name,
        "original_filename": original_filename,
    }


def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    supabase = _get_client()
    result = supabase.storage.from_(bucket()).create_signed_url(path=storage_path, expires_in=expires_in)
    data = result.get("signedURL") or result.get("signedUrl")
    if not data:
        raise KeyError(f"Unexpected signed URL response: {result}")
    return data


def delete_document(storage_path: str) -> bool:
    supabase = _get_client()
    supabase.storage.from_(bucket()).remove([storage_path])
    return True


def upload_logo(file_bytes: bytes, firm_id: str, mime_type: str) -> str:
    supabase = _get_client()
    ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
    storage_path = f"logos/{firm_id}/logo.{ext}"
    supabase.storage.from_(bucket()).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": mime_type, "upsert": "true"},
    )
    return get_signed_url(storage_path, expires_in=86400 * 365)
