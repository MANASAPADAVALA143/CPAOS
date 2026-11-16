from __future__ import annotations

import uuid
from datetime import datetime, timezone

from supabase import Client

from app.core.config import get_settings
from app.db import repo
from app.models.enums import ClientStatus, FirmUserRole, MessageChannel, MessageDeliveryStatus
from app.services.email_service import send_onboarding_complete_staff_email
from app.services.messaging import send_message


def maybe_complete_client(sb: Client, client_id: uuid.UUID) -> bool:
    """When completion reaches 100%, finalize onboarding and notify client + staff."""
    c = repo.client_by_id(sb, client_id)
    if not c:
        return False
    if int(c.get("completion_pct") or 0) < 100:
        return False
    if c.get("status") == ClientStatus.completed.value:
        return False

    firm_id = uuid.UUID(str(c["firm_id"]))
    firm = repo.firm_by_id(sb, firm_id)
    if not firm:
        return False

    now = datetime.now(timezone.utc).isoformat()
    repo.update_client(
        sb,
        client_id,
        {
            "status": ClientStatus.completed.value,
            "completed_at": now,
            "last_activity_at": now,
        },
    )

    repo.insert_activity(
        sb,
        client_id=client_id,
        firm_id=firm_id,
        action="onboarding_completed",
        description="All required items verified — onboarding marked complete",
        performed_by="system",
    )

    token = str(c["onboarding_token"])
    slug = firm["slug"]
    portal = f"{get_settings().frontend_url.rstrip('/')}/portal/{slug}/{token}"
    variables = {
        "client_name": c["client_name"],
        "firm_name": firm["name"],
        "portal_link": portal,
        "doc_count": "0",
        "deadline": "—",
        "completion_pct": "100",
        "pending_items": "—",
    }
    result = send_message(c["phone"], "completion", variables, prefer="whatsapp")
    ch = MessageChannel.whatsapp.value
    if result.get("channel") == "sms":
        ch = MessageChannel.sms.value
    repo.insert_whatsapp_log(
        sb,
        client_id=client_id,
        firm_id=firm_id,
        channel=ch,
        message_type="completion",
        phone_number=c["phone"],
        message_content="completion",
        status=MessageDeliveryStatus.sent.value if result.get("status") == "sent" else MessageDeliveryStatus.failed.value,
    )

    staff_email: str | None = None
    if c.get("assigned_to"):
        assignee = repo.firm_user_by_id(sb, uuid.UUID(str(c["assigned_to"])))
        if assignee:
            staff_email = assignee["email"]
    if not staff_email:
        owner = repo.owner_user_for_firm(sb, firm_id)
        if owner:
            staff_email = owner["email"]
    if staff_email:
        send_onboarding_complete_staff_email(
            staff_email, c["client_name"], str(client_id), firm["name"]
        )

    return True
