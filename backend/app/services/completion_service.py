from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.onboarding import (
    Client,
    ClientStatus,
    Firm,
    FirmUser,
    FirmUserRole,
    MessageChannel,
    MessageDeliveryStatus,
    OnboardingActivity,
    WhatsAppLog,
)
from app.services.email_service import send_onboarding_complete_staff_email
from app.services.messaging import send_message


def maybe_complete_client(db: Session, client: Client) -> bool:
    """When completion reaches 100%, finalize onboarding and notify client + staff."""
    if client.completion_pct < 100:
        return False
    if client.status == ClientStatus.completed:
        return False

    firm = db.query(Firm).filter(Firm.id == client.firm_id).first()
    if not firm:
        return False

    client.status = ClientStatus.completed
    client.completed_at = datetime.utcnow()
    client.last_activity_at = datetime.utcnow()
    db.add(client)

    db.add(
        OnboardingActivity(
            client_id=client.id,
            firm_id=client.firm_id,
            action="onboarding_completed",
            description="All required items verified — onboarding marked complete",
            performed_by="system",
        )
    )

    variables = {
        "client_name": client.client_name,
        "firm_name": firm.name,
        "portal_link": f"{get_settings().frontend_url.rstrip('/')}/portal/{firm.slug}/{client.onboarding_token}",
        "doc_count": "0",
        "deadline": "—",
        "completion_pct": "100",
        "pending_items": "—",
    }
    result = send_message(client.phone, "completion", variables, prefer="whatsapp")
    ch = MessageChannel.whatsapp
    if result.get("channel") == "sms":
        ch = MessageChannel.sms
    db.add(
        WhatsAppLog(
            client_id=client.id,
            firm_id=client.firm_id,
            channel=ch,
            message_type="completion",
            phone_number=client.phone,
            message_content="completion",
            status=MessageDeliveryStatus.sent if result.get("status") == "sent" else MessageDeliveryStatus.failed,
        )
    )

    staff_email: str | None = None
    if client.assigned_to:
        assignee = db.query(FirmUser).filter(FirmUser.id == client.assigned_to).first()
        if assignee:
            staff_email = assignee.email
    if not staff_email:
        owner = (
            db.query(FirmUser)
            .filter(FirmUser.firm_id == firm.id, FirmUser.role == FirmUserRole.owner, FirmUser.is_active.is_(True))
            .first()
        )
        if owner:
            staff_email = owner.email
    if staff_email:
        send_onboarding_complete_staff_email(
            staff_email, client.client_name, str(client.id), firm.name
        )

    db.flush()
    return True
