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


def checklist_items_expiring_by(sb: Client, firm_id: uuid.UUID, cutoff_iso: str) -> list[dict[str, Any]]:
    r = (
        sb.table("checklist_items")
        .select("*, clients!inner(client_name, country, firm_id)")
        .eq("clients.firm_id", str(firm_id))
        .lte("expiry_date", cutoff_iso)
        .order("expiry_date")
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


def count_documents_pending_clients(sb: Client, firm_id: uuid.UUID, client_ids: list[str]) -> int:
    if not client_ids:
        return 0
    r = (
        sb.table("documents")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .eq("review_status", "pending")
        .in_("client_id", client_ids)
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


# ============================================================================
# ASSIGNMENT MANAGEMENT (CA PRACTICE OS)
# ============================================================================


def assignment_by_id(sb: Client, assignment_id: uuid.UUID, firm_id: uuid.UUID | None = None) -> dict[str, Any] | None:
    """Get assignment by ID with optional firm isolation"""
    q = sb.table("assignments").select("*").eq("id", str(assignment_id))
    if firm_id is not None:
        q = q.eq("firm_id", str(firm_id))
    r = q.limit(1).execute()
    return r.data[0] if r.data else None


def list_assignments_filtered(
    sb: Client,
    firm_id: uuid.UUID,
    *,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    assigned_partner: uuid.UUID | None = None,
    assigned_manager: uuid.UUID | None = None,
    assigned_staff: uuid.UUID | None = None,
    service_category: str | None = None,
    search: str | None = None,
    overdue_only: bool = False,
) -> list[dict[str, Any]]:
    """List assignments with filters"""
    q = sb.table("assignments").select("*, clients!inner(client_name, business_name)").eq("firm_id", str(firm_id))
    
    if client_id is not None:
        q = q.eq("client_id", str(client_id))
    if status:
        q = q.eq("status", status)
    if assigned_partner is not None:
        q = q.eq("assigned_partner", str(assigned_partner))
    if assigned_manager is not None:
        q = q.eq("assigned_manager", str(assigned_manager))
    if assigned_staff is not None:
        q = q.eq("assigned_staff", str(assigned_staff))
    if service_category:
        q = q.eq("service_category", service_category)
    if search:
        q = q.ilike("assignment_name", f"%{search}%")
    if overdue_only:
        today = utc_now_iso()[:10]  # Get date part YYYY-MM-DD
        q = q.lt("due_date", today).neq("status", "completed")
    
    r = q.order("due_date", desc=False).execute()
    return r.data or []


def count_assignments(sb: Client, firm_id: uuid.UUID, **filters) -> int:
    """Count assignments with filters"""
    q = sb.table("assignments").select("id", count="exact").eq("firm_id", str(firm_id))
    
    if "status" in filters and filters["status"]:
        if isinstance(filters["status"], list):
            q = q.in_("status", filters["status"])
        else:
            q = q.eq("status", filters["status"])
    
    if "assigned_staff" in filters and filters["assigned_staff"]:
        q = q.eq("assigned_staff", str(filters["assigned_staff"]))
    
    r = q.execute()
    return int(r.count or 0)


def count_overdue_assignments(sb: Client, firm_id: uuid.UUID) -> int:
    """Count overdue assignments"""
    today = utc_now_iso()[:10]
    r = (
        sb.table("assignments")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .lt("due_date", today)
        .neq("status", "completed")
        .execute()
    )
    return int(r.count or 0)


def create_assignment(sb: Client, data: dict[str, Any]) -> dict[str, Any]:
    """Create new assignment"""
    r = sb.table("assignments").insert(data).execute()
    if not r.data:
        raise RuntimeError("Failed to create assignment")
    return r.data[0]


def update_assignment(sb: Client, assignment_id: uuid.UUID, updates: dict[str, Any]) -> None:
    """Update assignment"""
    updates["updated_at"] = utc_now_iso()
    sb.table("assignments").update(updates).eq("id", str(assignment_id)).execute()


def delete_assignment(sb: Client, assignment_id: uuid.UUID, firm_id: uuid.UUID) -> None:
    """Delete assignment (with firm isolation)"""
    sb.table("assignments").delete().eq("id", str(assignment_id)).eq("firm_id", str(firm_id)).execute()


def get_staff_workload(
    sb: Client,
    firm_id: uuid.UUID,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Get staff workload summary"""
    # Get all assignments in date range, grouped by staff
    q = sb.table("assignments").select("assigned_staff, estimated_hours, actual_hours, status").eq("firm_id", str(firm_id))
    
    if start_date:
        q = q.gte("due_date", start_date)
    if end_date:
        q = q.lte("due_date", end_date)
    
    r = q.execute()
    assignments = r.data or []
    
    # Group by staff
    workload_map: dict[str, dict] = {}
    for a in assignments:
        staff_id = a.get("assigned_staff")
        if not staff_id:
            continue
        
        if staff_id not in workload_map:
            workload_map[staff_id] = {
                "staff_id": staff_id,
                "assignments_count": 0,
                "estimated_hours": 0,
                "actual_hours": 0,
            }
        
        workload_map[staff_id]["assignments_count"] += 1
        workload_map[staff_id]["estimated_hours"] += float(a.get("estimated_hours") or 0)
        workload_map[staff_id]["actual_hours"] += float(a.get("actual_hours") or 0)
    
    return list(workload_map.values())


# ============================================================================
# ASSIGNMENT REVIEWS
# ============================================================================


def create_assignment_review(sb: Client, data: dict[str, Any]) -> dict[str, Any]:
    """Create assignment review record"""
    r = sb.table("assignment_reviews").insert(data).execute()
    if not r.data:
        raise RuntimeError("Failed to create assignment review")
    return r.data[0]


def get_assignment_reviews(sb: Client, assignment_id: uuid.UUID) -> list[dict[str, Any]]:
    """Get all reviews for an assignment"""
    r = (
        sb.table("assignment_reviews")
        .select("*, firm_users!inner(full_name, email)")
        .eq("assignment_id", str(assignment_id))
        .order("created_at", desc=True)
        .execute()
    )
    return r.data or []


def get_pending_reviews(sb: Client, firm_id: uuid.UUID, reviewer_id: uuid.UUID, review_level: str | None = None) -> list[dict[str, Any]]:
    """Get pending reviews for a reviewer"""
    # Get assignments with pending reviews
    q = (
        sb.table("assignment_reviews")
        .select("*, assignments!inner(*, clients!inner(client_name))")
        .eq("reviewer_id", str(reviewer_id))
        .eq("status", "pending")
    )
    
    if review_level:
        q = q.eq("review_level", review_level)
    
    r = q.order("submitted_at", desc=False).execute()
    
    # Filter by firm_id (assignments.firm_id)
    reviews = r.data or []
    return [rev for rev in reviews if rev.get("assignments", {}).get("firm_id") == str(firm_id)]


def update_assignment_review(sb: Client, review_id: uuid.UUID, updates: dict[str, Any]) -> None:
    """Update assignment review"""
    sb.table("assignment_reviews").update(updates).eq("id", str(review_id)).execute()


def count_pending_reviews(sb: Client, firm_id: uuid.UUID, review_level: str | None = None) -> int:
    """Count pending reviews for a firm"""
    # Need to join with assignments to filter by firm_id
    q = (
        sb.table("assignment_reviews")
        .select("id", count="exact")
        .eq("status", "pending")
    )
    
    if review_level:
        q = q.eq("review_level", review_level)
    
    r = q.execute()
    
    # Note: This is a simplified count. For accurate firm filtering, 
    # we'd need to join with assignments table, but Supabase REST API
    # doesn't support count with joins easily. We'll handle this in the service layer.
    return int(r.count or 0)


# ============================================================================
# PHASE 2: COMPLIANCE CALENDAR REPOSITORY FUNCTIONS
# ============================================================================

def list_compliance_templates(
    sb: Client,
    firm_id: uuid.UUID | None = None,
    country: str | None = None,
    service_category: str | None = None,
    is_active: bool = True,
) -> list[dict[str, Any]]:
    """List compliance templates with filters"""
    q = sb.table("compliance_templates").select("*")
    
    if firm_id:
        # Include both firm-specific and system templates
        q = q.or_(f"firm_id.eq.{firm_id},firm_id.is.null")
    else:
        # Only system templates
        q = q.is_("firm_id", "null")
    
    if country:
        q = q.eq("country", country)
    
    if service_category:
        q = q.eq("service_category", service_category)
    
    if is_active:
        q = q.eq("is_active", True)
    
    q = q.order("country", desc=False).order("service_category", desc=False)
    r = q.execute()
    return r.data or []


def compliance_template_by_id(sb: Client, template_id: uuid.UUID) -> dict[str, Any] | None:
    """Get compliance template by ID"""
    r = sb.table("compliance_templates").select("*").eq("id", str(template_id)).limit(1).execute()
    return r.data[0] if r.data else None


def create_compliance_template(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a compliance template"""
    r = sb.table("compliance_templates").insert(data).execute()
    return r.data[0] if r.data else None


def update_compliance_template(sb: Client, template_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a compliance template"""
    data["updated_at"] = utc_now_iso()
    r = sb.table("compliance_templates").update(data).eq("id", str(template_id)).execute()
    return r.data[0] if r.data else None


def list_compliance_requirements(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    service_category: str | None = None,
    financial_year: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List compliance requirements with filters"""
    q = (
        sb.table("compliance_requirements")
        .select("""
            *,
            clients!compliance_requirements_client_id_fkey(company_name),
            firm_users!compliance_requirements_assigned_to_fkey(full_name),
            compliance_templates!compliance_requirements_template_id_fkey(compliance_code)
        """)
        .eq("firm_id", str(firm_id))
    )
    
    if client_id:
        q = q.eq("client_id", str(client_id))
    
    if status:
        q = q.eq("status", status)
    
    if service_category:
        q = q.eq("service_category", service_category)
    
    if financial_year:
        q = q.eq("financial_year", financial_year)
    
    if from_date:
        q = q.gte("due_date", from_date)
    
    if to_date:
        q = q.lte("due_date", to_date)
    
    q = q.order("due_date", desc=False).range(offset, offset + limit - 1)
    r = q.execute()
    return r.data or []


def compliance_requirement_by_id(sb: Client, requirement_id: uuid.UUID, firm_id: uuid.UUID) -> dict[str, Any] | None:
    """Get compliance requirement by ID with firm isolation"""
    r = (
        sb.table("compliance_requirements")
        .select("""
            *,
            clients!compliance_requirements_client_id_fkey(company_name, country, entity_type),
            firm_users!compliance_requirements_assigned_to_fkey(full_name, email),
            compliance_templates!compliance_requirements_template_id_fkey(compliance_code, penalty_info, documents_required)
        """)
        .eq("id", str(requirement_id))
        .eq("firm_id", str(firm_id))
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def create_compliance_requirement(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a compliance requirement"""
    r = sb.table("compliance_requirements").insert(data).execute()
    return r.data[0] if r.data else None


def update_compliance_requirement(sb: Client, requirement_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a compliance requirement"""
    data["updated_at"] = utc_now_iso()
    r = sb.table("compliance_requirements").update(data).eq("id", str(requirement_id)).execute()
    return r.data[0] if r.data else None


def delete_compliance_requirement(sb: Client, requirement_id: uuid.UUID, firm_id: uuid.UUID) -> bool:
    """Delete a compliance requirement (with firm isolation)"""
    r = sb.table("compliance_requirements").delete().eq("id", str(requirement_id)).eq("firm_id", str(firm_id)).execute()
    return bool(r.data)


def count_compliance_requirements(
    sb: Client,
    firm_id: uuid.UUID,
    status: str | None = None,
    client_id: uuid.UUID | None = None,
) -> int:
    """Count compliance requirements with filters"""
    q = sb.table("compliance_requirements").select("id", count="exact").eq("firm_id", str(firm_id))
    
    if status:
        q = q.eq("status", status)
    
    if client_id:
        q = q.eq("client_id", str(client_id))
    
    r = q.execute()
    return int(r.count or 0)


def list_compliance_reminders(
    sb: Client,
    firm_id: uuid.UUID,
    template_id: uuid.UUID | None = None,
    is_active: bool = True,
) -> list[dict[str, Any]]:
    """List compliance reminders"""
    q = sb.table("compliance_reminders").select("*").eq("firm_id", str(firm_id))
    
    if template_id:
        q = q.eq("template_id", str(template_id))
    
    if is_active:
        q = q.eq("is_active", True)
    
    q = q.order("days_before_due", desc=True)
    r = q.execute()
    return r.data or []


def create_compliance_reminder(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a compliance reminder"""
    r = sb.table("compliance_reminders").insert(data).execute()
    return r.data[0] if r.data else None


def list_compliance_alerts(
    sb: Client,
    firm_id: uuid.UUID,
    recipient_id: uuid.UUID | None = None,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List compliance alerts"""
    q = (
        sb.table("compliance_alerts")
        .select("""
            *,
            compliance_requirements!compliance_alerts_requirement_id_fkey(compliance_name, due_date, clients!compliance_requirements_client_id_fkey(company_name)),
            firm_users!compliance_alerts_recipient_id_fkey(full_name)
        """)
        .eq("firm_id", str(firm_id))
    )
    
    if recipient_id:
        q = q.eq("recipient_id", str(recipient_id))
    
    if unread_only:
        q = q.is_("read_at", "null")
    
    q = q.order("sent_at", desc=True).range(offset, offset + limit - 1)
    r = q.execute()
    return r.data or []


def create_compliance_alert(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a compliance alert"""
    r = sb.table("compliance_alerts").insert(data).execute()
    return r.data[0] if r.data else None


def mark_alert_as_read(sb: Client, alert_id: uuid.UUID) -> dict[str, Any] | None:
    """Mark alert as read"""
    r = sb.table("compliance_alerts").update({"read_at": utc_now_iso()}).eq("id", str(alert_id)).execute()
    return r.data[0] if r.data else None


def dismiss_alert(sb: Client, alert_id: uuid.UUID) -> dict[str, Any] | None:
    """Dismiss an alert"""
    r = sb.table("compliance_alerts").update({"dismissed_at": utc_now_iso()}).eq("id", str(alert_id)).execute()
    return r.data[0] if r.data else None


def list_document_requirements(
    sb: Client,
    firm_id: uuid.UUID,
    requirement_id: uuid.UUID,
) -> list[dict[str, Any]]:
    """List document requirements for a compliance requirement"""
    r = (
        sb.table("document_requirements")
        .select("""
            *,
            documents!document_requirements_document_id_fkey(filename, original_filename, uploaded_at),
            firm_users!document_requirements_verified_by_fkey(full_name)
        """)
        .eq("firm_id", str(firm_id))
        .eq("requirement_id", str(requirement_id))
        .order("is_mandatory", desc=True)
        .execute()
    )
    return r.data or []


def create_document_requirement(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a document requirement"""
    r = sb.table("document_requirements").insert(data).execute()
    return r.data[0] if r.data else None


def update_document_requirement(sb: Client, requirement_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a document requirement"""
    r = sb.table("document_requirements").update(data).eq("id", str(requirement_id)).execute()
    return r.data[0] if r.data else None


def count_overdue_compliance(sb: Client, firm_id: uuid.UUID, today: str) -> int:
    """Count overdue compliance requirements"""
    r = (
        sb.table("compliance_requirements")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .lt("due_date", today)
        .neq("status", "completed")
        .neq("status", "not_applicable")
        .execute()
    )
    return int(r.count or 0)


def count_due_soon(sb: Client, firm_id: uuid.UUID, from_date: str, to_date: str) -> int:
    """Count compliance requirements due within date range"""
    r = (
        sb.table("compliance_requirements")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .gte("due_date", from_date)
        .lte("due_date", to_date)
        .neq("status", "completed")
        .neq("status", "not_applicable")
        .execute()
    )
    return int(r.count or 0)


# ============================================================================
# PHASE 3: BILLING & INVOICING REPOSITORY FUNCTIONS
# ============================================================================

def generate_invoice_number(sb: Client, firm_id: uuid.UUID) -> str:
    """Generate next invoice number for firm (INV-2024-0001)"""
    # Get current year
    from datetime import datetime
    year = datetime.now().year
    
    # Count invoices this year for this firm
    r = (
        sb.table("invoices")
        .select("invoice_number", count="exact")
        .eq("firm_id", str(firm_id))
        .like("invoice_number", f"INV-{year}-%")
        .execute()
    )
    count = int(r.count or 0)
    next_num = count + 1
    return f"INV-{year}-{next_num:04d}"


def list_invoices(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List invoices with filters"""
    q = (
        sb.table("invoices")
        .select("*, clients!invoices_client_id_fkey(company_name)")
        .eq("firm_id", str(firm_id))
    )
    
    if client_id:
        q = q.eq("client_id", str(client_id))
    if status:
        q = q.eq("status", status)
    if from_date:
        q = q.gte("invoice_date", from_date)
    if to_date:
        q = q.lte("invoice_date", to_date)
    
    q = q.order("invoice_date", desc=True).range(offset, offset + limit - 1)
    r = q.execute()
    return r.data or []


def invoice_by_id(sb: Client, invoice_id: uuid.UUID, firm_id: uuid.UUID) -> dict[str, Any] | None:
    """Get invoice by ID with firm isolation"""
    r = (
        sb.table("invoices")
        .select("*, clients!invoices_client_id_fkey(company_name, email, country)")
        .eq("id", str(invoice_id))
        .eq("firm_id", str(firm_id))
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def create_invoice(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create an invoice"""
    r = sb.table("invoices").insert(data).execute()
    return r.data[0] if r.data else None


def update_invoice(sb: Client, invoice_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update an invoice"""
    data["updated_at"] = utc_now_iso()
    r = sb.table("invoices").update(data).eq("id", str(invoice_id)).execute()
    return r.data[0] if r.data else None


def list_invoice_items(sb: Client, invoice_id: uuid.UUID) -> list[dict[str, Any]]:
    """Get invoice items"""
    r = (
        sb.table("invoice_items")
        .select("*")
        .eq("invoice_id", str(invoice_id))
        .order("sort_order", desc=False)
        .execute()
    )
    return r.data or []


def create_invoice_item(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create an invoice item"""
    r = sb.table("invoice_items").insert(data).execute()
    return r.data[0] if r.data else None


def list_payments(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: uuid.UUID | None = None,
    invoice_id: uuid.UUID | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List payments"""
    q = (
        sb.table("payments")
        .select("*, clients!payments_client_id_fkey(company_name), invoices!payments_invoice_id_fkey(invoice_number)")
        .eq("firm_id", str(firm_id))
    )
    
    if client_id:
        q = q.eq("client_id", str(client_id))
    if invoice_id:
        q = q.eq("invoice_id", str(invoice_id))
    
    q = q.order("payment_date", desc=True).limit(limit)
    r = q.execute()
    return r.data or []


def create_payment(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a payment record"""
    r = sb.table("payments").insert(data).execute()
    return r.data[0] if r.data else None


def list_timesheet_entries(
    sb: Client,
    firm_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    is_billable: bool | None = None,
    is_invoiced: bool | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    """List timesheet entries"""
    q = (
        sb.table("timesheet_entries")
        .select("""
            *,
            clients!timesheet_entries_client_id_fkey(company_name),
            assignments!timesheet_entries_assignment_id_fkey(assignment_name),
            firm_users!timesheet_entries_user_id_fkey(full_name)
        """)
        .eq("firm_id", str(firm_id))
    )
    
    if user_id:
        q = q.eq("user_id", str(user_id))
    if from_date:
        q = q.gte("entry_date", from_date)
    if to_date:
        q = q.lte("entry_date", to_date)
    if is_billable is not None:
        q = q.eq("is_billable", is_billable)
    if is_invoiced is not None:
        q = q.eq("is_invoiced", is_invoiced)
    
    q = q.order("entry_date", desc=True).limit(limit)
    r = q.execute()
    return r.data or []


def create_timesheet_entry(sb: Client, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a timesheet entry"""
    r = sb.table("timesheet_entries").insert(data).execute()
    return r.data[0] if r.data else None


def get_billing_dashboard_stats(sb: Client, firm_id: uuid.UUID) -> dict[str, Any]:
    """Get billing dashboard statistics"""
    from datetime import date, timedelta
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    
    # Total revenue (all paid invoices)
    r_revenue = (
        sb.table("invoices")
        .select("total_amount", count="exact")
        .eq("firm_id", str(firm_id))
        .eq("status", "paid")
        .execute()
    )
    total_revenue = sum(float(inv.get("total_amount", 0)) for inv in (r_revenue.data or []))
    
    # Revenue this month
    r_month = (
        sb.table("invoices")
        .select("total_amount")
        .eq("firm_id", str(firm_id))
        .gte("paid_at", first_of_month.isoformat())
        .eq("status", "paid")
        .execute()
    )
    revenue_this_month = sum(float(inv.get("total_amount", 0)) for inv in (r_month.data or []))
    
    # Outstanding amount
    r_outstanding = (
        sb.table("invoices")
        .select("balance_due")
        .eq("firm_id", str(firm_id))
        .in_("status", ["sent", "viewed", "partially_paid", "overdue"])
        .execute()
    )
    outstanding = sum(float(inv.get("balance_due", 0)) for inv in (r_outstanding.data or []))
    
    # Overdue
    r_overdue = (
        sb.table("invoices")
        .select("balance_due")
        .eq("firm_id", str(firm_id))
        .eq("status", "overdue")
        .execute()
    )
    overdue = sum(float(inv.get("balance_due", 0)) for inv in (r_overdue.data or []))
    
    return {
        "total_revenue": total_revenue,
        "revenue_this_month": revenue_this_month,
        "outstanding_amount": outstanding,
        "overdue_amount": overdue,
    }


# ============================================================================
# PHASE 4: AUDIT ENGAGEMENT MANAGEMENT
# ============================================================================

def list_audit_engagements(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    financial_year: Optional[str] = None,
    engagement_type: Optional[str] = None,
) -> list[dict]:
    """List audit engagements with filters"""
    query = sb.table("audit_engagements").select("*").eq("firm_id", str(firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    if status:
        query = query.eq("status", status)
    if financial_year:
        query = query.eq("financial_year", financial_year)
    if engagement_type:
        query = query.eq("engagement_type", engagement_type)
    
    query = query.order("created_at", desc=True)
    r = query.execute()
    return r.data or []


def audit_engagement_by_id(sb: Client, engagement_id: uuid.UUID, firm_id: uuid.UUID) -> Optional[dict]:
    """Get audit engagement by ID"""
    r = (
        sb.table("audit_engagements")
        .select("*")
        .eq("id", str(engagement_id))
        .eq("firm_id", str(firm_id))
        .maybe_single()
        .execute()
    )
    return r.data


def create_audit_engagement(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create audit engagement"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("audit_engagements").insert(payload).execute()
    return r.data[0]


def update_audit_engagement(sb: Client, engagement_id: uuid.UUID, firm_id: uuid.UUID, data: dict) -> dict:
    """Update audit engagement"""
    payload = {**data, "updated_at": datetime.utcnow().isoformat()}
    r = (
        sb.table("audit_engagements")
        .update(payload)
        .eq("id", str(engagement_id))
        .eq("firm_id", str(firm_id))
        .execute()
    )
    return r.data[0]


# Working Papers
def list_working_papers(sb: Client, engagement_id: uuid.UUID, firm_id: uuid.UUID) -> list[dict]:
    """List working papers for engagement"""
    r = (
        sb.table("working_papers")
        .select("*")
        .eq("engagement_id", str(engagement_id))
        .eq("firm_id", str(firm_id))
        .order("reference_number")
        .execute()
    )
    return r.data or []


def create_working_paper(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create working paper"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("working_papers").insert(payload).execute()
    return r.data[0]


def update_working_paper(sb: Client, wp_id: uuid.UUID, firm_id: uuid.UUID, data: dict) -> dict:
    """Update working paper"""
    payload = {**data, "updated_at": datetime.utcnow().isoformat()}
    r = (
        sb.table("working_papers")
        .update(payload)
        .eq("id", str(wp_id))
        .eq("firm_id", str(firm_id))
        .execute()
    )
    return r.data[0]


# PBC Checklists
def list_pbc_items(sb: Client, engagement_id: uuid.UUID, firm_id: uuid.UUID) -> list[dict]:
    """List PBC items"""
    r = (
        sb.table("pbc_checklists")
        .select("*")
        .eq("engagement_id", str(engagement_id))
        .eq("firm_id", str(firm_id))
        .order("created_at")
        .execute()
    )
    return r.data or []


def create_pbc_item(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create PBC item"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("pbc_checklists").insert(payload).execute()
    return r.data[0]


def update_pbc_item(sb: Client, pbc_id: uuid.UUID, firm_id: uuid.UUID, data: dict) -> dict:
    """Update PBC item"""
    payload = {**data, "updated_at": datetime.utcnow().isoformat()}
    r = (
        sb.table("pbc_checklists")
        .update(payload)
        .eq("id", str(pbc_id))
        .eq("firm_id", str(firm_id))
        .execute()
    )
    return r.data[0]


# Risk Assessments
def list_risk_assessments(sb: Client, engagement_id: uuid.UUID, firm_id: uuid.UUID) -> list[dict]:
    """List risk assessments"""
    r = (
        sb.table("risk_assessments")
        .select("*")
        .eq("engagement_id", str(engagement_id))
        .eq("firm_id", str(firm_id))
        .order("created_at")
        .execute()
    )
    return r.data or []


def create_risk_assessment(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create risk assessment"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("risk_assessments").insert(payload).execute()
    return r.data[0]


# Review Notes
def list_review_notes(
    sb: Client, 
    engagement_id: uuid.UUID, 
    firm_id: uuid.UUID,
    status: Optional[str] = None
) -> list[dict]:
    """List review notes"""
    query = (
        sb.table("review_notes")
        .select("*")
        .eq("engagement_id", str(engagement_id))
        .eq("firm_id", str(firm_id))
    )
    if status:
        query = query.eq("status", status)
    query = query.order("created_at", desc=True)
    r = query.execute()
    return r.data or []


def create_review_note(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create review note"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("review_notes").insert(payload).execute()
    return r.data[0]


def update_review_note(sb: Client, note_id: uuid.UUID, firm_id: uuid.UUID, data: dict) -> dict:
    """Update review note"""
    payload = {**data, "updated_at": datetime.utcnow().isoformat()}
    r = (
        sb.table("review_notes")
        .update(payload)
        .eq("id", str(note_id))
        .eq("firm_id", str(firm_id))
        .execute()
    )
    return r.data[0]


# Audit Dashboard Stats
def get_audit_dashboard_stats(sb: Client, firm_id: uuid.UUID) -> dict:
    """Get audit dashboard statistics"""
    from collections import Counter
    
    # Get all engagements
    engagements = (
        sb.table("audit_engagements")
        .select("status")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    
    status_counts = Counter(e.get("status") for e in (engagements.data or []))
    active_statuses = ["planning", "fieldwork", "review", "reporting"]
    
    # Working papers
    wps = (
        sb.table("working_papers")
        .select("status")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    wp_counts = Counter(wp.get("status") for wp in (wps.data or []))
    
    # PBC items
    pbc = (
        sb.table("pbc_checklists")
        .select("status")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    pbc_counts = Counter(p.get("status") for p in (pbc.data or []))
    
    # Review notes
    notes = (
        sb.table("review_notes")
        .select("status")
        .eq("firm_id", str(firm_id))
        .eq("status", "open")
        .execute()
    )
    
    # High risk areas
    high_risks = (
        sb.table("risk_assessments")
        .select("id", count="exact")
        .eq("firm_id", str(firm_id))
        .eq("overall_risk", "high")
        .execute()
    )
    
    return {
        "total_engagements": len(engagements.data or []),
        "active_engagements": sum(status_counts[s] for s in active_statuses),
        "planning_phase": status_counts.get("planning", 0),
        "fieldwork_phase": status_counts.get("fieldwork", 0),
        "review_phase": status_counts.get("review", 0),
        "reporting_phase": status_counts.get("reporting", 0),
        "completed": status_counts.get("completed", 0),
        "total_working_papers": len(wps.data or []),
        "draft_papers": wp_counts.get("draft", 0),
        "approved_papers": wp_counts.get("approved", 0),
        "total_pbc_items": len(pbc.data or []),
        "pending_pbc": pbc_counts.get("pending", 0),
        "received_pbc": pbc_counts.get("received", 0),
        "open_review_notes": len(notes.data or []),
        "high_risk_areas": high_risks.count or 0,
    }


# ============================================================================
# PHASE 4: ACCOUNTING WORKBENCH
# ============================================================================

def create_accounting_import(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create accounting import record"""
    payload = {
        **data,
        "firm_id": str(firm_id),
        "created_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("accounting_imports").insert(payload).execute()
    return r.data[0]


def list_trial_balance(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = None,
    period_date: Optional[str] = None,
) -> list[dict]:
    """List trial balance entries"""
    query = sb.table("trial_balance").select("*").eq("firm_id", str(firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    if period_date:
        query = query.eq("period_date", period_date)
    
    query = query.order("account_code")
    r = query.execute()
    return r.data or []


def create_trial_balance_bulk(sb: Client, firm_id: uuid.UUID, entries: list[dict]) -> list[dict]:
    """Bulk insert trial balance entries"""
    payload = [
        {**entry, "firm_id": str(firm_id), "created_at": datetime.utcnow().isoformat()}
        for entry in entries
    ]
    r = sb.table("trial_balance").insert(payload).execute()
    return r.data


def list_ledger_entries(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = None,
    account_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """List ledger entries"""
    query = sb.table("ledger_entries").select("*").eq("firm_id", str(firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    if account_code:
        query = query.eq("account_code", account_code)
    if start_date:
        query = query.gte("entry_date", start_date)
    if end_date:
        query = query.lte("entry_date", end_date)
    
    query = query.order("entry_date", desc=True)
    r = query.execute()
    return r.data or []


def create_bank_reconciliation(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create bank reconciliation"""
    # Calculate adjusted balances
    book_bal = float(data.get("book_balance", 0))
    bank_bal = float(data.get("bank_balance", 0))
    
    cheques = float(data.get("cheques_issued_not_presented", 0))
    deposits = float(data.get("deposits_not_cleared", 0))
    charges = float(data.get("bank_charges", 0))
    interest = float(data.get("interest_credited", 0))
    other = float(data.get("other_adjustments", 0))
    
    adjusted_book = book_bal - charges + interest + other
    adjusted_bank = bank_bal - cheques + deposits
    difference = adjusted_book - adjusted_bank
    
    payload = {
        **data,
        "firm_id": str(firm_id),
        "adjusted_book_balance": adjusted_book,
        "adjusted_bank_balance": adjusted_bank,
        "difference": difference,
        "is_reconciled": abs(difference) < 0.01,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("bank_reconciliation").insert(payload).execute()
    return r.data[0]


def create_gst_reconciliation(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create GST reconciliation"""
    # Calculate variances
    books_total = float(data.get("books_total_gst", 0))
    gstr3b_total = float(data.get("gstr3b_total_gst", 0))
    
    books_sales = float(data.get("books_taxable_sales", 0))
    gstr3b_sales = float(data.get("gstr3b_taxable_sales", 0))
    
    variance_gst = books_total - gstr3b_total
    variance_taxable = books_sales - gstr3b_sales
    
    payload = {
        **data,
        "firm_id": str(firm_id),
        "variance_taxable": variance_taxable,
        "variance_gst": variance_gst,
        "is_reconciled": abs(variance_gst) < 0.01,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("gst_reconciliation").insert(payload).execute()
    return r.data[0]


def create_tds_reconciliation(sb: Client, firm_id: uuid.UUID, data: dict) -> dict:
    """Create TDS reconciliation"""
    books = float(data.get("books_tds_deposited", 0))
    form26as = float(data.get("form26as_tds", 0))
    variance = books - form26as
    
    payload = {
        **data,
        "firm_id": str(firm_id),
        "variance_amount": variance,
        "is_reconciled": abs(variance) < 0.01,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = sb.table("tds_reconciliation").insert(payload).execute()
    return r.data[0]


def get_accounting_dashboard_stats(sb: Client, firm_id: uuid.UUID) -> dict:
    """Get accounting workbench dashboard stats"""
    from collections import Counter
    
    # Imports
    imports = (
        sb.table("accounting_imports")
        .select("status")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    import_counts = Counter(i.get("status") for i in (imports.data or []))
    
    # Trial balance
    tb = (
        sb.table("trial_balance")
        .select("is_reconciled", count="exact")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    unreconciled = sum(1 for e in (tb.data or []) if not e.get("is_reconciled"))
    
    # Bank reco
    banks = (
        sb.table("bank_reconciliation")
        .select("is_reconciled", count="exact")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    unreconciled_banks = sum(1 for b in (banks.data or []) if not b.get("is_reconciled"))
    
    # GST
    gst = (
        sb.table("gst_reconciliation")
        .select("is_reconciled", "variance_gst")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    gst_variances = sum(1 for g in (gst.data or []) if not g.get("is_reconciled"))
    
    # TDS
    tds = (
        sb.table("tds_reconciliation")
        .select("is_reconciled")
        .eq("firm_id", str(firm_id))
        .execute()
    )
    tds_variances = sum(1 for t in (tds.data or []) if not t.get("is_reconciled"))
    
    return {
        "total_imports": len(imports.data or []),
        "pending_imports": import_counts.get("processing", 0),
        "completed_imports": import_counts.get("completed", 0),
        "trial_balance_entries": tb.count or 0,
        "unreconciled_accounts": unreconciled,
        "bank_reconciliations": banks.count or 0,
        "unreconciled_banks": unreconciled_banks,
        "gst_reconciliations": len(gst.data or []),
        "gst_variances": gst_variances,
        "tds_reconciliations": len(tds.data or []),
        "tds_variances": tds_variances,
        "total_variance_amount": 0,  # Could calculate sum of all variances
    }
