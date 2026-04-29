from __future__ import annotations

import re
import uuid
from typing import Any

from supabase import Client

from app.db.dates import utc_now_iso


def norm_email(s: str) -> str:
    return (s or "").strip().lower()


def digits_only(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


def firm_by_slug(sb: Client, slug: str) -> dict[str, Any] | None:
    r = sb.table("firms").select("*").eq("slug", slug).limit(1).execute()
    return r.data[0] if r.data else None


def firm_by_id(sb: Client, firm_id: uuid.UUID) -> dict[str, Any] | None:
    r = sb.table("firms").select("*").eq("id", str(firm_id)).limit(1).execute()
    return r.data[0] if r.data else None


def firm_user_by_supabase_id(sb: Client, supabase_user_id: str) -> dict[str, Any] | None:
    r = (
        sb.table("firm_users")
        .select("*")
        .eq("supabase_user_id", supabase_user_id)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def firm_user_by_id(sb: Client, user_id: uuid.UUID) -> dict[str, Any] | None:
    r = sb.table("firm_users").select("*").eq("id", str(user_id)).limit(1).execute()
    return r.data[0] if r.data else None


def firm_users_for_firm(sb: Client, firm_id: uuid.UUID) -> list[dict[str, Any]]:
    r = sb.table("firm_users").select("*").eq("firm_id", str(firm_id)).execute()
    return r.data or []


def client_by_id(sb: Client, client_id: uuid.UUID, firm_id: uuid.UUID | None = None) -> dict[str, Any] | None:
    q = sb.table("clients").select("*").eq("id", str(client_id))
    if firm_id is not None:
        q = q.eq("firm_id", str(firm_id))
    r = q.limit(1).execute()
    return r.data[0] if r.data else None


def client_by_token(sb: Client, firm_id: uuid.UUID, token: uuid.UUID) -> dict[str, Any] | None:
    r = (
        sb.table("clients")
        .select("*")
        .eq("firm_id", str(firm_id))
        .eq("onboarding_token", str(token))
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def clients_for_firm_email(sb: Client, firm_id: uuid.UUID, email: str) -> dict[str, Any] | None:
    em = norm_email(email)
    r = sb.table("clients").select("*").eq("firm_id", str(firm_id)).eq("email", em).limit(1).execute()
    return r.data[0] if r.data else None


def count_clients_firm(sb: Client, firm_id: uuid.UUID) -> int:
    r = sb.table("clients").select("id", count="exact").eq("firm_id", str(firm_id)).execute()
    return int(r.count or 0)


def list_clients_filtered(
    sb: Client,
    firm_id: uuid.UUID,
    *,
    status: str | None = None,
    country: str | None = None,
    search: str | None = None,
    assigned_to: uuid.UUID | None = None,
) -> list[dict[str, Any]]:
    q = sb.table("clients").select("*").eq("firm_id", str(firm_id))
    if status:
        q = q.eq("status", status)
    if country:
        q = q.eq("country", country)
    if search:
        q = q.ilike("client_name", f"%{search}%")
    if assigned_to is not None:
        q = q.eq("assigned_to", str(assigned_to))
    r = q.order("created_at", desc=True).execute()
    return r.data or []


def checklist_items_for_client(sb: Client, client_id: uuid.UUID) -> list[dict[str, Any]]:
    r = (
        sb.table("checklist_items")
        .select("*")
        .eq("client_id", str(client_id))
        .order("display_order")
        .execute()
    )
    return r.data or []


def checklist_pending_for_client(sb: Client, client_id: uuid.UUID) -> list[dict[str, Any]]:
    r = (
        sb.table("checklist_items")
        .select("*")
        .eq("client_id", str(client_id))
        .eq("status", "pending")
        .order("display_order")
        .execute()
    )
    return r.data or []


def checklist_uploaded_count(sb: Client, client_id: uuid.UUID) -> int:
    r = (
        sb.table("checklist_items")
        .select("id", count="exact")
        .eq("client_id", str(client_id))
        .eq("status", "uploaded")
        .execute()
    )
    return int(r.count or 0)


def checklist_item_by_id(sb: Client, item_id: uuid.UUID, client_id: uuid.UUID | None = None) -> dict[str, Any] | None:
    q = sb.table("checklist_items").select("*").eq("id", str(item_id))
    if client_id is not None:
        q = q.eq("client_id", str(client_id))
    r = q.limit(1).execute()
    return r.data[0] if r.data else None


def insert_activity(
    sb: Client,
    *,
    client_id: uuid.UUID,
    firm_id: uuid.UUID,
    action: str,
    description: str,
    performed_by: str,
) -> dict[str, Any] | None:
    payload = {
        "client_id": str(client_id),
        "firm_id": str(firm_id),
        "action": action,
        "description": description,
        "performed_by": performed_by,
    }
    r = sb.table("onboarding_activity").insert(payload).execute()
    return r.data[0] if r.data else None


def insert_whatsapp_log(
    sb: Client,
    *,
    client_id: uuid.UUID,
    firm_id: uuid.UUID,
    channel: str,
    message_type: str,
    phone_number: str,
    message_content: str,
    status: str,
) -> None:
    sb.table("whatsapp_logs").insert(
        {
            "client_id": str(client_id),
            "firm_id": str(firm_id),
            "channel": channel,
            "message_type": message_type,
            "phone_number": phone_number,
            "message_content": message_content,
            "status": status,
        }
    ).execute()


def clients_in_ids(sb: Client, firm_id: uuid.UUID, ids: list[uuid.UUID]) -> list[dict[str, Any]]:
    if not ids:
        return []
    sid = [str(i) for i in ids]
    r = sb.table("clients").select("*").eq("firm_id", str(firm_id)).in_("id", sid).execute()
    return r.data or []


def list_onboarding_activity(sb: Client, firm_id: uuid.UUID, limit: int = 20) -> list[dict[str, Any]]:
    r = (
        sb.table("onboarding_activity")
        .select("*")
        .eq("firm_id", str(firm_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []


def documents_for_client(sb: Client, client_id: uuid.UUID, firm_id: uuid.UUID) -> list[dict[str, Any]]:
    r = (
        sb.table("documents")
        .select("*")
        .eq("client_id", str(client_id))
        .eq("firm_id", str(firm_id))
        .execute()
    )
    return r.data or []


def document_by_id(sb: Client, doc_id: uuid.UUID, firm_id: uuid.UUID) -> dict[str, Any] | None:
    r = (
        sb.table("documents")
        .select("*")
        .eq("id", str(doc_id))
        .eq("firm_id", str(firm_id))
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def whatsapp_logs_for_client(sb: Client, client_id: uuid.UUID) -> list[dict[str, Any]]:
    r = (
        sb.table("whatsapp_logs")
        .select("*")
        .eq("client_id", str(client_id))
        .order("sent_at", desc=True)
        .execute()
    )
    return r.data or []


def update_client(sb: Client, client_id: uuid.UUID, patch: dict[str, Any]) -> None:
    sb.table("clients").update(patch).eq("id", str(client_id)).execute()


def update_checklist_item(sb: Client, item_id: uuid.UUID, patch: dict[str, Any]) -> None:
    sb.table("checklist_items").update(patch).eq("id", str(item_id)).execute()


def update_document(sb: Client, doc_id: uuid.UUID, patch: dict[str, Any]) -> None:
    sb.table("documents").update(patch).eq("id", str(doc_id)).execute()


def update_firm(sb: Client, firm_id: uuid.UUID, patch: dict[str, Any]) -> None:
    sb.table("firms").update(patch).eq("id", str(firm_id)).execute()


def update_firm_user(sb: Client, user_id: uuid.UUID, patch: dict[str, Any]) -> None:
    sb.table("firm_users").update(patch).eq("id", str(user_id)).execute()


def owner_user_for_firm(sb: Client, firm_id: uuid.UUID) -> dict[str, Any] | None:
    r = (
        sb.table("firm_users")
        .select("*")
        .eq("firm_id", str(firm_id))
        .eq("role", "owner")
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def client_by_envelope(sb: Client, envelope_id: str) -> dict[str, Any] | None:
    r = sb.table("clients").select("*").eq("signature_envelope_id", envelope_id).limit(1).execute()
    return r.data[0] if r.data else None


def list_clients_for_reminders(sb: Client) -> list[dict[str, Any]]:
    r = sb.table("clients").select("*").execute()
    return r.data or []


def count_whatsapp_since(sb: Client, client_id: uuid.UUID, since_iso: str) -> int:
    r = (
        sb.table("whatsapp_logs")
        .select("id", count="exact")
        .eq("client_id", str(client_id))
        .gte("sent_at", since_iso)
        .execute()
    )
    return int(r.count or 0)


def count_whatsapp_type_since(sb: Client, client_id: uuid.UUID, message_type: str, since_iso: str) -> int:
    r = (
        sb.table("whatsapp_logs")
        .select("id", count="exact")
        .eq("client_id", str(client_id))
        .eq("message_type", message_type)
        .gte("sent_at", since_iso)
        .execute()
    )
    return int(r.count or 0)


def count_documents_pending_firm(sb: Client, firm_id: uuid.UUID) -> int:
    r = (
        sb.table("documents")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .eq("review_status", "pending")
        .execute()
    )
    return int(r.count or 0)


def all_clients_firm(sb: Client, firm_id: uuid.UUID) -> list[dict[str, Any]]:
    r = sb.table("clients").select("*").eq("firm_id", str(firm_id)).execute()
    return r.data or []


def all_clients_firm_phone_match(sb: Client, firm_id: uuid.UUID) -> list[dict[str, Any]]:
    r = sb.table("clients").select("*").eq("firm_id", str(firm_id)).execute()
    return r.data or []


def touch_client_activity(sb: Client, client_id: uuid.UUID) -> None:
    update_client(sb, client_id, {"last_activity_at": utc_now_iso()})
