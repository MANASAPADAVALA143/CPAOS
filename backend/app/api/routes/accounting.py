"""
GNANOVA CA PRACTICE OS - Accounting Workbench API Routes
Phase 4: Trial balance, ledger, reconciliations, Excel/CSV imports
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from supabase import Client
import io
import csv

from app.api.deps import get_current_user, get_supabase
from app.models import FirmUser
from app.db import repo

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TrialBalanceImport(BaseModel):
    client_id: UUID
    period_date: date
    entries: List[dict]


class BankReconciliationCreate(BaseModel):
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
    notes: Optional[str] = None


class GSTReconciliationCreate(BaseModel):
    client_id: UUID
    month: str  # YYYY-MM
    gstin: Optional[str] = None
    books_taxable_sales: Decimal = Decimal("0")
    books_cgst: Decimal = Decimal("0")
    books_sgst: Decimal = Decimal("0")
    books_igst: Decimal = Decimal("0")
    books_total_gst: Decimal = Decimal("0")
    gstr1_taxable_sales: Decimal = Decimal("0")
    gstr1_cgst: Decimal = Decimal("0")
    gstr1_sgst: Decimal = Decimal("0")
    gstr1_igst: Decimal = Decimal("0")
    gstr1_total_gst: Decimal = Decimal("0")
    gstr3b_taxable_sales: Decimal = Decimal("0")
    gstr3b_cgst: Decimal = Decimal("0")
    gstr3b_sgst: Decimal = Decimal("0")
    gstr3b_igst: Decimal = Decimal("0")
    gstr3b_total_gst: Decimal = Decimal("0")
    notes: Optional[str] = None


class TDSReconciliationCreate(BaseModel):
    client_id: UUID
    quarter: str  # Q1-2024
    tan: Optional[str] = None
    books_tds_deducted: Decimal = Decimal("0")
    books_tds_deposited: Decimal = Decimal("0")
    form26as_tds: Decimal = Decimal("0")
    tds_return_amount: Decimal = Decimal("0")
    notes: Optional[str] = None


# ============================================================================
# DASHBOARD ENDPOINT
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Get accounting workbench dashboard statistics"""
    stats = repo.get_accounting_dashboard_stats(sb, current.firm_id)
    return stats


# ============================================================================
# TRIAL BALANCE ENDPOINTS
# ============================================================================

