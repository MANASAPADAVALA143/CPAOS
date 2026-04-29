from __future__ import annotations

import calendar
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db
from app.db import repo
from app.db.dates import parse_dt
from app.models.enums import ClientStatus
from app.models.staff import FirmUser

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
    sb: Client = Depends(get_db),
):
    firm_id = current.firm_id
    clients = repo.all_clients_firm(sb, firm_id)
    total = len(clients)
    active_clients = sum(
        1 for c in clients if c.get("status") not in (ClientStatus.completed.value, ClientStatus.active.value)
    )

    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    completed_this_month = 0
    for c in clients:
        if c.get("status") != ClientStatus.completed.value:
            continue
        ca = parse_dt(c.get("completed_at"))
        if ca and ca >= month_start:
            completed_this_month += 1

    deltas = []
    for c in clients:
        if c.get("status") != ClientStatus.completed.value:
            continue
        ca = parse_dt(c.get("completed_at"))
        cr = parse_dt(c.get("created_at"))
        if ca and cr:
            deltas.append((ca - cr).total_seconds() / 86400)
    avg_completion_days = round(sum(deltas) / len(deltas), 1) if deltas else 0.0

    docs_pending_review = repo.count_documents_pending_firm(sb, firm_id)

    signature_pending = sum(1 for c in clients if c.get("status") == ClientStatus.signature_pending.value)

    completed_total = sum(1 for c in clients if c.get("status") == ClientStatus.completed.value)
    completion_rate_pct = int(round(100 * completed_total / total)) if total else 0

    by_country: dict[str, int] = defaultdict(int)
    for c in clients:
        by_country[str(c.get("country", ""))] += 1

    by_status: dict[str, int] = defaultdict(int)
    for c in clients:
        by_status[str(c.get("status", ""))] += 1

    recent_rows = repo.list_onboarding_activity(sb, firm_id, limit=20)
    client_ids = list({uuid.UUID(str(r["client_id"])) for r in recent_rows})
    cmap: dict[str, dict] = {}
    for cid in client_ids:
        cl = repo.client_by_id(sb, cid, firm_id)
        if cl:
            cmap[str(cid)] = cl
    recent_activity = []
    for act in recent_rows:
        cl = cmap.get(str(act["client_id"]), {})
        recent_activity.append(
            {
                "client_name": cl.get("client_name", "Client"),
                "action": act["action"],
                "description": act["description"],
                "performed_by": act["performed_by"],
                "created_at": str(act.get("created_at", "")) + ("Z" if act.get("created_at") and "Z" not in str(act.get("created_at")) else ""),
            }
        )

    trend: dict[str, int] = defaultdict(int)
    for c in clients:
        if c.get("status") != ClientStatus.completed.value:
            continue
        ca = parse_dt(c.get("completed_at"))
        if not ca:
            continue
        key = f"{ca.year}-{ca.month:02d}"
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
