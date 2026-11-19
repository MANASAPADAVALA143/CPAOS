"""
GNANOVA CA PRACTICE OS - Automation API Routes
Workflow automation, auto-assignment, templates, and statutory filing
"""

from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.models import FirmUser
from app.services.workflow_engine import workflow_engine
from app.services.assignment_rules import assignment_rules
from app.services.working_paper_templates import wp_templates
from app.services.statutory_filing import statutory_filing, FilingType

router = APIRouter()


# ============================================================================
# AUTO-ASSIGNMENT ENDPOINTS
# ============================================================================

class AutoAssignRequest(BaseModel):
    service_category: str
    priority: str = "medium"
    client_id: Optional[UUID] = None


class AutoAssignReviewerRequest(BaseModel):
    service_category: str
    review_level: str  # manager or partner


class AutoAssignAuditTeamRequest(BaseModel):
    engagement_type: str
    client_size: str = "medium"


@router.post("/auto-assign/staff")
async def auto_assign_staff(
    data: AutoAssignRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Auto-assign staff based on skills and workload"""
    
    result = assignment_rules.auto_assign_staff(
        sb,
        current.firm_id,
        data.service_category,
        data.priority,
        data.client_id,
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="No suitable staff found")
    
    return result


@router.post("/auto-assign/reviewer")
async def auto_assign_reviewer(
    data: AutoAssignReviewerRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Auto-assign reviewer (manager or partner)"""
    
    result = assignment_rules.auto_assign_reviewer(
        sb,
        current.firm_id,
        data.service_category,
        data.review_level,
    )
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No suitable {data.review_level} found")
    
    return result


@router.post("/auto-assign/audit-team")
async def auto_assign_audit_team(
    data: AutoAssignAuditTeamRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Auto-assign audit engagement team"""
    
    team = assignment_rules.auto_assign_audit_team(
        sb,
        current.firm_id,
        data.engagement_type,
        data.client_size,
    )
    
    return {"team": team}


@router.post("/auto-assign/redistribute")
async def redistribute_workload(
    overloaded_threshold: int = 10,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Redistribute workload when staff is overloaded"""
    
    result = assignment_rules.redistribute_workload(
        sb,
        current.firm_id,
        overloaded_threshold,
    )
    
    return result


# ============================================================================
# WORKING PAPER TEMPLATES ENDPOINTS
# ============================================================================

@router.get("/templates/engagement-types")
async def list_engagement_types(
    current: FirmUser = Depends(get_current_user),
):
    """List all available engagement types"""
    return {"engagement_types": wp_templates.get_all_engagement_types()}


@router.get("/templates/{engagement_type}/sections")
async def list_template_sections(
    engagement_type: str,
    current: FirmUser = Depends(get_current_user),
):
    """List sections for an engagement type"""
    sections = wp_templates.get_sections_for_engagement(engagement_type)
    return {"sections": sections}


@router.get("/templates/{engagement_type}/section/{section}")
async def get_section_templates(
    engagement_type: str,
    section: str,
    current: FirmUser = Depends(get_current_user),
):
    """Get templates for a specific section"""
    templates = wp_templates.get_template_by_section(engagement_type, section)
    return {"templates": templates}


@router.post("/templates/{engagement_type}/generate")
async def generate_working_papers(
    engagement_type: str,
    selected_sections: Optional[List[str]] = None,
    current: FirmUser = Depends(get_current_user),
):
    """Generate working papers for an engagement"""
    papers = wp_templates.generate_working_papers_for_engagement(
        engagement_type,
        selected_sections,
    )
    return {"working_papers": papers, "count": len(papers)}


# ============================================================================
# STATUTORY FILING ENDPOINTS
# ============================================================================

class ValidateFilingRequest(BaseModel):
    filing_type: str
    data: dict


class FileReturnRequest(BaseModel):
    filing_type: str
    data: dict
    digital_signature: Optional[str] = None


@router.get("/statutory-filing/types")
async def list_filing_types(
    current: FirmUser = Depends(get_current_user),
):
    """List supported filing types"""
    return {"filing_types": statutory_filing.get_supported_filing_types()}


@router.post("/statutory-filing/validate")
async def validate_filing(
    data: ValidateFilingRequest,
    current: FirmUser = Depends(get_current_user),
):
    """Validate filing data before submission"""
    
    filing_type = FilingType(data.filing_type)
    validation = statutory_filing.validate_filing_data(filing_type, data.data)
    
    return validation


@router.post("/statutory-filing/file")
async def file_return(
    data: FileReturnRequest,
    current: FirmUser = Depends(get_current_user),
):
    """
    File return with government portal
    
    NOTE: This is a MOCK filing for demonstration.
    For production, integrate with actual government APIs.
    """
    
    filing_type = FilingType(data.filing_type)
    result = statutory_filing.file_return(
        filing_type,
        data.data,
        data.digital_signature,
    )
    
    return result


@router.get("/statutory-filing/status/{acknowledgment_number}")
async def check_filing_status(
    acknowledgment_number: str,
    filing_type: str,
    current: FirmUser = Depends(get_current_user),
):
    """
    Check status of filed return
    
    NOTE: This is a MOCK status check.
    For production, query actual government portal.
    """
    
    filing_type_enum = FilingType(filing_type)
    status = statutory_filing.check_filing_status(
        filing_type_enum,
        acknowledgment_number,
    )
    
    return status


@router.get("/statutory-filing/prefill")
async def get_prefill_data(
    filing_type: str,
    identifier: str,
    period: str,
    current: FirmUser = Depends(get_current_user),
):
    """
    Get pre-filled return data from portal
    
    NOTE: This returns MOCK data.
    For production, fetch actual data from government portal.
    """
    
    filing_type_enum = FilingType(filing_type)
    data = statutory_filing.get_return_prefill_data(
        filing_type_enum,
        identifier,
        period,
    )
    
    return data


@router.post("/statutory-filing/reconcile")
async def reconcile_with_portal(
    filing_type: str,
    identifier: str,
    period: str,
    our_data: dict,
    current: FirmUser = Depends(get_current_user),
):
    """
    Reconcile our data with portal data
    
    NOTE: This is a MOCK reconciliation.
    For production, compare with actual portal data.
    """
    
    filing_type_enum = FilingType(filing_type)
    reconciliation = statutory_filing.reconcile_with_portal(
        filing_type_enum,
        identifier,
        period,
        our_data,
    )
    
    return reconciliation


# ============================================================================
# WORKFLOW TRIGGER ENDPOINTS (Manual triggers for testing)
# ============================================================================

@router.post("/workflow/test/daily-checks")
async def run_daily_checks(
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Manually trigger daily workflow checks (for testing)"""
    
    results = workflow_engine.run_daily_workflow_checks(sb, current.firm_id)
    
    return {
        "message": "Daily workflow checks completed",
        "results": results,
    }
