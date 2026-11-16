"""Assignment management API routes"""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db, repo
from app.models.enums import AssignmentPriority, AssignmentStatus, FirmUserRole
from app.models.staff import FirmUser
from app.services import assignment_service

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CreateAssignmentBody(BaseModel):
    client_id: uuid.UUID
    assignment_name: str
    service_category: str
    assignment_type: str
    financial_year: str
    period_start: date | None = None
    period_end: date | None = None
    assigned_partner: uuid.UUID | None = None
    assigned_manager: uuid.UUID | None = None
    assigned_staff: uuid.UUID | None = None
    start_date: date | None = None
    due_date: date
    priority: str = "medium"
    estimated_hours: float | None = None
    description: str | None = None


class UpdateAssignmentBody(BaseModel):
    assignment_name: str | None = None
    status: str | None = None
    assigned_partner: uuid.UUID | None = None
    assigned_manager: uuid.UUID | None = None
    assigned_staff: uuid.UUID | None = None
    due_date: date | None = None
    priority: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    description: str | None = None
    internal_notes: str | None = None


class ReviewAssignmentBody(BaseModel):
    action: str  # approve, reject, changes_requested
    comments: str | None = None


# ============================================================================
# ASSIGNMENT CRUD
# ============================================================================


@router.post("/assignments")
def create_assignment(
    body: CreateAssignmentBody,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create new assignment"""
    # Verify client belongs to firm
    client = repo.client_by_id(sb, body.client_id, current.firm_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate assignment code
    assignment_code = assignment_service.generate_assignment_code(sb, current.firm_id)
    
    # Create assignment
    assignment_data = {
        "firm_id": str(current.firm_id),
        "client_id": str(body.client_id),
        "assignment_code": assignment_code,
        "assignment_name": body.assignment_name,
        "service_category": body.service_category,
        "assignment_type": body.assignment_type,
        "financial_year": body.financial_year,
        "period_start": body.period_start.isoformat() if body.period_start else None,
        "period_end": body.period_end.isoformat() if body.period_end else None,
        "assigned_partner": str(body.assigned_partner) if body.assigned_partner else None,
        "assigned_manager": str(body.assigned_manager) if body.assigned_manager else None,
        "assigned_staff": str(body.assigned_staff) if body.assigned_staff else None,
        "start_date": body.start_date.isoformat() if body.start_date else None,
        "due_date": body.due_date.isoformat(),
        "priority": body.priority,
        "status": AssignmentStatus.created.value,
        "estimated_hours": body.estimated_hours,
        "description": body.description,
        "created_by": str(current.id),
    }
    
    assignment = repo.create_assignment(sb, assignment_data)
    
    # Log activity
    repo.insert_activity(
        sb,
        client_id=body.client_id,
        firm_id=current.firm_id,
        action="assignment_created",
        description=f"Assignment '{body.assignment_name}' created",
        performed_by=str(current.id),
    )
    
    return {
        "id": assignment["id"],
        "assignment_code": assignment["assignment_code"],
        "assignment_name": assignment["assignment_name"],
        "status": assignment["status"],
    }


@router.get("/assignments")
def list_assignments(
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    assigned_partner: uuid.UUID | None = None,
    assigned_manager: uuid.UUID | None = None,
    assigned_staff: uuid.UUID | None = None,
    service_category: str | None = None,
    search: str | None = None,
    overdue_only: bool = False,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List assignments with filters"""
    assignments = repo.list_assignments_filtered(
        sb,
        current.firm_id,
        client_id=client_id,
        status=status,
        assigned_partner=assigned_partner,
        assigned_manager=assigned_manager,
        assigned_staff=assigned_staff,
        service_category=service_category,
        search=search,
        overdue_only=overdue_only,
    )
    
    # Get staff names
    staff_map = {str(u["id"]): u["full_name"] for u in repo.firm_users_for_firm(sb, current.firm_id)}
    
    return [
        {
            "id": a["id"],
            "assignment_code": a["assignment_code"],
            "assignment_name": a["assignment_name"],
            "client_id": a["client_id"],
            "client_name": a.get("clients", {}).get("client_name", ""),
            "service_category": a["service_category"],
            "assignment_type": a["assignment_type"],
            "financial_year": a["financial_year"],
            "due_date": a["due_date"],
            "completed_date": a.get("completed_date"),
            "priority": a["priority"],
            "status": a["status"],
            "completion_pct": a.get("completion_pct", 0),
            "assigned_partner": a.get("assigned_partner"),
            "assigned_partner_name": staff_map.get(a.get("assigned_partner", ""), ""),
            "assigned_manager": a.get("assigned_manager"),
            "assigned_manager_name": staff_map.get(a.get("assigned_manager", ""), ""),
            "assigned_staff": a.get("assigned_staff"),
            "assigned_staff_name": staff_map.get(a.get("assigned_staff", ""), ""),
            "created_at": a.get("created_at"),
        }
        for a in assignments
    ]


@router.get("/assignments/{assignment_id}")
def get_assignment(
    assignment_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get assignment details"""
    assignment = repo.assignment_by_id(sb, assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get client
    client = repo.client_by_id(sb, uuid.UUID(assignment["client_id"]))
    
    # Get staff names
    staff_map = {str(u["id"]): u["full_name"] for u in repo.firm_users_for_firm(sb, current.firm_id)}
    
    return {
        "id": assignment["id"],
        "assignment_code": assignment["assignment_code"],
        "assignment_name": assignment["assignment_name"],
        "client_id": assignment["client_id"],
        "client_name": client.get("client_name", "") if client else "",
        "service_category": assignment["service_category"],
        "assignment_type": assignment["assignment_type"],
        "financial_year": assignment["financial_year"],
        "period_start": assignment.get("period_start"),
        "period_end": assignment.get("period_end"),
        "start_date": assignment.get("start_date"),
        "due_date": assignment["due_date"],
        "completed_date": assignment.get("completed_date"),
        "priority": assignment["priority"],
        "status": assignment["status"],
        "completion_pct": assignment.get("completion_pct", 0),
        "estimated_hours": assignment.get("estimated_hours"),
        "actual_hours": assignment.get("actual_hours"),
        "description": assignment.get("description"),
        "internal_notes": assignment.get("internal_notes"),
        "assigned_partner": assignment.get("assigned_partner"),
        "assigned_partner_name": staff_map.get(assignment.get("assigned_partner", ""), ""),
        "assigned_manager": assignment.get("assigned_manager"),
        "assigned_manager_name": staff_map.get(assignment.get("assigned_manager", ""), ""),
        "assigned_staff": assignment.get("assigned_staff"),
        "assigned_staff_name": staff_map.get(assignment.get("assigned_staff", ""), ""),
        "created_at": assignment.get("created_at"),
        "updated_at": assignment.get("updated_at"),
    }


@router.patch("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: uuid.UUID,
    body: UpdateAssignmentBody,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Update assignment"""
    assignment = repo.assignment_by_id(sb, assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Build updates
    updates = {}
    if body.assignment_name is not None:
        updates["assignment_name"] = body.assignment_name
    if body.status is not None:
        updates["status"] = body.status
    if body.assigned_partner is not None:
        updates["assigned_partner"] = str(body.assigned_partner) if body.assigned_partner else None
    if body.assigned_manager is not None:
        updates["assigned_manager"] = str(body.assigned_manager) if body.assigned_manager else None
    if body.assigned_staff is not None:
        updates["assigned_staff"] = str(body.assigned_staff) if body.assigned_staff else None
    if body.due_date is not None:
        updates["due_date"] = body.due_date.isoformat()
    if body.priority is not None:
        updates["priority"] = body.priority
    if body.estimated_hours is not None:
        updates["estimated_hours"] = body.estimated_hours
    if body.actual_hours is not None:
        updates["actual_hours"] = body.actual_hours
    if body.description is not None:
        updates["description"] = body.description
    if body.internal_notes is not None:
        updates["internal_notes"] = body.internal_notes
    
    if updates:
        repo.update_assignment(sb, assignment_id, updates)
        
        # Log activity
        repo.insert_activity(
            sb,
            client_id=uuid.UUID(assignment["client_id"]),
            firm_id=current.firm_id,
            action="assignment_updated",
            description=f"Assignment '{assignment['assignment_name']}' updated",
            performed_by=str(current.id),
        )
    
    return {"ok": True}


@router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Delete assignment (owner/admin only)"""
    if current.role not in (FirmUserRole.owner, FirmUserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to delete assignments")
    
    assignment = repo.assignment_by_id(sb, assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    repo.delete_assignment(sb, assignment_id, current.firm_id)
    
    # Log activity
    repo.insert_activity(
        sb,
        client_id=uuid.UUID(assignment["client_id"]),
        firm_id=current.firm_id,
        action="assignment_deleted",
        description=f"Assignment '{assignment['assignment_name']}' deleted",
        performed_by=str(current.id),
    )
    
    return {"ok": True}


# ============================================================================
# ASSIGNMENT WORKFLOW
# ============================================================================


@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(
    assignment_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Submit assignment for review"""
    assignment = repo.assignment_by_id(sb, assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if can submit
    can_submit, reason = assignment_service.can_submit_for_review(sb, assignment_id)
    if not can_submit:
        raise HTTPException(status_code=400, detail=reason)
    
    # Submit for review
    try:
        review = assignment_service.submit_assignment_for_review(sb, assignment_id, current.id)
        return {
            "ok": True,
            "review_id": str(review["id"]),
            "reviewer_id": review["reviewer_id"],
            "status": "submitted",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assignments/{assignment_id}/review")
def review_assignment_endpoint(
    assignment_id: uuid.UUID,
    body: ReviewAssignmentBody,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Review assignment (approve/reject/request changes)"""
    # Get pending review for this assignment and current user
    reviews = repo.get_assignment_reviews(sb, assignment_id)
    
    # Find pending review for current user
    pending_review = None
    for r in reviews:
        if r.get("reviewer_id") == str(current.id) and r.get("status") == "pending":
            pending_review = r
            break
    
    if not pending_review:
        raise HTTPException(status_code=404, detail="No pending review found for this user")
    
    # Validate action
    if body.action not in ["approved", "rejected", "changes_requested"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Perform review
    try:
        assignment_service.review_assignment(
            sb,
            uuid.UUID(pending_review["id"]),
            current.id,
            body.action,
            body.comments,
        )
        return {"ok": True, "action": body.action}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assignments/{assignment_id}/reviews")
def get_assignment_reviews_endpoint(
    assignment_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get review history for assignment"""
    assignment = repo.assignment_by_id(sb, assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    reviews = repo.get_assignment_reviews(sb, assignment_id)
    
    return [
        {
            "id": r["id"],
            "review_level": r["review_level"],
            "reviewer_name": r.get("firm_users", {}).get("full_name", ""),
            "submitted_at": r["submitted_at"],
            "reviewed_at": r.get("reviewed_at"),
            "status": r["status"],
            "comments": r.get("comments"),
            "rejection_reason": r.get("rejection_reason"),
        }
        for r in reviews
    ]


# ============================================================================
# MY TASKS & REVIEW QUEUE
# ============================================================================


@router.get("/assignments/my/tasks")
def my_tasks(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get current user's assigned tasks"""
    assignments = repo.list_assignments_filtered(
        sb,
        current.firm_id,
        assigned_staff=current.id,
    )
    
    # Get client names
    client_map = {str(c["id"]): c["client_name"] for c in repo.all_clients_firm(sb, current.firm_id)}
    
    return [
        {
            "id": a["id"],
            "assignment_code": a["assignment_code"],
            "assignment_name": a["assignment_name"],
            "client_name": client_map.get(a["client_id"], ""),
            "due_date": a["due_date"],
            "priority": a["priority"],
            "status": a["status"],
            "completion_pct": a.get("completion_pct", 0),
        }
        for a in assignments
    ]


@router.get("/assignments/review-queue")
def review_queue(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get assignments pending current user's review"""
    # Determine review level based on role
    review_level = None
    if current.role == FirmUserRole.owner:
        review_level = "partner"
    
    reviews = repo.get_pending_reviews(sb, current.firm_id, current.id, review_level)
    
    return [
        {
            "review_id": r["id"],
            "assignment_id": r["assignment_id"],
            "assignment_name": r.get("assignments", {}).get("assignment_name", ""),
            "assignment_code": r.get("assignments", {}).get("assignment_code", ""),
            "client_name": r.get("assignments", {}).get("clients", {}).get("client_name", ""),
            "due_date": r.get("assignments", {}).get("due_date"),
            "review_level": r["review_level"],
            "submitted_at": r["submitted_at"],
        }
        for r in reviews
    ]
