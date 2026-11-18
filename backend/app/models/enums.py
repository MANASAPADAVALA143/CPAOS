from __future__ import annotations

import enum


class Plan(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    agency = "agency"


class FirmUserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    staff = "staff"


class Country(str, enum.Enum):
    India = "India"
    UAE = "UAE"
    UK = "UK"
    US = "US"
    Singapore = "Singapore"
    Australia = "Australia"
    Other = "Other"


class EntityType(str, enum.Enum):
    individual = "individual"
    sole_proprietor = "sole_proprietor"
    sole_trader = "sole_trader"
    partnership = "partnership"
    llp = "llp"
    private_limited = "private_limited"
    public_limited = "public_limited"
    trust = "trust"
    llc = "llc"
    s_corp = "s_corp"
    c_corp = "c_corp"
    other = "other"


class ClientStatus(str, enum.Enum):
    invited = "invited"
    signature_pending = "signature_pending"
    in_progress = "in_progress"
    documents_pending = "documents_pending"
    under_review = "under_review"
    completed = "completed"
    active = "active"


class ChecklistItemStatus(str, enum.Enum):
    pending = "pending"
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"
    waived = "waived"


class DocumentReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MessageChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    sms = "sms"


class MessageDeliveryStatus(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    failed = "failed"


# ============================================================================
# CA PRACTICE OS - ASSIGNMENT MANAGEMENT ENUMS
# ============================================================================

class ServiceCategory(str, enum.Enum):
    """Service categories for assignments"""
    gst = "GST"
    income_tax = "Income Tax"
    tds = "TDS"
    tcs = "TCS"
    mca = "MCA"
    roc = "ROC"
    audit = "Audit"
    accounting = "Accounting"
    payroll = "Payroll"
    advisory = "Advisory"
    other = "Other"


class AssignmentType(str, enum.Enum):
    """Common assignment types (subset - can be extended)"""
    # GST
    gstr_1 = "GSTR-1"
    gstr_3b = "GSTR-3B"
    gstr_9 = "GSTR-9"
    gstr_9c = "GSTR-9C"
    
    # Income Tax
    itr = "Income Tax Return"
    advance_tax = "Advance Tax"
    tax_audit = "Tax Audit"
    tax_computation = "Tax Computation"
    
    # TDS
    tds_24q = "24Q"
    tds_26q = "26Q"
    tds_27q = "27Q"
    tds_27eq = "27EQ"
    
    # MCA
    aoc_4 = "AOC-4"
    mgt_7 = "MGT-7"
    dir_3_kyc = "DIR-3 KYC"
    
    # Audit
    statutory_audit = "Statutory Audit"
    internal_audit = "Internal Audit"
    tax_audit_report = "Tax Audit Report"
    
    # Accounting
    bookkeeping = "Bookkeeping"
    bank_reconciliation = "Bank Reconciliation"
    financial_statements = "Financial Statements"
    
    # Other
    other = "Other"


class AssignmentStatus(str, enum.Enum):
    """Assignment lifecycle status"""
    created = "created"
    assigned = "assigned"
    in_progress = "in_progress"
    submitted = "submitted"
    manager_review = "manager_review"
    partner_review = "partner_review"
    approved = "approved"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"


class AssignmentPriority(str, enum.Enum):
    """Assignment priority levels"""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class ReviewLevel(str, enum.Enum):
    """Review levels in workflow"""
    manager = "manager"
    partner = "partner"


class ReviewStatus(str, enum.Enum):
    """Review status"""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    changes_requested = "changes_requested"


class ClientCategory(str, enum.Enum):
    """Client categorization"""
    premium = "Premium"
    standard = "Standard"
    basic = "Basic"


class RiskClassification(str, enum.Enum):
    """Client risk classification"""
    low = "Low"
    medium = "Medium"
    high = "High"


# ============================================================================
# PHASE 2 - COMPLIANCE CALENDAR ENUMS
# ============================================================================

class ComplianceFrequency(str, enum.Enum):
    """Compliance frequency types"""
    monthly = "monthly"
    quarterly = "quarterly"
    half_yearly = "half_yearly"
    annual = "annual"
    event_based = "event_based"


class ComplianceStatus(str, enum.Enum):
    """Compliance requirement status"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    not_applicable = "not_applicable"


class ReminderType(str, enum.Enum):
    """Reminder/notification types"""
    notification = "notification"
    email = "email"
    whatsapp = "whatsapp"
    escalation = "escalation"


class AlertType(str, enum.Enum):
    """Alert types"""
    reminder = "reminder"
    overdue = "overdue"
    escalation = "escalation"
    completed = "completed"
    due_soon = "due_soon"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    info = "info"
    warning = "warning"
    critical = "critical"


class DocumentRequirementStatus(str, enum.Enum):
    """Document requirement status"""
    pending = "pending"
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"


# ============================================================================
# PHASE 3 - BILLING & INVOICING ENUMS
# ============================================================================

class AgreementType(str, enum.Enum):
    """Fee agreement types"""
    fixed_monthly = "fixed_monthly"
    hourly = "hourly"
    project_based = "project_based"
    annual_retainer = "annual_retainer"


class BillingFrequency(str, enum.Enum):
    """Billing frequency"""
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"
    one_time = "one_time"


class InvoiceType(str, enum.Enum):
    """Invoice types"""
    standard = "standard"
    recurring = "recurring"
    advance = "advance"
    credit_note = "credit_note"


class InvoiceStatus(str, enum.Enum):
    """Invoice status"""
    draft = "draft"
    sent = "sent"
    viewed = "viewed"
    partially_paid = "partially_paid"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment methods"""
    bank_transfer = "bank_transfer"
    cheque = "cheque"
    cash = "cash"
    card = "card"
    upi = "upi"
    online = "online"


class PaymentStatus(str, enum.Enum):
    """Payment status"""
    pending = "pending"
    received = "received"
    cleared = "cleared"
    bounced = "bounced"
    refunded = "refunded"


class TimesheetStatus(str, enum.Enum):
    """Timesheet status"""
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class ActivityType(str, enum.Enum):
    """Time entry activity types"""
    research = "research"
    preparation = "preparation"
    filing = "filing"
    client_meeting = "client_meeting"
    internal_meeting = "internal_meeting"
    review = "review"
    documentation = "documentation"
    travel = "travel"
    other = "other"
