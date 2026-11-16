"""Assignment service - business logic for assignment management"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from supabase import Client

from app.db import repo
from app.db.dates import utc_now_iso


def generate_assignment_code(sb: Client, firm_id: uuid.UUID) -> str:
    """
    Generate unique assignment code for firm
    Format: ASG-YYYY-NNNN (e.g., ASG-2024-0001)
    """
    year = datetime.now().year
    
    # Get count of assignments this year for this firm
    # Note: This is a simple implementation. For high-volume firms,
    # consider using a dedicated sequence or atomic counter.
    
    # Query assignments for this firm and year
    q = sb.table("assignments").select("assignment_code", count="exact").eq("firm_id", str(firm_id)).ilike("assignment_code", f"ASG-{year}-%")
    r = q.execute()
    
    count = int(r.count or 0)
    next_num = count + 1
    
    return f"ASG-{year}-{next_num:04d}"


def calculate_assignment_completion(sb: Client, assignment_id: uuid.UUID) -> int:
    """
    Calculate assignment completion percentage
    Based on checklist items if they exist, otherwise status-based
    """
    # Get checklist items for this assignment
    items = repo.checklist_items_for_assignment(sb, assignment_id)
    
    if not items:
        # No checklist, use status-based completion
        assignment = repo.assignment_by_id(sb, assignment_id)
        if not assignment:
            return 0
        
        status = assignment.get("status", "created")
        status_pct = {
            "created": 0,
            "assigned": 10,
            "in_progress": 30,
            "submitted": 60,
            "manager_review": 70,
            "partner_review": 80,
            "approved": 90,
            "completed": 100,
        }
        return status_pct.get(status, 0)
    
    # Calculate based on checklist
    total = len(items)
    completed = sum(1 for item in items if item.get("status") in ["verified", "waived"])
    
    return int((completed / total) * 100) if total > 0 else 0


def get_overdue_assignments(sb: Client, firm_id: uuid.UUID, limit: int = 10) -> list[dict]:
    """Get list of overdue assignments"""
    return repo.list_assignments_filtered(sb, firm_id, overdue_only=True)[:limit]


def get_staff_workload_summary(sb: Client, firm_id: uuid.UUID) -> list[dict]:
    """
    Get staff workload summary with names
    Returns list of staff with their assignment counts and hours
    """
    # Get workload data
    workload = repo.get_staff_workload(sb, firm_id)
    
    # Get staff details
    staff_map = {str(user["id"]): user for user in repo.firm_users_for_firm(sb, firm_id)}
    
    # Combine data
    result = []
    for w in workload:
        staff_id = w["staff_id"]
        staff = staff_map.get(staff_id, {})
        
        result.append({
            "staff_id": staff_id,
            "staff_name": staff.get("full_name", "Unknown"),
            "designation": staff.get("designation", ""),
            "department": staff.get("department", ""),
            "assignments_count": w["assignments_count"],
            "estimated_hours": w["estimated_hours"],
            "actual_hours": w["actual_hours"],
            "utilization_pct": int((w["actual_hours"] / w["estimated_hours"]) * 100) if w["estimated_hours"] > 0 else 0,
        })
    
    return sorted(result, key=lambda x: x["assignments_count"], reverse=True)


def can_submit_for_review(sb: Client, assignment_id: uuid.UUID) -> tuple[bool, str]:
    """
    Check if assignment can be submitted for review
    Returns (can_submit, reason)
    """
    assignment = repo.assignment_by_id(sb, assignment_id)
    if not assignment:
        return False, "Assignment not found"
    
    status = assignment.get("status")
    if status in ["submitted", "manager_review", "partner_review", "approved", "completed"]:
        return False, f"Assignment already submitted (status: {status})"
    
    # Optional: Check if documents are uploaded
    # For now, allow submission without strict validation
    
    return True, "OK"


def submit_assignment_for_review(
    sb: Client,
    assignment_id: uuid.UUID,
    submitted_by: uuid.UUID,
) -> dict:
    """
    Submit assignment for manager review
    Creates review record and updates assignment status
    """
    assignment = repo.assignment_by_id(sb, assignment_id)
    if not assignment:
        raise ValueError("Assignment not found")
    
    # Determine reviewer (manager or partner if no manager)
    reviewer_id = assignment.get("assigned_manager") or assignment.get("assigned_partner")
    if not reviewer_id:
        raise ValueError("No manager or partner assigned to review this assignment")
    
    # Update assignment status
    repo.update_assignment(sb, assignment_id, {"status": "manager_review"})
    
    # Create review record
    review_data = {
        "assignment_id": str(assignment_id),
        "reviewer_id": str(reviewer_id),
        "review_level": "manager",
        "submitted_at": utc_now_iso(),
        "status": "pending",
    }
    review = repo.create_assignment_review(sb, review_data)
    
    # Log activity
    repo.insert_activity(
        sb,
        client_id=uuid.UUID(assignment["client_id"]),
        firm_id=uuid.UUID(assignment["firm_id"]),
        action="assignment_submitted",
        description=f"Assignment '{assignment['assignment_name']}' submitted for review",
        performed_by=str(submitted_by),
    )
    
    return review


def review_assignment(
    sb: Client,
    review_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    action: str,  # approve, reject, changes_requested
    comments: str | None = None,
) -> dict:
    """
    Review an assignment (manager or partner)
    """
    # Get review record
    review = sb.table("assignment_reviews").select("*").eq("id", str(review_id)).limit(1).execute()
    if not review.data:
        raise ValueError("Review not found")
    
    review_data = review.data[0]
    assignment_id = uuid.UUID(review_data["assignment_id"])
    review_level = review_data["review_level"]
    
    # Get assignment
    assignment = repo.assignment_by_id(sb, assignment_id)
    if not assignment:
        raise ValueError("Assignment not found")
    
    # Update review record
    review_updates = {
        "reviewed_at": utc_now_iso(),
        "status": action,
        "comments": comments,
    }
    repo.update_assignment_review(sb, review_id, review_updates)
    
    # Update assignment based on action
    if action == "approved":
        if review_level == "manager":
            # Manager approved, send to partner
            partner_id = assignment.get("assigned_partner")
            if partner_id:
                # Create partner review
                partner_review_data = {
                    "assignment_id": str(assignment_id),
                    "reviewer_id": str(partner_id),
                    "review_level": "partner",
                    "submitted_at": utc_now_iso(),
                    "status": "pending",
                }
                repo.create_assignment_review(sb, partner_review_data)
                repo.update_assignment(sb, assignment_id, {"status": "partner_review"})
            else:
                # No partner, mark as approved
                repo.update_assignment(sb, assignment_id, {
                    "status": "approved",
                    "completed_date": date.today().isoformat(),
                })
        else:  # partner review
            # Partner approved, mark as completed
            repo.update_assignment(sb, assignment_id, {
                "status": "completed",
                "completed_date": date.today().isoformat(),
                "completion_pct": 100,
            })
    
    elif action == "rejected":
        # Send back to in_progress
        repo.update_assignment(sb, assignment_id, {"status": "in_progress"})
    
    elif action == "changes_requested":
        # Send back to in_progress
        repo.update_assignment(sb, assignment_id, {"status": "in_progress"})
    
    # Log activity
    repo.insert_activity(
        sb,
        client_id=uuid.UUID(assignment["client_id"]),
        firm_id=uuid.UUID(assignment["firm_id"]),
        action=f"assignment_{action}",
        description=f"Assignment '{assignment['assignment_name']}' {action} by {review_level}",
        performed_by=str(reviewer_id),
    )
    
    return review_data


# Helper function to check if table exists (for backward compatibility)
def checklist_items_for_assignment(sb: Client, assignment_id: uuid.UUID) -> list[dict]:
    """Get checklist items for an assignment"""
    try:
        r = sb.table("checklist_items").select("*").eq("assignment_id", str(assignment_id)).execute()
        return r.data or []
    except Exception:
        # Table might not have assignment_id column yet
        return []


# Add to repo for convenience
repo.checklist_items_for_assignment = checklist_items_for_assignment
