"""
Compliance calendar API routes for GNANOVA CA Practice OS
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db, repo
from app.models.staff import FirmUser
from app.services import compliance_service

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ComplianceTemplateCreate(BaseModel):
    country: str = Field(..., min_length=2, max_length=10)
    service_category: str
    compliance_name: str
    compliance_code: Optional[str] = None
    description: Optional[str] = None
    frequency: str
    due_day_of_month: Optional[int] = None
    due_month: Optional[int] = None
    due_days_after_period_end: Optional[int] = None
    applies_to_entity_types: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    auto_create_assignment: bool = True
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    penalty_info: Optional[str] = None


class ComplianceTemplateUpdate(BaseModel):
    compliance_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[str] = None
    estimated_hours: Optional[float] = None


class ComplianceRequirementCreate(BaseModel):
    client_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    compliance_name: str
    service_category: str
    financial_year: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    due_date: date
    priority: str = "medium"
    assigned_to: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class ComplianceRequirementUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    completion_date: Optional[date] = None
    notes: Optional[str] = None
    is_enabled: Optional[bool] = None


class GenerateComplianceRequest(BaseModel):
    client_id: uuid.UUID
    financial_year: str


class ComplianceReminderCreate(BaseModel):
    template_id: Optional[uuid.UUID] = None
    reminder_name: str
    days_before_due: int
    reminder_type: str
    escalate_to_role: Optional[str] = None
    message_template: Optional[str] = None


class LinkToAssignmentRequest(BaseModel):
    assignment_id: uuid.UUID


# ============================================================================
# COMPLIANCE TEMPLATES
# ============================================================================

@router.get("/templates")
async def list_templates(
    country: Optional[str] = None,
    service_category: Optional[str] = None,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List compliance templates (system + firm-specific)"""
    templates = repo.list_compliance_templates(
        sb,
        firm_id=current.firm_id,
        country=country,
        service_category=service_category,
        is_active=True,
    )
    return templates


