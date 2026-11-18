-- GNANOVA CA PRACTICE OS - Phase 3 Database Migrations
-- Migration: 003_phase3_billing
-- Date: 2026-11-18
-- Description: Billing, invoicing, payments, timesheets, and revenue analytics

-- ============================================================================
-- PART 1: FEE AGREEMENTS (Client Pricing)
-- ============================================================================

-- fee_agreements: Client-specific fee structures
CREATE TABLE IF NOT EXISTS fee_agreements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    agreement_name VARCHAR(255) NOT NULL,
    agreement_type VARCHAR(50) NOT NULL, -- fixed_monthly, hourly, project_based, annual_retainer
    start_date DATE NOT NULL,
    end_date DATE,
    currency VARCHAR(10) DEFAULT 'INR', -- INR, AED, USD
    
    -- Pricing details
    fixed_amount DECIMAL(12,2), -- For fixed/retainer
    hourly_rate DECIMAL(10,2), -- For hourly billing
    billing_frequency VARCHAR(50), -- monthly, quarterly, annual, one_time
    
    -- Payment terms
    payment_terms_days INTEGER DEFAULT 15, -- Net 15, Net 30, etc.
    late_fee_percentage DECIMAL(5,2), -- Late payment fee %
    
    -- Discounts
    discount_percentage DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    
    -- Service-specific rates
    service_rates JSONB, -- {"GST": 5000, "Income Tax": 15000, etc.}
    
    status VARCHAR(50) DEFAULT 'active', -- draft, active, expired, terminated
    notes TEXT,
    
    created_by UUID REFERENCES firm_users(id),
    approved_by UUID REFERENCES firm_users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fee_agreements_firm ON fee_agreements(firm_id);
CREATE INDEX idx_fee_agreements_client ON fee_agreements(client_id);
CREATE INDEX idx_fee_agreements_status ON fee_agreements(status);
CREATE INDEX idx_fee_agreements_dates ON fee_agreements(start_date, end_date);

-- ============================================================================
-- PART 2: INVOICES
-- ============================================================================

