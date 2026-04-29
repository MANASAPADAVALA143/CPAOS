from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.db import get_supabase
from app.db import repo
from app.db.dates import utc_now_iso
from app.models.enums import ClientStatus, MessageChannel, MessageDeliveryStatus
from app.services.messaging import send_message


def _portal_url(firm: dict, client: dict) -> str:
    base = get_settings().frontend_url.rstrip("/")
    return f"{base}/portal/{firm['slug']}/{client['onboarding_token']}"


def _last_message_days_ago(sb, client_id: uuid.UUID, days: int) -> bool:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    n = repo.count_whatsapp_since(sb, client_id, since)
    return n == 0


def _no_log_type_since_hours(sb, client_id: uuid.UUID, message_type: str, hours: int) -> bool:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    n = repo.count_whatsapp_type_since(sb, client_id, message_type, since)
    return n == 0


def run_daily_reminders() -> dict:
    sb = get_supabase()
    sent = 0
    cutoff2 = datetime.now(timezone.utc) - timedelta(days=2)
    cutoff5 = datetime.now(timezone.utc) - timedelta(days=5)
    candidates = []
    for c in repo.list_clients_for_reminders(sb):
        st = c.get("status")
        if st not in (ClientStatus.in_progress.value, ClientStatus.documents_pending.value):
            continue
        if int(c.get("completion_pct") or 0) >= 100:
            continue
        la = c.get("last_activity_at")
        if not la:
            continue
        try:
            last = datetime.fromisoformat(str(la).replace("Z", "+00:00"))
        except ValueError:
            continue
        if last >= cutoff2:
            continue
        candidates.append(c)

    for c in candidates:
        cid = uuid.UUID(str(c["id"]))
        fid = uuid.UUID(str(c["firm_id"]))
        firm = repo.firm_by_id(sb, fid)
        if not firm:
            continue
        pending = repo.checklist_pending_for_client(sb, cid)
        pending_items = "\n".join(f"- {p['item_name']}" for p in pending[:10]) or "- None"
        variables = {
            "client_name": c["client_name"],
            "firm_name": firm["name"],
            "portal_link": _portal_url(firm, c),
            "doc_count": str(len(pending)),
            "deadline": "this week",
            "completion_pct": str(c.get("completion_pct", 0)),
            "pending_items": pending_items,
        }

        try:
            last_act = datetime.fromisoformat(str(c.get("last_activity_at", "")).replace("Z", "+00:00"))
        except ValueError:
            last_act = datetime.now(timezone.utc)

        if last_act < cutoff5 and _last_message_days_ago(sb, cid, 3):
            if not _no_log_type_since_hours(sb, cid, "reminder_day5_auto", 24 * 5):
                continue
            result = send_message(c["phone"], "reminder_day5", variables)
            ch = MessageChannel.whatsapp.value if result.get("channel") == "whatsapp" else MessageChannel.sms.value
            repo.insert_whatsapp_log(
                sb,
                client_id=cid,
                firm_id=fid,
                channel=ch,
                message_type="reminder_day5_auto",
                phone_number=c["phone"],
                message_content="reminder_day5",
                status=MessageDeliveryStatus.sent.value
                if result.get("status") == "sent"
                else MessageDeliveryStatus.failed.value,
            )
            repo.insert_activity(
                sb,
                client_id=cid,
                firm_id=fid,
                action="auto_reminder_day5",
                description="Automatic day-5 reminder",
                performed_by="system",
            )
            sent += 1
            continue

        if _no_log_type_since_hours(sb, cid, "reminder_day2_auto", 48):
            result = send_message(c["phone"], "reminder_day2", variables)
            ch = MessageChannel.whatsapp.value if result.get("channel") == "whatsapp" else MessageChannel.sms.value
            repo.insert_whatsapp_log(
                sb,
                client_id=cid,
                firm_id=fid,
                channel=ch,
                message_type="reminder_day2_auto",
                phone_number=c["phone"],
                message_content="reminder_day2",
                status=MessageDeliveryStatus.sent.value
                if result.get("status") == "sent"
                else MessageDeliveryStatus.failed.value,
            )
            repo.insert_activity(
                sb,
                client_id=cid,
                firm_id=fid,
                action="auto_reminder_day2",
                description="Automatic day-2 reminder",
                performed_by="system",
            )
            sent += 1

    sig_cut = datetime.now(timezone.utc) - timedelta(days=2)
    for c in repo.list_clients_for_reminders(sb):
        if not c.get("engagement_letter_sent") or c.get("engagement_letter_signed"):
            continue
        created = c.get("created_at")
        if not created:
            continue
        try:
            cr = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        except ValueError:
            continue
        if cr >= sig_cut:
            continue
        cid = uuid.UUID(str(c["id"]))
        if not _last_message_days_ago(sb, cid, 2):
            continue
        fid = uuid.UUID(str(c["firm_id"]))
        firm = repo.firm_by_id(sb, fid)
        if not firm:
            continue
        variables = {
            "client_name": c["client_name"],
            "firm_name": firm["name"],
            "portal_link": _portal_url(firm, c),
            "doc_count": "0",
            "deadline": "—",
            "completion_pct": str(c.get("completion_pct", 0)),
            "pending_items": "—",
        }
        result = send_message(c["phone"], "engagement_sign_reminder", variables)
        ch = MessageChannel.whatsapp.value if result.get("channel") == "whatsapp" else MessageChannel.sms.value
        repo.insert_whatsapp_log(
            sb,
            client_id=cid,
            firm_id=fid,
            channel=ch,
            message_type="engagement_sign_reminder",
            phone_number=c["phone"],
            message_content="engagement_sign_reminder",
            status=MessageDeliveryStatus.sent.value if result.get("status") == "sent" else MessageDeliveryStatus.failed.value,
        )
        repo.insert_activity(
            sb,
            client_id=cid,
            firm_id=fid,
            action="engagement_letter_reminder",
            description="Automatic engagement letter reminder",
            performed_by="system",
        )
        sent += 1

    return {"processed": sent}