@router.get("/templates/{template_id}")
async def get_template(
    template_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get compliance template by ID"""
    template = repo.compliance_template_by_id(sb, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates")
async def create_template(
    data: ComplianceTemplateCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create a firm-specific compliance template"""
    # Only admin/owner can create templates
    if current.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    template_data = data.model_dump()
    template_data["firm_id"] = str(current.firm_id)
    template_data["is_system_template"] = False
    template_data["is_active"] = True
    
    template = repo.create_compliance_template(sb, template_data)
    if not template:
        raise HTTPException(status_code=500, detail="Failed to create template")
    
    return template


@router.patch("/templates/{template_id}")
async def update_template(
    template_id: uuid.UUID,
    data: ComplianceTemplateUpdate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Update a firm-specific compliance template"""
    if current.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    template = repo.compliance_template_by_id(sb, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Can only update firm-specific templates
    if template.get("firm_id") != str(current.firm_id):
        raise HTTPException(status_code=403, detail="Cannot update system templates")
    
    update_data = data.model_dump(exclude_unset=True)
    updated = repo.update_compliance_template(sb, template_id, update_data)
    
    return updated


# ============================================================================
# COMPLIANCE REQUIREMENTS
# ============================================================================

@router.get("/requirements")
async def list_requirements(
    client_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    service_category: Optional[str] = None,
    financial_year: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List compliance requirements with filters"""
    requirements = repo.list_compliance_requirements(
        sb,
        firm_id=current.firm_id,
        client_id=client_id,
        status=status,
        service_category=service_category,
        financial_year=financial_year,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    
    # Enrich with calculated fields
    today = date.today()
    for req in requirements:
        due_date_str = req["due_date"]
        due_date_obj = date.fromisoformat(due_date_str)
        req["days_until_due"] = (due_date_obj - today).days
        req["is_overdue"] = due_date_obj < today and req["status"] not in ["completed", "not_applicable"]
        
        # Flatten nested objects
        if req.get("clients"):
            req["client_name"] = req["clients"].get("company_name")
        if req.get("firm_users"):
            req["assigned_to_name"] = req["firm_users"].get("full_name")
        if req.get("compliance_templates"):
            req["template_code"] = req["compliance_templates"].get("compliance_code")
    
    return requirements


@router.get("/requirements/{requirement_id}")
async def get_requirement(
    requirement_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get compliance requirement by ID"""
    requirement = repo.compliance_requirement_by_id(sb, requirement_id, current.firm_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Get document requirements
    doc_requirements = repo.list_document_requirements(
        sb,
        firm_id=current.firm_id,
        requirement_id=requirement_id,
    )
    requirement["document_requirements"] = doc_requirements
    
    return requirement


@router.post("/requirements")
async def create_requirement(
    data: ComplianceRequirementCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create a compliance requirement"""
    # Verify client belongs to firm
    client = repo.client_by_id(sb, data.client_id, current.firm_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    req_data = data.model_dump()
    req_data["firm_id"] = str(current.firm_id)
    req_data["client_id"] = str(data.client_id)
    req_data["status"] = "pending"
    req_data["is_enabled"] = True
    req_data["created_by"] = str(current.id)
    
    if data.template_id:
        req_data["template_id"] = str(data.template_id)
        
        # Get template to create document requirements
        template = repo.compliance_template_by_id(sb, data.template_id)
        if template and template.get("documents_required"):
            requirement = repo.create_compliance_requirement(sb, req_data)
            if requirement:
                compliance_service.create_document_requirements_for_compliance(
                    sb,
                    current.firm_id,
                    uuid.UUID(requirement["id"]),
                    template["documents_required"],
                )
            return requirement
    
    requirement = repo.create_compliance_requirement(sb, req_data)
    if not requirement:
        raise HTTPException(status_code=500, detail="Failed to create requirement")
    
    return requirement


@router.patch("/requirements/{requirement_id}")
async def update_requirement(
    requirement_id: uuid.UUID,
    data: ComplianceRequirementUpdate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Update a compliance requirement"""
    # Verify requirement belongs to firm
    requirement = repo.compliance_requirement_by_id(sb, requirement_id, current.firm_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Convert dates to ISO strings
    if "due_date" in update_data and update_data["due_date"]:
        update_data["due_date"] = update_data["due_date"].isoformat()
    if "completion_date" in update_data and update_data["completion_date"]:
        update_data["completion_date"] = update_data["completion_date"].isoformat()
    
    updated = repo.update_compliance_requirement(sb, requirement_id, update_data)
    return updated


@router.delete("/requirements/{requirement_id}")
async def delete_requirement(
    requirement_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Delete a compliance requirement"""
    # Only admin/owner can delete
    if current.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    success = repo.delete_compliance_requirement(sb, requirement_id, current.firm_id)
    if not success:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return {"success": True}


@router.post("/requirements/{requirement_id}/link-assignment")
async def link_to_assignment(
    requirement_id: uuid.UUID,
    data: LinkToAssignmentRequest,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Link a compliance requirement to an assignment"""
    # Verify requirement belongs to firm
    requirement = repo.compliance_requirement_by_id(sb, requirement_id, current.firm_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Verify assignment belongs to firm
    assignment = repo.assignment_by_id(sb, data.assignment_id, current.firm_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    compliance_service.link_compliance_to_assignment(
        sb,
        requirement_id,
        data.assignment_id,
    )
    
    return {"success": True}


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/generate")
async def generate_compliance(
    data: GenerateComplianceRequest,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """
    Generate compliance calendar for a client
    Creates all applicable compliance requirements for the financial year
    """
    requirements = compliance_service.generate_compliance_requirements_for_client(
        sb,
        firm_id=current.firm_id,
        client_id=data.client_id,
        financial_year=data.financial_year,
        created_by=current.id,
    )
    
    return {
        "success": True,
        "generated_count": len(requirements),
        "requirements": requirements,
    }


# ============================================================================
# REMINDERS & ALERTS
# ============================================================================

@router.get("/reminders")
async def list_reminders(
    template_id: Optional[uuid.UUID] = None,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List compliance reminders"""
    reminders = repo.list_compliance_reminders(
        sb,
        firm_id=current.firm_id,
        template_id=template_id,
        is_active=True,
    )
    return reminders


@router.post("/reminders")
async def create_reminder(
    data: ComplianceReminderCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create a compliance reminder rule"""
    if current.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    reminder_data = data.model_dump()
    reminder_data["firm_id"] = str(current.firm_id)
    reminder_data["is_active"] = True
    
    if data.template_id:
        reminder_data["template_id"] = str(data.template_id)
    
    reminder = repo.create_compliance_reminder(sb, reminder_data)
    if not reminder:
        raise HTTPException(status_code=500, detail="Failed to create reminder")
    
    return reminder


@router.get("/alerts")
async def list_alerts(
    unread_only: bool = False,
    limit: int = Query(50, le=200),
    offset: int = 0,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List compliance alerts for current user"""
    alerts = repo.list_compliance_alerts(
        sb,
        firm_id=current.firm_id,
        recipient_id=current.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    
    # Flatten nested data
    for alert in alerts:
        if alert.get("compliance_requirements"):
            req = alert["compliance_requirements"]
            alert["requirement_name"] = req.get("compliance_name")
            alert["due_date"] = req.get("due_date")
            if req.get("clients"):
                alert["client_name"] = req["clients"].get("company_name")
        if alert.get("firm_users"):
            alert["recipient_name"] = alert["firm_users"].get("full_name")
    
    return alerts


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Mark alert as read"""
    alert = repo.mark_alert_as_read(sb, alert_id)
    return {"success": True, "alert": alert}


@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert_endpoint(
    alert_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Dismiss an alert"""
    alert = repo.dismiss_alert(sb, alert_id)
    return {"success": True, "alert": alert}


@router.post("/alerts/generate")
async def generate_alerts(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """
    Manually trigger alert generation
    (Usually run by scheduler, but can be triggered manually)
    """
    if current.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    alerts = compliance_service.generate_reminders_and_alerts(sb, current.firm_id)
    
    return {
        "success": True,
        "generated_count": len(alerts),
    }


# ============================================================================
# ANALYTICS & DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def compliance_dashboard(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get compliance dashboard statistics"""
    stats = compliance_service.get_compliance_dashboard_stats(sb, current.firm_id)
    
    # Get upcoming deadlines (next 30 days)
    today = date.today()
    upcoming = repo.list_compliance_requirements(
        sb,
        firm_id=current.firm_id,
        from_date=today.isoformat(),
        to_date=(today + timedelta(days=30)).isoformat(),
        limit=10,
    )
    
    stats["upcoming_deadlines"] = upcoming
    
    return stats
