from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func

from app.core.config import get_settings
from app.db import SessionLocal
from app.models.onboarding import (
    ChecklistItem,
    ChecklistItemStatus,
    Client,
    ClientStatus,
    Firm,
    MessageChannel,
    MessageDeliveryStatus,
    OnboardingActivity,
    WhatsAppLog,
)
from app.services.messaging import send_message


def _portal_url(firm: Firm, client: Client) -> str:
    base = get_settings().frontend_url.rstrip("/")
    return f"{base}/portal/{firm.slug}/{client.onboarding_token}"


def _last_message_days_ago(db, client_id, days: int) -> bool:
    since = datetime.utcnow() - timedelta(days=days)
    n = (
        db.query(func.count(WhatsAppLog.id))
        .filter(WhatsAppLog.client_id == client_id, WhatsAppLog.sent_at >= since)
        .scalar()
    )
    return int(n or 0) == 0


def _no_log_type_since_hours(db, client_id: str, message_type: str, hours: int) -> bool:
    since = datetime.utcnow() - timedelta(hours=hours)
    n = (
        db.query(func.count(WhatsAppLog.id))
        .filter(
            WhatsAppLog.client_id == client_id,
            WhatsAppLog.message_type == message_type,
            WhatsAppLog.sent_at >= since,
        )
        .scalar()
    )
    return int(n or 0) == 0


def run_daily_reminders() -> dict:
    db = SessionLocal()
    sent = 0
    try:
        cutoff2 = datetime.utcnow() - timedelta(days=2)
        cutoff5 = datetime.utcnow() - timedelta(days=5)
        candidates = (
            db.query(Client)
            .filter(
                Client.status.in_([ClientStatus.in_progress, ClientStatus.documents_pending]),
                Client.completion_pct < 100,
                Client.last_activity_at < cutoff2,
            )
            .all()
        )
        for c in candidates:
            firm = db.query(Firm).filter(Firm.id == c.firm_id).first()
            if not firm:
                continue
            pending = (
                db.query(ChecklistItem)
                .filter(ChecklistItem.client_id == c.id, ChecklistItem.status == ChecklistItemStatus.pending)
                .all()
            )
            pending_items = "\n".join(f"- {p.item_name}" for p in pending[:10]) or "- None"
            variables = {
                "client_name": c.client_name,
                "firm_name": firm.name,
                "portal_link": _portal_url(firm, c),
                "doc_count": str(len(pending)),
                "deadline": "this week",
                "completion_pct": str(c.completion_pct),
                "pending_items": pending_items,
            }

            if c.last_activity_at < cutoff5 and _last_message_days_ago(db, c.id, 3):
                if not _no_log_type_since_hours(db, c.id, "reminder_day5_auto", 24 * 5):
                    continue
                result = send_message(c.phone, "reminder_day5", variables)
                ch = MessageChannel.whatsapp if result.get("channel") == "whatsapp" else MessageChannel.sms
                db.add(
                    WhatsAppLog(
                        client_id=c.id,
                        firm_id=c.firm_id,
                        channel=ch,
                        message_type="reminder_day5_auto",
                        phone_number=c.phone,
                        message_content="reminder_day5",
                        status=MessageDeliveryStatus.sent
                        if result.get("status") == "sent"
                        else MessageDeliveryStatus.failed,
                    )
                )
                db.add(
                    OnboardingActivity(
                        client_id=c.id,
                        firm_id=c.firm_id,
                        action="auto_reminder_day5",
                        description="Automatic day-5 reminder",
                        performed_by="system",
                    )
                )
                sent += 1
                continue

            if _no_log_type_since_hours(db, c.id, "reminder_day2_auto", 48):
                result = send_message(c.phone, "reminder_day2", variables)
                ch = MessageChannel.whatsapp if result.get("channel") == "whatsapp" else MessageChannel.sms
                db.add(
                    WhatsAppLog(
                        client_id=c.id,
                        firm_id=c.firm_id,
                        channel=ch,
                        message_type="reminder_day2_auto",
                        phone_number=c.phone,
                        message_content="reminder_day2",
                        status=MessageDeliveryStatus.sent
                        if result.get("status") == "sent"
                        else MessageDeliveryStatus.failed,
                    )
                )
                db.add(
                    OnboardingActivity(
                        client_id=c.id,
                        firm_id=c.firm_id,
                        action="auto_reminder_day2",
                        description="Automatic day-2 reminder",
                        performed_by="system",
                    )
                )
                sent += 1

        sig_cut = datetime.utcnow() - timedelta(days=2)
        qsig = (
            db.query(Client)
            .filter(
                Client.engagement_letter_sent.is_(True),
                Client.engagement_letter_signed.is_(False),
                Client.created_at < sig_cut,
            )
            .all()
        )
        for c in qsig:
            if not _last_message_days_ago(db, c.id, 2):
                continue
            firm = db.query(Firm).filter(Firm.id == c.firm_id).first()
            if not firm:
                continue
            variables = {
                "client_name": c.client_name,
                "firm_name": firm.name,
                "portal_link": _portal_url(firm, c),
                "doc_count": "0",
                "deadline": "—",
                "completion_pct": str(c.completion_pct),
                "pending_items": "—",
            }
            result = send_message(c.phone, "engagement_sign_reminder", variables)
            ch = MessageChannel.whatsapp if result.get("channel") == "whatsapp" else MessageChannel.sms
            db.add(
                WhatsAppLog(
                    client_id=c.id,
                    firm_id=c.firm_id,
                    channel=ch,
                    message_type="engagement_sign_reminder",
                    phone_number=c.phone,
                    message_content="engagement_sign_reminder",
                    status=MessageDeliveryStatus.sent if result.get("status") == "sent" else MessageDeliveryStatus.failed,
                )
            )
            db.add(
                OnboardingActivity(
                    client_id=c.id,
                    firm_id=c.firm_id,
                    action="engagement_letter_reminder",
                    description="Automatic engagement letter reminder",
                    performed_by="system",
                )
            )
            sent += 1

        db.commit()
        return {"processed": sent}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