@router.get("/trial-balance")
async def list_trial_balance(
    client_id: Optional[UUID] = None,
    period_date: Optional[str] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List trial balance entries"""
    entries = repo.list_trial_balance(sb, current.firm_id, client_id, period_date)
    
    # Calculate totals
    total_debit = sum(Decimal(str(e.get("debit_amount", 0))) for e in entries)
    total_credit = sum(Decimal(str(e.get("credit_amount", 0))) for e in entries)
    total_closing = sum(Decimal(str(e.get("closing_balance", 0))) for e in entries)
    
    return {
        "entries": entries,
        "totals": {
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "total_closing": float(total_closing),
        },
    }


@router.post("/trial-balance/import")
async def import_trial_balance(
    file: UploadFile = File(...),
    client_id: UUID = None,
    period_date: str = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Import trial balance from CSV file"""
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        # Create import record
        import_record = repo.create_accounting_import(
            sb,
            current.firm_id,
            {
                "client_id": str(client_id),
                "import_type": "trial_balance",
                "file_name": file.filename,
                "file_size": len(content),
                "period_start": period_date,
                "period_end": period_date,
                "imported_by": str(current.id),
                "status": "processing",
            },
        )
        
        # Parse entries
        entries = []
        rows_imported = 0
        rows_failed = 0
        
        for row in reader:
            try:
                entry = {
                    "client_id": str(client_id),
                    "import_id": import_record["id"],
                    "account_code": row.get("account_code", ""),
                    "account_name": row.get("account_name", ""),
                    "account_group": row.get("account_group"),
                    "account_type": row.get("account_type"),
                    "period_date": period_date,
                    "opening_balance": Decimal(row.get("opening_balance", "0")),
                    "debit_amount": Decimal(row.get("debit_amount", "0")),
                    "credit_amount": Decimal(row.get("credit_amount", "0")),
                    "closing_balance": Decimal(row.get("closing_balance", "0")),
                }
                entries.append(entry)
                rows_imported += 1
            except Exception as e:
                rows_failed += 1
                continue
        
        # Bulk insert
        if entries:
            repo.create_trial_balance_bulk(sb, current.firm_id, entries)
        
        # Update import record
        sb.table("accounting_imports").update({
            "status": "completed",
            "rows_imported": rows_imported,
            "rows_failed": rows_failed,
        }).eq("id", import_record["id"]).execute()
        
        return {
            "import_id": import_record["id"],
            "rows_imported": rows_imported,
            "rows_failed": rows_failed,
            "status": "completed",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# ============================================================================
# LEDGER ENDPOINTS
# ============================================================================

@router.get("/ledger")
async def list_ledger_entries(
    client_id: Optional[UUID] = None,
    account_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List ledger entries"""
    entries = repo.list_ledger_entries(
        sb, current.firm_id, client_id, account_code, start_date, end_date
    )
    
    # Calculate totals
    total_debit = sum(Decimal(str(e.get("debit_amount", 0))) for e in entries)
    total_credit = sum(Decimal(str(e.get("credit_amount", 0))) for e in entries)
    
    return {
        "entries": entries,
        "totals": {
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "balance": float(total_debit - total_credit),
        },
    }


@router.post("/ledger/import")
async def import_ledger(
    file: UploadFile = File(...),
    client_id: UUID = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Import ledger entries from CSV file"""
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        import_record = repo.create_accounting_import(
            sb,
            current.firm_id,
            {
                "client_id": str(client_id),
                "import_type": "ledger",
                "file_name": file.filename,
                "file_size": len(content),
                "imported_by": str(current.id),
                "status": "processing",
            },
        )
        
        entries = []
        rows_imported = 0
        
        for row in reader:
            try:
                entry = {
                    "client_id": str(client_id),
                    "import_id": import_record["id"],
                    "entry_date": row.get("entry_date"),
                    "voucher_number": row.get("voucher_number"),
                    "voucher_type": row.get("voucher_type"),
                    "account_code": row.get("account_code", ""),
                    "account_name": row.get("account_name"),
                    "debit_amount": Decimal(row.get("debit_amount", "0")),
                    "credit_amount": Decimal(row.get("credit_amount", "0")),
                    "narration": row.get("narration"),
                    "reference": row.get("reference"),
                }
                entries.append(entry)
                rows_imported += 1
            except:
                continue
        
        # Bulk insert (batch of 100)
        for i in range(0, len(entries), 100):
            batch = entries[i:i+100]
            payload = [
                {**e, "firm_id": str(current.firm_id), "created_at": "NOW()"}
                for e in batch
            ]
            sb.table("ledger_entries").insert(payload).execute()
        
        sb.table("accounting_imports").update({
            "status": "completed",
            "rows_imported": rows_imported,
        }).eq("id", import_record["id"]).execute()
        
        return {
            "import_id": import_record["id"],
            "rows_imported": rows_imported,
            "status": "completed",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# ============================================================================
# BANK RECONCILIATION ENDPOINTS
# ============================================================================

@router.get("/bank-reconciliation")
async def list_bank_reconciliations(
    client_id: Optional[UUID] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List bank reconciliations"""
    query = sb.table("bank_reconciliation").select("*").eq("firm_id", str(current.firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    
    query = query.order("reconciliation_date", desc=True)
    r = query.execute()
    
    return {"reconciliations": r.data or []}


@router.post("/bank-reconciliation")
async def create_bank_reconciliation(
    data: BankReconciliationCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create bank reconciliation"""
    payload = {
        **data.model_dump(),
        "prepared_by": str(current.id),
    }
    reco = repo.create_bank_reconciliation(sb, current.firm_id, payload)
    return {"reconciliation": reco}


# ============================================================================
# GST RECONCILIATION ENDPOINTS
# ============================================================================

@router.get("/gst-reconciliation")
async def list_gst_reconciliations(
    client_id: Optional[UUID] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List GST reconciliations"""
    query = sb.table("gst_reconciliation").select("*").eq("firm_id", str(current.firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    
    query = query.order("month", desc=True)
    r = query.execute()
    
    return {"reconciliations": r.data or []}


@router.post("/gst-reconciliation")
async def create_gst_reconciliation(
    data: GSTReconciliationCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create GST reconciliation"""
    payload = {
        **data.model_dump(),
        "prepared_by": str(current.id),
    }
    reco = repo.create_gst_reconciliation(sb, current.firm_id, payload)
    return {"reconciliation": reco}


# ============================================================================
# TDS RECONCILIATION ENDPOINTS
# ============================================================================

@router.get("/tds-reconciliation")
async def list_tds_reconciliations(
    client_id: Optional[UUID] = None,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """List TDS reconciliations"""
    query = sb.table("tds_reconciliation").select("*").eq("firm_id", str(current.firm_id))
    
    if client_id:
        query = query.eq("client_id", str(client_id))
    
    query = query.order("quarter", desc=True)
    r = query.execute()
    
    return {"reconciliations": r.data or []}


@router.post("/tds-reconciliation")
async def create_tds_reconciliation(
    data: TDSReconciliationCreate,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create TDS reconciliation"""
    payload = {
        **data.model_dump(),
        "prepared_by": str(current.id),
    }
    reco = repo.create_tds_reconciliation(sb, current.firm_id, payload)
    return {"reconciliation": reco}
