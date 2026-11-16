"""Assignment domain models for CA Practice OS"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime

from app.models.enums import (
    AssignmentPriority,
    AssignmentStatus,
    ReviewLevel,
    ReviewStatus,
    ServiceCategory,
)


@dataclass
class Assignment:
    """Assignment model representing a client assignment/task"""

    id: uuid.UUID
    firm_id: uuid.UUID
    client_id: uuid.UUID
    assignment_code: str
    assignment_name: str
    service_category: str
    assignment_type: str
    financial_year: str
    period_start: date | None
    period_end: date | None
    assigned_partner: uuid.UUID | None
    assigned_manager: uuid.UUID | None
    assigned_staff: uuid.UUID | None
    start_date: date | None
    due_date: date
    completed_date: date | None
    priority: str
    status: str
    completion_pct: int
    estimated_hours: float | None
    actual_hours: float | None
    description: str | None
    internal_notes: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass
class AssignmentReview:
    """Assignment review record"""

    id: uuid.UUID
    assignment_id: uuid.UUID
    reviewer_id: uuid.UUID
    review_level: str
    submitted_at: datetime
    reviewed_at: datetime | None
    status: str
    comments: str | None
    rejection_reason: str | None
    created_at: datetime
