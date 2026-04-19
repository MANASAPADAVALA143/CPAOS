from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_firm_user
from app.db import get_db
from app.models.onboarding import (
    Client,
    ClientStatus,
    Document,
    DocumentReviewStatus,
    FirmUser,
    OnboardingActivity,
)

router = APIRouter()


def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    m = month + delta
    y = year
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return y, m


@router.get("/analytics/dashboard")
def dashboard_analytics(
    current: FirmUser = Depends(get_current_firm_user),
    db: Session = Depends(get_db),
):
    firm_id = current.firm_id
    clients = db.query(Client).filter(Client.firm_id == firm_id).all()
    total = len(clients)
    active_clients = sum(1 for c in clients if c.status not in (ClientStatus.completed, ClientStatus.active))

    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    completed_this_month = sum(
        1
        for c in clients
        if c.status == ClientStatus.completed and c.completed_at and c.completed_at >= month_start
    )

    completed_rows = [c for c in clients if c.status == ClientStatus.completed and c.completed_at and c.created_at]
    deltas = [(c.completed_at - c.created_at).total_seconds() / 86400 for c in completed_rows if c.completed_at]
    avg_completion_days = round(sum(deltas) / len(deltas), 1) if deltas else 0.0

    docs_pending_review = (
        db.query(func.count(Document.id))
        .filter(Document.firm_id == firm_id, Document.review_status == DocumentReviewStatus.pending)
        .scalar()
        or 0
    )

    signature_pending = sum(1 for c in clients if c.status == ClientStatus.signature_pending)

    completed_total = sum(1 for c in clients if c.status == ClientStatus.completed)
    completion_rate_pct = int(round(100 * completed_total / total)) if total else 0

    by_country: dict[str, int] = defaultdict(int)
    for c in clients:
        by_country[c.country.value] += 1

    by_status: dict[str, int] = defaultdict(int)
    for c in clients:
        by_status[c.status.value] += 1

    recent = (
        db.query(OnboardingActivity, Client)
        .join(Client, Client.id == OnboardingActivity.client_id)
        .filter(OnboardingActivity.firm_id == firm_id)
        .order_by(OnboardingActivity.created_at.desc())
        .limit(20)
        .all()
    )
    recent_activity = [
        {
            "client_name": cl.client_name if cl else "Client",
            "action": act.action,
            "description": act.description,
            "performed_by": act.performed_by,
            "created_at": act.created_at.isoformat() + "Z",
        }
        for act, cl in recent
    ]

    trend: dict[str, int] = defaultdict(int)
    for c in clients:
        if c.status != ClientStatus.completed or not c.completed_at:
            continue
        cm = datetime(c.completed_at.year, c.completed_at.month, 1)
        key = f"{cm.year}-{cm.month:02d}"
        trend[key] += 1

    months_out = []
    for delta in (-3, -2, -1, 0):
        yy, mm = _shift_month(now.year, now.month, delta)
        label = calendar.month_abbr[mm]
        key = f"{yy}-{mm:02d}"
        months_out.append({"month": label, "completed": int(trend.get(key, 0))})

    return {
        "kpis": {
            "active_clients": active_clients,
            "completed_this_month": completed_this_month,
            "avg_completion_days": avg_completion_days,
            "docs_pending_review": int(docs_pending_review),
            "signature_pending": signature_pending,
            "completion_rate_pct": completion_rate_pct,
        },
        "by_country": [{"country": k, "count": v} for k, v in sorted(by_country.items(), key=lambda x: -x[1])],
        "by_status": [{"status": k, "count": v} for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        "recent_activity": recent_activity,
        "completion_trend": months_out,
    }
