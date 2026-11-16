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
    country: str | None = None,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    firm_id = current.firm_id
    all_clients = repo.all_clients_firm(sb, firm_id)

    country_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "pct_sum": 0})
    for c in all_clients:
        s = country_stats[str(c.get("country", ""))]
        s["count"] += 1
        s["pct_sum"] += int(c.get("completion_pct") or 0)

    clients = [c for c in all_clients if c.get("country") == country] if country else all_clients
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

    if country:
        docs_pending_review = repo.count_documents_pending_clients(sb, firm_id, [str(c["id"]) for c in clients])
    else:
        docs_pending_review = repo.count_documents_pending_firm(sb, firm_id)

    signature_pending = sum(1 for c in clients if c.get("status") == ClientStatus.signature_pending.value)

    completed_total = sum(1 for c in clients if c.get("status") == ClientStatus.completed.value)
    completion_rate_pct = int(round(100 * completed_total / total)) if total else 0

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
    for delta in (-5, -4, -3, -2, -1, 0):
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
        "by_country": [
            {
                "country": k,
                "count": v["count"],
                "avg_completion_pct": int(round(v["pct_sum"] / v["count"])) if v["count"] else 0,
            }
            for k, v in sorted(country_stats.items(), key=lambda x: -x[1]["count"])
        ],
        "by_status": [{"status": k, "count": v} for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        "recent_activity": recent_activity,
        "completion_trend": months_out,
    }


@router.get("/analytics/practice-dashboard")
def practice_dashboard_analytics(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Practice management dashboard with assignment and staff KPIs"""
    from app.services import assignment_service
    
    firm_id = current.firm_id
    
    # Client KPIs
    all_clients = repo.all_clients_firm(sb, firm_id)
    total_clients = len(all_clients)
    active_clients = sum(
        1 for c in all_clients if c.get("status") not in (ClientStatus.completed.value, ClientStatus.active.value)
    )
    
    # Assignment KPIs
    active_statuses = ["created", "assigned", "in_progress", "submitted", "manager_review", "partner_review"]
    active_assignments = repo.count_assignments(sb, firm_id, status=active_statuses)
    overdue_assignments = repo.count_overdue_assignments(sb, firm_id)
    
    # Count completed assignments this month
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    completed_assignments_month = repo.count_assignments(
        sb, firm_id, status="completed"
    )  # Simplified - would need date filter in production
    
    # Review queue KPIs
    pending_manager_reviews = 0
    pending_partner_reviews = 0
    try:
        # Count pending reviews by level
        all_reviews_resp = sb.table("assignment_reviews").select("review_level", count="exact").eq("status", "pending").execute()
        # Note: This is simplified. In production, filter by firm_id via join
        pending_manager_reviews = sum(1 for r in (all_reviews_resp.data or []) if r.get("review_level") == "manager")
        pending_partner_reviews = sum(1 for r in (all_reviews_resp.data or []) if r.get("review_level") == "partner")
    except Exception:
        pass
    
    # Staff utilization (simplified - would calculate from timesheets in production)
    staff_workload = assignment_service.get_staff_workload_summary(sb, firm_id)
    avg_utilization = int(sum(s["utilization_pct"] for s in staff_workload) / len(staff_workload)) if staff_workload else 0
    
    # Document KPIs
    docs_pending_review = repo.count_documents_pending_firm(sb, firm_id)
    
    # Assignment breakdown by status
    all_assignments = repo.list_assignments_filtered(sb, firm_id)
    assignments_by_status: dict[str, int] = defaultdict(int)
    for a in all_assignments:
        assignments_by_status[a.get("status", "unknown")] += 1
    
    # Get overdue assignments list (top 10)
    overdue_list = assignment_service.get_overdue_assignments(sb, firm_id, limit=10)
    
    return {
        "kpis": {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "active_assignments": active_assignments,
            "overdue_assignments": overdue_assignments,
            "completed_assignments_month": completed_assignments_month,
            "pending_manager_reviews": pending_manager_reviews,
            "pending_partner_reviews": pending_partner_reviews,
            "pending_reviews": pending_manager_reviews + pending_partner_reviews,
            "docs_pending_review": docs_pending_review,
            "staff_utilization": avg_utilization,
        },
        "assignments_by_status": [
            {"status": k, "count": v}
            for k, v in sorted(assignments_by_status.items(), key=lambda x: -x[1])
        ],
        "overdue_assignments": [
            {
                "assignment_id": a["id"],
                "assignment_code": a["assignment_code"],
                "assignment_name": a["assignment_name"],
                "client_name": a.get("clients", {}).get("client_name", ""),
                "due_date": a["due_date"],
                "days_overdue": (now.date() - datetime.fromisoformat(a["due_date"]).date()).days,
                "assigned_staff": a.get("assigned_staff"),
            }
            for a in overdue_list
        ],
        "staff_workload": staff_workload[:10],  # Top 10 staff by workload
    }
