"""
Billing and invoicing API routes for GNANOVA CA Practice OS
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from supabase import Client

from app.core.security import get_current_firm_user
from app.db import get_db, repo
from app.models.staff import FirmUser

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class InvoiceItemCreate(BaseModel):
    description: str
    assignment_id: Optional[uuid.UUID] = None
    compliance_id: Optional[uuid.UUID] = None
    service_category: Optional[str] = None
    quantity: Decimal = Decimal("1")
    unit: str = "hours"
    rate: Decimal
    tax_rate: Decimal = Decimal("0")


class InvoiceCreate(BaseModel):
    client_id: uuid.UUID
    invoice_date: date
    due_date: date
    description: Optional[str] = None
    items: list[InvoiceItemCreate]
    tax_rate: Decimal = Decimal("18")  # GST 18% default
    discount_percentage: Decimal = Decimal("0")


class PaymentCreate(BaseModel):
    invoice_id: uuid.UUID
    payment_date: date
    amount: Decimal
    payment_method: str
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class TimesheetEntryCreate(BaseModel):
    entry_date: date
    duration_hours: Decimal
    client_id: Optional[uuid.UUID] = None
    assignment_id: Optional[uuid.UUID] = None
    activity_type: Optional[str] = None
    description: Optional[str] = None
    is_billable: bool = True


# ============================================================================
# INVOICES
# ============================================================================

@router.get("/invoices")
async def list_invoices(
    client_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List invoices with filters"""
    invoices = repo.list_invoices(
        sb,
        firm_id=current.firm_id,
        client_id=client_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    
    # Calculate days overdue
    today = date.today()
    for inv in invoices:
        if inv.get("clients"):
            inv["client_name"] = inv["clients"].get("company_name")
        
        due_date_str = inv["due_date"]
        due_date_obj = date.fromisoformat(due_date_str)
        if due_date_obj < today and inv["status"] not in ["paid", "cancelled"]:
            inv["days_overdue"] = (today - due_date_obj).days
            inv["is_overdue"] = True
        else:
            inv["days_overdue"] = 0
            inv["is_overdue"] = False
    
    return invoices


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get invoice by ID with items"""
    invoice = repo.invoice_by_id(sb, invoice_id, current.firm_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get invoice items
    items = repo.list_invoice_items(sb, invoice_id)
    invoice["items"] = items
    
    # Get payments
    payments = repo.list_payments(sb, current.firm_id, invoice_id=invoice_id)
    invoice["payments"] = payments
    
    return invoice


@router.post("/invoices")
async def create_invoice(
    data: InvoiceCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create a new invoice"""
    # Verify client
    client = repo.client_by_id(sb, data.client_id, current.firm_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate invoice number
    invoice_number = repo.generate_invoice_number(sb, current.firm_id)
    
    # Calculate totals from items
    subtotal = Decimal("0")
    for item in data.items:
        amount = item.quantity * item.rate
        subtotal += amount
    
    # Apply discount
    discount_amount = subtotal * (data.discount_percentage / Decimal("100"))
    after_discount = subtotal - discount_amount
    
    # Calculate tax
    tax_amount = after_discount * (data.tax_rate / Decimal("100"))
    total_amount = after_discount + tax_amount
    
    # Create invoice
    invoice_data = {
        "firm_id": str(current.firm_id),
        "client_id": str(data.client_id),
        "invoice_number": invoice_number,
        "invoice_date": data.invoice_date.isoformat(),
        "due_date": data.due_date.isoformat(),
        "currency": client.get("country") == "UAE" and "AED" or "INR",
        "subtotal": str(subtotal),
        "discount_amount": str(discount_amount),
        "tax_amount": str(tax_amount),
        "total_amount": str(total_amount),
        "balance_due": str(total_amount),
        "status": "draft",
        "description": data.description,
        "created_by": str(current.id),
    }
    
    invoice = repo.create_invoice(sb, invoice_data)
    if not invoice:
        raise HTTPException(status_code=500, detail="Failed to create invoice")
    
    # Create invoice items
    sort_order = 0
    for item in data.items:
        amount = item.quantity * item.rate
        item_tax = amount * (item.tax_rate / Decimal("100"))
        item_total = amount + item_tax
        
        item_data = {
            "firm_id": str(current.firm_id),
            "invoice_id": invoice["id"],
            "description": item.description,
            "quantity": str(item.quantity),
            "unit": item.unit,
            "rate": str(item.rate),
            "amount": str(amount),
            "tax_rate": str(item.tax_rate),
            "tax_amount": str(item_tax),
            "total_amount": str(item_total),
            "sort_order": sort_order,
        }
        
        if item.assignment_id:
            item_data["assignment_id"] = str(item.assignment_id)
        if item.compliance_id:
            item_data["compliance_id"] = str(item.compliance_id)
        if item.service_category:
            item_data["service_category"] = item.service_category
        
        repo.create_invoice_item(sb, item_data)
        sort_order += 1
    
    return invoice


@router.post("/invoices/{invoice_id}/send")
async def send_invoice(
    invoice_id: uuid.UUID,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Mark invoice as sent"""
    invoice = repo.invoice_by_id(sb, invoice_id, current.firm_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    from datetime import datetime
    repo.update_invoice(
        sb,
        invoice_id,
        {"status": "sent", "sent_at": datetime.now().isoformat()},
    )
    
    return {"success": True}


# ============================================================================
# PAYMENTS
# ============================================================================

@router.get("/payments")
async def list_payments(
    client_id: Optional[uuid.UUID] = None,
    limit: int = Query(100, le=500),
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List payments"""
    payments = repo.list_payments(
        sb,
        firm_id=current.firm_id,
        client_id=client_id,
        limit=limit,
    )
    
    # Flatten nested data
    for payment in payments:
        if payment.get("clients"):
            payment["client_name"] = payment["clients"].get("company_name")
        if payment.get("invoices"):
            payment["invoice_number"] = payment["invoices"].get("invoice_number")
    
    return payments


@router.post("/payments")
async def record_payment(
    data: PaymentCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Record a payment"""
    # Verify invoice
    invoice = repo.invoice_by_id(sb, data.invoice_id, current.firm_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] == "paid":
        raise HTTPException(status_code=400, detail="Invoice is already paid")
    
    # Create payment
    payment_data = {
        "firm_id": str(current.firm_id),
        "client_id": invoice["client_id"],
        "invoice_id": str(data.invoice_id),
        "payment_date": data.payment_date.isoformat(),
        "currency": invoice["currency"],
        "amount": str(data.amount),
        "payment_method": data.payment_method,
        "payment_reference": data.payment_reference,
        "notes": data.notes,
        "status": "received",
        "recorded_by": str(current.id),
    }
    
    payment = repo.create_payment(sb, payment_data)
    
    # Update invoice
    new_paid_amount = Decimal(str(invoice["paid_amount"])) + data.amount
    new_balance = Decimal(str(invoice["total_amount"])) - new_paid_amount
    
    new_status = "paid" if new_balance <= 0 else "partially_paid"
    
    repo.update_invoice(
        sb,
        data.invoice_id,
        {
            "paid_amount": str(new_paid_amount),
            "balance_due": str(max(new_balance, Decimal("0"))),
            "status": new_status,
            "paid_at": data.payment_date.isoformat() if new_status == "paid" else None,
        },
    )
    
    return payment


# ============================================================================
# TIMESHEETS
# ============================================================================

@router.get("/timesheets/entries")
async def list_timesheet_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    is_billable: Optional[bool] = None,
    is_invoiced: Optional[bool] = None,
    limit: int = Query(200, le=500),
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """List timesheet entries"""
    entries = repo.list_timesheet_entries(
        sb,
        firm_id=current.firm_id,
        user_id=current.id,
        from_date=from_date,
        to_date=to_date,
        is_billable=is_billable,
        is_invoiced=is_invoiced,
        limit=limit,
    )
    
    # Flatten nested data
    for entry in entries:
        if entry.get("clients"):
            entry["client_name"] = entry["clients"].get("company_name")
        if entry.get("assignments"):
            entry["assignment_name"] = entry["assignments"].get("assignment_name")
        if entry.get("firm_users"):
            entry["user_name"] = entry["firm_users"].get("full_name")
    
    return entries


@router.post("/timesheets/entries")
async def create_timesheet_entry(
    data: TimesheetEntryCreate,
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Create a timesheet entry"""
    # Get user's cost per hour for billable amount
    user = repo.firm_user_by_id(sb, current.id)
    cost_per_hour = Decimal(str(user.get("cost_per_hour") or "1000"))
    
    billable_amount = data.duration_hours * cost_per_hour if data.is_billable else Decimal("0")
    
    entry_data = {
        "firm_id": str(current.firm_id),
        "user_id": str(current.id),
        "entry_date": data.entry_date.isoformat(),
        "duration_hours": str(data.duration_hours),
        "activity_type": data.activity_type,
        "description": data.description,
        "is_billable": data.is_billable,
        "billable_rate": str(cost_per_hour),
        "billable_amount": str(billable_amount),
        "is_invoiced": False,
    }
    
    if data.client_id:
        entry_data["client_id"] = str(data.client_id)
    if data.assignment_id:
        entry_data["assignment_id"] = str(data.assignment_id)
    
    entry = repo.create_timesheet_entry(sb, entry_data)
    return entry


# ============================================================================
# DASHBOARD & ANALYTICS
# ============================================================================

@router.get("/dashboard")
async def billing_dashboard(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get billing dashboard statistics"""
    stats = repo.get_billing_dashboard_stats(sb, current.firm_id)
    
    # Count invoices by status
    invoices = repo.list_invoices(sb, current.firm_id, limit=1000)
    invoices_sent = len([i for i in invoices if i["status"] in ["sent", "viewed", "partially_paid"]])
    invoices_paid = len([i for i in invoices if i["status"] == "paid"])
    invoices_overdue = len([i for i in invoices if i["status"] == "overdue"])
    
    # Unbilled hours
    unbilled_entries = repo.list_timesheet_entries(
        sb, current.firm_id, is_billable=True, is_invoiced=False, limit=1000
    )
    unbilled_hours = sum(Decimal(str(e.get("duration_hours", 0))) for e in unbilled_entries)
    unbilled_amount = sum(Decimal(str(e.get("billable_amount", 0))) for e in unbilled_entries)
    
    stats.update({
        "invoices_sent": invoices_sent,
        "invoices_paid": invoices_paid,
        "invoices_overdue": invoices_overdue,
        "unbilled_hours": float(unbilled_hours),
        "unbilled_amount": float(unbilled_amount),
    })
    
    return stats


@router.get("/receivables-ageing")
async def receivables_ageing(
    current: FirmUser = Depends(get_current_firm_user),
    sb: Client = Depends(get_db),
):
    """Get receivables ageing report"""
    invoices = repo.list_invoices(
        sb,
        current.firm_id,
        limit=1000,
    )
    
    # Group by client
    from collections import defaultdict
    client_ageing = defaultdict(lambda: {
        "current": Decimal("0"),
        "days_31_60": Decimal("0"),
        "days_61_90": Decimal("0"),
        "days_over_90": Decimal("0"),
        "total_outstanding": Decimal("0"),
    })
    
    today = date.today()
    
    for inv in invoices:
        if inv["status"] in ["paid", "cancelled"]:
            continue
        
        client_id = inv["client_id"]
        client_name = inv.get("clients", {}).get("company_name", "Unknown")
        balance = Decimal(str(inv["balance_due"]))
        due_date = date.fromisoformat(inv["due_date"])
        days_overdue = (today - due_date).days
        
        if days_overdue <= 30:
            client_ageing[client_id]["current"] += balance
        elif days_overdue <= 60:
            client_ageing[client_id]["days_31_60"] += balance
        elif days_overdue <= 90:
            client_ageing[client_id]["days_61_90"] += balance
        else:
            client_ageing[client_id]["days_over_90"] += balance
        
        client_ageing[client_id]["total_outstanding"] += balance
        client_ageing[client_id]["client_name"] = client_name
        client_ageing[client_id]["client_id"] = client_id
    
    # Convert to list
    ageing_list = []
    for client_id, data in client_ageing.items():
        ageing_list.append({
            "client_id": client_id,
            "client_name": data["client_name"],
            "total_outstanding": float(data["total_outstanding"]),
            "current": float(data["current"]),
            "days_31_60": float(data["days_31_60"]),
            "days_61_90": float(data["days_61_90"]),
            "days_over_90": float(data["days_over_90"]),
        })
    
    # Sort by total outstanding descending
    ageing_list.sort(key=lambda x: x["total_outstanding"], reverse=True)
    
    return ageing_list
