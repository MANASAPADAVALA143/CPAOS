"""
Billing and invoicing models for GNANOVA CA Practice OS
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class FeeAgreement:
    """Client fee agreement"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    agreement_name: str
    agreement_type: str
    start_date: date
    end_date: Optional[date]
    currency: str
    fixed_amount: Optional[Decimal]
    hourly_rate: Optional[Decimal]
    billing_frequency: Optional[str]
    payment_terms_days: int
    late_fee_percentage: Optional[Decimal]
    discount_percentage: Optional[Decimal]
    discount_amount: Optional[Decimal]
    service_rates: Optional[dict]
    status: str
    notes: Optional[str]
    created_by: Optional[UUID]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined fields
    client_name: Optional[str] = None


@dataclass
class Invoice:
    """Invoice header"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    fee_agreement_id: Optional[UUID]
    invoice_number: str
    invoice_date: date
    due_date: date
    invoice_type: str
    recurring_invoice_id: Optional[UUID]
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    status: str
    sent_at: Optional[datetime]
    viewed_at: Optional[datetime]
    paid_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    assignment_ids: Optional[list[str]]
    compliance_ids: Optional[list[str]]
    description: Optional[str]
    notes: Optional[str]
    terms_and_conditions: Optional[str]
    pdf_generated: bool
    pdf_path: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined/calculated fields
    client_name: Optional[str] = None
    days_overdue: Optional[int] = None
    is_overdue: bool = False


@dataclass
class InvoiceItem:
    """Invoice line item"""
    id: UUID
    firm_id: UUID
    invoice_id: UUID
    item_type: str
    description: str
    assignment_id: Optional[UUID]
    compliance_id: Optional[UUID]
    service_category: Optional[str]
    service_code: Optional[str]
    quantity: Decimal
    unit: str
    rate: Decimal
    amount: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    sort_order: int
    created_at: datetime


@dataclass
class Payment:
    """Payment record"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    invoice_id: Optional[UUID]
    payment_number: Optional[str]
    payment_date: date
    currency: str
    amount: Decimal
    payment_method: Optional[str]
    payment_reference: Optional[str]
    bank_name: Optional[str]
    bank_account_last4: Optional[str]
    status: str
    cleared_at: Optional[datetime]
    notes: Optional[str]
    receipt_generated: bool
    receipt_path: Optional[str]
    recorded_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined fields
    client_name: Optional[str] = None
    invoice_number: Optional[str] = None


@dataclass
class Timesheet:
    """Timesheet header"""
    id: UUID
    firm_id: UUID
    user_id: UUID
    timesheet_period_start: date
    timesheet_period_end: date
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    status: str
    submitted_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined fields
    user_name: Optional[str] = None
    approver_name: Optional[str] = None


@dataclass
class TimesheetEntry:
    """Individual time entry"""
    id: UUID
    firm_id: UUID
    user_id: UUID
    timesheet_id: Optional[UUID]
    entry_date: date
    start_time: Optional[str]
    end_time: Optional[str]
    duration_hours: Decimal
    client_id: Optional[UUID]
    assignment_id: Optional[UUID]
    compliance_id: Optional[UUID]
    activity_type: Optional[str]
    description: Optional[str]
    is_billable: bool
    billable_rate: Optional[Decimal]
    billable_amount: Optional[Decimal]
    is_invoiced: bool
    invoice_id: Optional[UUID]
    invoiced_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Joined fields
    client_name: Optional[str] = None
    assignment_name: Optional[str] = None
    user_name: Optional[str] = None


@dataclass
class BillingDashboardStats:
    """Billing dashboard statistics"""
    total_revenue: Decimal
    revenue_this_month: Decimal
    outstanding_amount: Decimal
    overdue_amount: Decimal
    invoices_sent: int
    invoices_paid: int
    invoices_overdue: int
    average_days_to_payment: float
    clients_with_outstanding: int
    unbilled_hours: Decimal
    unbilled_amount: Decimal


@dataclass
class ReceivablesAgeing:
    """Receivables ageing report"""
    client_id: UUID
    client_name: str
    total_outstanding: Decimal
    current: Decimal  # 0-30 days
    days_31_60: Decimal
    days_61_90: Decimal
    days_over_90: Decimal
    oldest_invoice_date: Optional[date]
    days_overdue: Optional[int]


@dataclass
class ClientProfitability:
    """Client profitability analysis"""
    client_id: UUID
    client_name: str
    total_revenue: Decimal
    total_hours: Decimal
    total_cost: Decimal  # hours * cost_per_hour
    gross_profit: Decimal
    profit_margin: Decimal  # percentage
    average_hourly_rate: Decimal
