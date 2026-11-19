"""
GNANOVA CA PRACTICE OS - Accounting Workbench Models
Phase 4: Trial balance, ledger, reconciliations, imports
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


@dataclass
class AccountingImport:
    """Accounting data import record"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    engagement_id: Optional[UUID] = None
    
    import_type: str = ""
    file_name: str = ""
    file_size: Optional[int] = None
    
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    status: str = "processing"
    rows_imported: int = 0
    rows_failed: int = 0
    
    error_log: Optional[str] = None
    
    imported_by: Optional[UUID] = None
    imported_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class TrialBalanceEntry:
    """Trial balance entry"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    import_id: Optional[UUID] = None
    
    account_code: str
    account_name: str
    account_group: Optional[str] = None
    account_type: Optional[str] = None
    
    period_date: date
    
    opening_balance: Decimal = Decimal("0")
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    closing_balance: Decimal = Decimal("0")
    
    is_reconciled: bool = False
    has_variance: bool = False
    
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class LedgerEntry:
    """General ledger entry"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    import_id: Optional[UUID] = None
    
    entry_date: date
    voucher_number: Optional[str] = None
    voucher_type: Optional[str] = None
    
    account_code: str
    account_name: Optional[str] = None
    
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    
    narration: Optional[str] = None
    reference: Optional[str] = None
    
    created_at: Optional[datetime] = None


@dataclass
class BankReconciliation:
    """Bank reconciliation"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    
    bank_name: str
    account_number: str
    
    reconciliation_date: date
    
    book_balance: Decimal
    bank_balance: Decimal
    
    cheques_issued_not_presented: Decimal = Decimal("0")
    deposits_not_cleared: Decimal = Decimal("0")
    bank_charges: Decimal = Decimal("0")
    interest_credited: Decimal = Decimal("0")
    other_adjustments: Decimal = Decimal("0")
    
    adjusted_book_balance: Optional[Decimal] = None
    adjusted_bank_balance: Optional[Decimal] = None
    difference: Optional[Decimal] = None
    
    is_reconciled: bool = False
    
    notes: Optional[str] = None
    
    prepared_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class GSTReconciliation:
    """GST reconciliation"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    
    month: str  # YYYY-MM
    gstin: Optional[str] = None
    
    # Books
    books_taxable_sales: Decimal = Decimal("0")
    books_cgst: Decimal = Decimal("0")
    books_sgst: Decimal = Decimal("0")
    books_igst: Decimal = Decimal("0")
    books_total_gst: Decimal = Decimal("0")
    
    # GSTR-1
    gstr1_taxable_sales: Decimal = Decimal("0")
    gstr1_cgst: Decimal = Decimal("0")
    gstr1_sgst: Decimal = Decimal("0")
    gstr1_igst: Decimal = Decimal("0")
    gstr1_total_gst: Decimal = Decimal("0")
    
    # GSTR-3B
    gstr3b_taxable_sales: Decimal = Decimal("0")
    gstr3b_cgst: Decimal = Decimal("0")
    gstr3b_sgst: Decimal = Decimal("0")
    gstr3b_igst: Decimal = Decimal("0")
    gstr3b_total_gst: Decimal = Decimal("0")
    
    # Variances
    variance_taxable: Optional[Decimal] = None
    variance_gst: Optional[Decimal] = None
    
    is_reconciled: bool = False
    
    notes: Optional[str] = None
    
    prepared_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class TDSReconciliation:
    """TDS reconciliation"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    
    quarter: str  # Q1-2024
    tan: Optional[str] = None
    
    books_tds_deducted: Decimal = Decimal("0")
    books_tds_deposited: Decimal = Decimal("0")
    
    form26as_tds: Decimal = Decimal("0")
    
    tds_return_amount: Decimal = Decimal("0")
    
    variance_amount: Optional[Decimal] = None
    
    is_reconciled: bool = False
    
    notes: Optional[str] = None
    
    prepared_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AccountingDashboardStats:
    """Accounting workbench dashboard stats"""
    total_imports: int = 0
    pending_imports: int = 0
    completed_imports: int = 0
    
    trial_balance_entries: int = 0
    unreconciled_accounts: int = 0
    
    bank_reconciliations: int = 0
    unreconciled_banks: int = 0
    
    gst_reconciliations: int = 0
    gst_variances: int = 0
    
    tds_reconciliations: int = 0
    tds_variances: int = 0
    
    total_variance_amount: Decimal = Decimal("0")