-- invoices: Invoice headers
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    fee_agreement_id UUID REFERENCES fee_agreements(id) ON DELETE SET NULL,
    
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    
    -- Invoice type
    invoice_type VARCHAR(50) DEFAULT 'standard', -- standard, recurring, advance, credit_note
    recurring_invoice_id UUID REFERENCES invoices(id), -- Parent for recurring
    
    -- Amounts (all in invoice currency)
    currency VARCHAR(10) DEFAULT 'INR',
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0, -- GST/VAT
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    
    -- Payment tracking
    paid_amount DECIMAL(12,2) DEFAULT 0,
    balance_due DECIMAL(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, viewed, partially_paid, paid, overdue, cancelled
    
    -- Dates
    sent_at TIMESTAMPTZ,
    viewed_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    
    -- References
    assignment_ids UUID[], -- Multiple assignments can be billed in one invoice
    compliance_ids UUID[], -- Multiple compliance items
    
    -- Notes
    description TEXT,
    notes TEXT, -- Internal notes
    terms_and_conditions TEXT,
    
    -- PDF
    pdf_generated BOOLEAN DEFAULT false,
    pdf_path VARCHAR(500),
    
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoices_firm ON invoices(firm_id);
CREATE INDEX idx_invoices_client ON invoices(client_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_dates ON invoices(invoice_date, due_date);
CREATE INDEX idx_invoices_fee_agreement ON invoices(fee_agreement_id) WHERE fee_agreement_id IS NOT NULL;

-- ============================================================================
-- PART 3: INVOICE ITEMS (Line Items)
-- ============================================================================

-- invoice_items: Line items in invoices
CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    
    -- Item details
    item_type VARCHAR(50) DEFAULT 'service', -- service, expense, discount, tax
    description TEXT NOT NULL,
    
    -- References
    assignment_id UUID REFERENCES assignments(id),
    compliance_id UUID REFERENCES compliance_requirements(id),
    
    -- Service details
    service_category VARCHAR(100),
    service_code VARCHAR(50),
    
    -- Quantity & Rate
    quantity DECIMAL(10,2) DEFAULT 1,
    unit VARCHAR(50) DEFAULT 'hours', -- hours, days, service, flat
    rate DECIMAL(10,2) NOT NULL,
    
    -- Amount
    amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0, -- GST/VAT rate
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_firm ON invoice_items(firm_id);
CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_assignment ON invoice_items(assignment_id) WHERE assignment_id IS NOT NULL;

-- ============================================================================
-- PART 4: PAYMENTS
-- ============================================================================

-- payments: Payment records
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    
    payment_number VARCHAR(50) UNIQUE,
    payment_date DATE NOT NULL,
    
    -- Amount
    currency VARCHAR(10) DEFAULT 'INR',
    amount DECIMAL(12,2) NOT NULL,
    
    -- Payment method
    payment_method VARCHAR(50), -- bank_transfer, cheque, cash, card, upi, online
    payment_reference VARCHAR(255), -- Transaction ID, Cheque number, etc.
    
    -- Bank details
    bank_name VARCHAR(255),
    bank_account_last4 VARCHAR(10),
    
    -- Status
    status VARCHAR(50) DEFAULT 'received', -- pending, received, cleared, bounced, refunded
    cleared_at TIMESTAMPTZ,
    
    -- Notes
    notes TEXT,
    
    -- References
    receipt_generated BOOLEAN DEFAULT false,
    receipt_path VARCHAR(500),
    
    recorded_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_firm ON payments(firm_id);
CREATE INDEX idx_payments_client ON payments(client_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id) WHERE invoice_id IS NOT NULL;
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_status ON payments(status);

-- ============================================================================
-- PART 5: TIMESHEETS
-- ============================================================================

-- timesheets: Weekly/monthly timesheets (header)
CREATE TABLE IF NOT EXISTS timesheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES firm_users(id) ON DELETE CASCADE,
    
    timesheet_period_start DATE NOT NULL,
    timesheet_period_end DATE NOT NULL,
    
    -- Totals
    total_hours DECIMAL(10,2) DEFAULT 0,
    billable_hours DECIMAL(10,2) DEFAULT 0,
    non_billable_hours DECIMAL(10,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, approved, rejected
    submitted_at TIMESTAMPTZ,
    approved_by UUID REFERENCES firm_users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timesheets_firm ON timesheets(firm_id);
CREATE INDEX idx_timesheets_user ON timesheets(user_id);
CREATE INDEX idx_timesheets_period ON timesheets(timesheet_period_start, timesheet_period_end);
CREATE INDEX idx_timesheets_status ON timesheets(status);

-- ============================================================================
-- PART 6: TIMESHEET ENTRIES (Individual Time Logs)
-- ============================================================================

-- timesheet_entries: Individual time entries
CREATE TABLE IF NOT EXISTS timesheet_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES firm_users(id) ON DELETE CASCADE,
    timesheet_id UUID REFERENCES timesheets(id) ON DELETE SET NULL,
    
    -- Date & Time
    entry_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    duration_hours DECIMAL(5,2) NOT NULL, -- Calculated or manual
    
    -- References
    client_id UUID REFERENCES clients(id),
    assignment_id UUID REFERENCES assignments(id),
    compliance_id UUID REFERENCES compliance_requirements(id),
    
    -- Activity details
    activity_type VARCHAR(100), -- research, preparation, filing, client_meeting, internal_meeting, etc.
    description TEXT,
    
    -- Billing
    is_billable BOOLEAN DEFAULT true,
    billable_rate DECIMAL(10,2), -- Rate at time of entry
    billable_amount DECIMAL(10,2), -- Calculated: hours * rate
    
    -- Invoice tracking
    is_invoiced BOOLEAN DEFAULT false,
    invoice_id UUID REFERENCES invoices(id),
    invoiced_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timesheet_entries_firm ON timesheet_entries(firm_id);
CREATE INDEX idx_timesheet_entries_user ON timesheet_entries(user_id);
CREATE INDEX idx_timesheet_entries_timesheet ON timesheet_entries(timesheet_id) WHERE timesheet_id IS NOT NULL;
CREATE INDEX idx_timesheet_entries_date ON timesheet_entries(entry_date);
CREATE INDEX idx_timesheet_entries_client ON timesheet_entries(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_timesheet_entries_assignment ON timesheet_entries(assignment_id) WHERE assignment_id IS NOT NULL;
CREATE INDEX idx_timesheet_entries_billable ON timesheet_entries(is_billable) WHERE is_billable = true;
CREATE INDEX idx_timesheet_entries_invoiced ON timesheet_entries(is_invoiced, invoice_id);

-- ============================================================================
-- PART 7: REVENUE ANALYTICS (Materialized View for Performance)
-- ============================================================================

-- This would be a materialized view in production, but we'll calculate on-demand for now
-- CREATE MATERIALIZED VIEW revenue_by_client AS ...

-- ============================================================================
-- PART 8: SEQUENCES FOR INVOICE/PAYMENT NUMBERS
-- ============================================================================

-- Create sequences for invoice and payment numbering
CREATE SEQUENCE IF NOT EXISTS invoice_number_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE IF NOT EXISTS payment_number_seq START WITH 1 INCREMENT BY 1;

-- ============================================================================
-- PART 9: ENHANCE EXISTING TABLES
-- ============================================================================

-- Add billing status to assignments
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS billing_status VARCHAR(50) DEFAULT 'unbilled'; -- unbilled, partially_billed, fully_billed
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS billed_amount DECIMAL(12,2) DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_assignments_billing_status ON assignments(billing_status);

-- Add billing fields to compliance_requirements
ALTER TABLE compliance_requirements ADD COLUMN IF NOT EXISTS billing_status VARCHAR(50) DEFAULT 'unbilled';
ALTER TABLE compliance_requirements ADD COLUMN IF NOT EXISTS billed_amount DECIMAL(12,2) DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_compliance_billing_status ON compliance_requirements(billing_status);

-- Add billing contact to clients
ALTER TABLE clients ADD COLUMN IF NOT EXISTS billing_contact_name VARCHAR(255);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS billing_contact_email VARCHAR(255);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS billing_contact_phone VARCHAR(32);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS billing_address TEXT;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification queries
-- SELECT COUNT(*) FROM fee_agreements;
-- SELECT COUNT(*) FROM invoices;
-- SELECT COUNT(*) FROM invoice_items;
-- SELECT COUNT(*) FROM payments;
-- SELECT COUNT(*) FROM timesheets;
-- SELECT COUNT(*) FROM timesheet_entries;
