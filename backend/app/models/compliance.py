"""
Compliance management models for GNANOVA CA Practice OS
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from app.models.enums import (
    ComplianceFrequency,
    ComplianceStatus,
    ReminderType,
    AlertType,
    AlertSeverity,
    DocumentRequirementStatus,
    AssignmentPriority,
    ServiceCategory,
)


@dataclass
class ComplianceTemplate:
    """Master compliance rule template"""
    id: UUID
    firm_id: Optional[UUID]
    country: str
    service_category: str
    compliance_name: str
    compliance_code: Optional[str]
    description: Optional[str]
    frequency: str
    due_day_of_month: Optional[int]
    due_month: Optional[int]
    due_days_after_period_end: Optional[int]
    applies_to_entity_types: list[str]
    is_active: bool
    is_system_template: bool
    documents_required: list[str]
    auto_create_assignment: bool
    priority: str
    estimated_hours: Optional[float]
    penalty_info: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class ComplianceRequirement:
    """Client-specific compliance instance"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    template_id: Optional[UUID]
    compliance_name: str
    service_category: str
    financial_year: str
    period_start: Optional[date]
    period_end: Optional[date]
    due_date: date
    status: str
    completion_date: Optional[date]
    assignment_id: Optional[UUID]
    assigned_to: Optional[UUID]
    priority: str
    is_enabled: bool
    notes: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined fields (not in DB)
    client_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    template_code: Optional[str] = None
    days_until_due: Optional[int] = None
    is_overdue: bool = False


@dataclass
class ComplianceReminder:
    """Reminder and escalation rule"""
    id: UUID
    firm_id: UUID
    template_id: Optional[UUID]
    reminder_name: str
    days_before_due: int
    reminder_type: str
    escalate_to_role: Optional[str]
    is_active: bool
    message_template: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class ComplianceAlert:
    """Generated alert/notification"""
    id: UUID
    firm_id: UUID
    requirement_id: UUID
    reminder_id: Optional[UUID]
    alert_type: str
    severity: str
    recipient_id: UUID
    message: str
    sent_at: datetime
    read_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    notification_sent: bool
    created_at: datetime
    
    # Joined fields
    requirement_name: Optional[str] = None
    client_name: Optional[str] = None
    due_date: Optional[date] = None
    recipient_name: Optional[str] = None


@dataclass
class DocumentRequirement:
    """Required document for compliance"""
    id: UUID
    firm_id: UUID
    requirement_id: UUID
    document_name: str
    document_type: Optional[str]
    is_mandatory: bool
    status: str
    document_id: Optional[UUID]
    uploaded_at: Optional[datetime]
    verified_by: Optional[UUID]
    verified_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    
    # Joined fields
    document_filename: Optional[str] = None
    verified_by_name: Optional[str] = None


@dataclass
class ComplianceDashboardStats:
    """Compliance dashboard statistics"""
    total_requirements: int
    pending: int
    in_progress: int
    completed: int
    overdue: int
    due_this_week: int
    due_this_month: int
    total_alerts: int
    unread_alerts: int
    upcoming_deadlines: list[dict]
    compliance_by_category: list[dict]
    compliance_by_client: list[dict]
