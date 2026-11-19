"""
GNANOVA CA PRACTICE OS - Audit Engagement API Routes
Phase 4: Audit engagements, working papers, PBC, risk assessment, review notes
"""

from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.models import FirmUser
from app.db import repo

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AuditEngagementCreate(BaseModel):
    client_id: UUID
    engagement_name: str
    engagement_type: str
    financial_year: str
    period_start: date
    period_end: date
    engagement_partner: Optional[UUID] = None
    audit_manager: Optional[UUID] = None
    audit_senior: Optional[UUID] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    budgeted_hours: Optional[float] = None
    materiality_amount: Optional[float] = None


class AuditEngagementUpdate(BaseModel):
    engagement_name: Optional[str] = None
    status: Optional[str] = None
    engagement_partner: Optional[UUID] = None
    audit_manager: Optional[UUID] = None
    audit_senior: Optional[UUID] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    report_date: Optional[date] = None
    overall_risk_rating: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    notes: Optional[str] = None


class WorkingPaperCreate(BaseModel):
    engagement_id: UUID
    reference_number: str
    title: str
    section: Optional[str] = None
    description: Optional[str] = None


class WorkingPaperUpdate(BaseModel):
    procedure_performed: Optional[str] = None
    findings: Optional[str] = None
    conclusion: Optional[str] = None
    status: Optional[str] = None
    prepared_date: Optional[date] = None
    reviewed_date: Optional[date] = None
    approved_date: Optional[date] = None


class PBCItemCreate(BaseModel):
    engagement_id: UUID
    item_name: str
    item_category: Optional[str] = None
    description: Optional[str] = None
    is_mandatory: bool = True
    due_date: Optional[date] = None


class PBCItemUpdate(BaseModel):
    status: Optional[str] = None
    received_date: Optional[date] = None
    document_id: Optional[UUID] = None
    notes: Optional[str] = None


class RiskAssessmentCreate(BaseModel):
    engagement_id: UUID
    risk_area: str
    risk_description: str
    inherent_risk: Optional[str] = None
    control_risk: Optional[str] = None
    detection_risk: Optional[str] = None
    overall_risk: Optional[str] = None
    controls_identified: Optional[str] = None
    audit_procedures: Optional[str] = None


class ReviewNoteCreate(BaseModel):
    engagement_id: UUID
    working_paper_id: Optional[UUID] = None
    note_type: str = "review_point"
    note_text: str
    assigned_to: Optional[UUID] = None
    raised_date: date


class ReviewNoteUpdate(BaseModel):
    status: Optional[str] = None
    response_text: Optional[str] = None
    responded_date: Optional[date] = None


# ============================================================================
# AUDIT ENGAGEMENT ENDPOINTS
# ============================================================================

