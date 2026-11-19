"""
GNANOVA CA PRACTICE OS - Audit Engagement Models
Phase 4: Audit engagement, working papers, PBC, risk assessment, review notes
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


@dataclass
class AuditEngagement:
    """Audit engagement model"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    
    engagement_name: str
    engagement_code: str
    engagement_type: str
    
    financial_year: str
    period_start: date
    period_end: date
    
    engagement_partner: Optional[UUID] = None
    audit_manager: Optional[UUID] = None
    audit_senior: Optional[UUID] = None
    team_members: Optional[List[UUID]] = None
    
    status: str = "planning"
    
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    report_date: Optional[date] = None
    
    budgeted_hours: Optional[Decimal] = None
    actual_hours: Decimal = Decimal("0")
    
    overall_risk_rating: Optional[str] = None
    materiality_amount: Optional[Decimal] = None
    
    description: Optional[str] = None
    scope: Optional[str] = None
    notes: Optional[str] = None
    
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PBCChecklistItem:
    """PBC (Provided By Client) checklist item"""
    id: UUID
    firm_id: UUID
    engagement_id: UUID
    
    item_name: str
    item_category: Optional[str] = None
    description: Optional[str] = None
    
    is_mandatory: bool = True
    status: str = "pending"
    
    requested_date: Optional[date] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    reviewed_by: Optional[UUID] = None
    reviewed_date: Optional[date] = None
    
    document_id: Optional[UUID] = None
    notes: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class WorkingPaper:
    """Audit working paper"""
    id: UUID
    firm_id: UUID
    engagement_id: UUID
    
    reference_number: str
    title: str
    section: Optional[str] = None
    
    description: Optional[str] = None
    procedure_performed: Optional[str] = None
    findings: Optional[str] = None
    conclusion: Optional[str] = None
    
    status: str = "draft"
    
    prepared_by: Optional[UUID] = None
    prepared_date: Optional[date] = None
    reviewed_by: Optional[UUID] = None
    reviewed_date: Optional[date] = None
    approved_by: Optional[UUID] = None
    approved_date: Optional[date] = None
    
    document_ids: Optional[List[UUID]] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class RiskAssessment:
    """Audit risk assessment"""
    id: UUID
    firm_id: UUID
    engagement_id: UUID
    
    risk_area: str
    risk_description: str
    
    inherent_risk: Optional[str] = None
    control_risk: Optional[str] = None
    detection_risk: Optional[str] = None
    overall_risk: Optional[str] = None
    
    controls_identified: Optional[str] = None
    audit_procedures: Optional[str] = None
    
    assessed_by: Optional[UUID] = None
    assessed_date: Optional[date] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ReviewNote:
    """Review note/query"""
    id: UUID
    firm_id: UUID
    engagement_id: UUID
    working_paper_id: Optional[UUID] = None
    
    note_type: str = "review_point"
    note_text: str = ""
    
    raised_by: Optional[UUID] = None
    raised_date: Optional[date] = None
    
    assigned_to: Optional[UUID] = None
    
    status: str = "open"
    
    response_text: Optional[str] = None
    responded_by: Optional[UUID] = None
    responded_date: Optional[date] = None
    
    cleared_by: Optional[UUID] = None
    cleared_date: Optional[date] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AuditDashboardStats:
    """Audit dashboard statistics"""
    total_engagements: int = 0
    active_engagements: int = 0
    planning_phase: int = 0
    fieldwork_phase: int = 0
    review_phase: int = 0
    reporting_phase: int = 0
    completed: int = 0
    
    total_working_papers: int = 0
    draft_papers: int = 0
    approved_papers: int = 0
    
    total_pbc_items: int = 0
    pending_pbc: int = 0
    received_pbc: int = 0
    
    open_review_notes: int = 0
    high_risk_areas: int = 0