@router.get("/engagements")
async def list_engagements(
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
    financial_year: Optional[str] = None,
    engagement_type: Optional[str] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List audit engagements with filters"""
    engagements = repo.list_audit_engagements(
        sb, current.firm_id, client_id, status, financial_year, engagement_type
    )
    return {"engagements": engagements}


@router.post("/engagements")
async def create_engagement(
    data: AuditEngagementCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create audit engagement"""
    # Generate engagement code
    from datetime import datetime
    year = datetime.now().year
    
    # Count existing engagements this year
    existing = repo.list_audit_engagements(sb, current.firm_id)
    year_count = sum(1 for e in existing if str(year) in e.get("engagement_code", ""))
    next_num = year_count + 1
    
    engagement_code = f"AUD-{year}-{next_num:04d}"
    
    payload = {
        **data.model_dump(),
        "engagement_code": engagement_code,
        "created_by": str(current.id),
        "status": "planning",
    }
    
    engagement = repo.create_audit_engagement(sb, current.firm_id, payload)
    return {"engagement": engagement}


@router.get("/engagements/{engagement_id}")
async def get_engagement(
    engagement_id: UUID,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Get audit engagement by ID"""
    engagement = repo.audit_engagement_by_id(sb, engagement_id, current.firm_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return {"engagement": engagement}


@router.put("/engagements/{engagement_id}")
async def update_engagement(
    engagement_id: UUID,
    data: AuditEngagementUpdate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Update audit engagement"""
    engagement = repo.audit_engagement_by_id(sb, engagement_id, current.firm_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = repo.update_audit_engagement(sb, engagement_id, current.firm_id, payload)
    return {"engagement": updated}


@router.get("/engagements/dashboard/stats")
async def get_dashboard_stats(
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Get audit dashboard statistics"""
    stats = repo.get_audit_dashboard_stats(sb, current.firm_id)
    return stats


# ============================================================================
# WORKING PAPERS ENDPOINTS
# ============================================================================

@router.get("/engagements/{engagement_id}/working-papers")
async def list_working_papers(
    engagement_id: UUID,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List working papers for engagement"""
    papers = repo.list_working_papers(sb, engagement_id, current.firm_id)
    return {"working_papers": papers}


@router.post("/working-papers")
async def create_working_paper(
    data: WorkingPaperCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create working paper"""
    payload = {
        **data.model_dump(),
        "prepared_by": str(current.id),
        "status": "draft",
    }
    paper = repo.create_working_paper(sb, current.firm_id, payload)
    return {"working_paper": paper}


@router.put("/working-papers/{wp_id}")
async def update_working_paper(
    wp_id: UUID,
    data: WorkingPaperUpdate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Update working paper"""
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # Set reviewer/approver based on status change
    if data.status == "review":
        payload["reviewed_by"] = str(current.id)
    elif data.status == "approved":
        payload["approved_by"] = str(current.id)
    
    paper = repo.update_working_paper(sb, wp_id, current.firm_id, payload)
    return {"working_paper": paper}


# ============================================================================
# PBC CHECKLIST ENDPOINTS
# ============================================================================

@router.get("/engagements/{engagement_id}/pbc-items")
async def list_pbc_items(
    engagement_id: UUID,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List PBC items"""
    items = repo.list_pbc_items(sb, engagement_id, current.firm_id)
    return {"pbc_items": items}


@router.post("/pbc-items")
async def create_pbc_item(
    data: PBCItemCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create PBC item"""
    from datetime import datetime
    payload = {
        **data.model_dump(),
        "requested_date": datetime.now().date().isoformat(),
        "status": "pending",
    }
    item = repo.create_pbc_item(sb, current.firm_id, payload)
    return {"pbc_item": item}


@router.put("/pbc-items/{pbc_id}")
async def update_pbc_item(
    pbc_id: UUID,
    data: PBCItemUpdate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Update PBC item"""
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if data.status == "reviewed":
        payload["reviewed_by"] = str(current.id)
        from datetime import datetime
        payload["reviewed_date"] = datetime.now().date().isoformat()
    
    item = repo.update_pbc_item(sb, pbc_id, current.firm_id, payload)
    return {"pbc_item": item}


# ============================================================================
# RISK ASSESSMENT ENDPOINTS
# ============================================================================

@router.get("/engagements/{engagement_id}/risk-assessments")
async def list_risk_assessments(
    engagement_id: UUID,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List risk assessments"""
    risks = repo.list_risk_assessments(sb, engagement_id, current.firm_id)
    return {"risk_assessments": risks}


@router.post("/risk-assessments")
async def create_risk_assessment(
    data: RiskAssessmentCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create risk assessment"""
    from datetime import datetime
    payload = {
        **data.model_dump(),
        "assessed_by": str(current.id),
        "assessed_date": datetime.now().date().isoformat(),
    }
    risk = repo.create_risk_assessment(sb, current.firm_id, payload)
    return {"risk_assessment": risk}


# ============================================================================
# REVIEW NOTES ENDPOINTS
# ============================================================================

@router.get("/engagements/{engagement_id}/review-notes")
async def list_review_notes(
    engagement_id: UUID,
    status: Optional[str] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List review notes"""
    notes = repo.list_review_notes(sb, engagement_id, current.firm_id, status)
    return {"review_notes": notes}


@router.post("/review-notes")
async def create_review_note(
    data: ReviewNoteCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create review note"""
    payload = {
        **data.model_dump(),
        "raised_by": str(current.id),
        "status": "open",
    }
    note = repo.create_review_note(sb, current.firm_id, payload)
    return {"review_note": note}


@router.put("/review-notes/{note_id}")
async def update_review_note(
    note_id: UUID,
    data: ReviewNoteUpdate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Update review note (respond or clear)"""
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if data.response_text:
        payload["responded_by"] = str(current.id)
    
    if data.status == "cleared":
        payload["cleared_by"] = str(current.id)
        from datetime import datetime
        payload["cleared_date"] = datetime.now().date().isoformat()
    
    note = repo.update_review_note(sb, note_id, current.firm_id, payload)
    return {"review_note": note}
