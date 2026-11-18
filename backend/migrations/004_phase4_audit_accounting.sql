-- GNANOVA CA PRACTICE OS - Phase 4 Database Migrations
-- Migration: 004_phase4_audit_accounting
-- Date: 2026-11-18
-- Description: Audit engagements, working papers, accounting workbench, reconciliations

-- ============================================================================
-- PART 1: AUDIT ENGAGEMENTS
-- ============================================================================

-- audit_engagements: Audit engagement management
CREATE TABLE IF NOT EXISTS audit_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    engagement_name VARCHAR(255) NOT NULL,
    engagement_code VARCHAR(50) UNIQUE,
    engagement_type VARCHAR(100) NOT NULL, -- statutory_audit, tax_audit, internal_audit, review, agreed_upon_procedures
    
    -- Period
    financial_year VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Team
    engagement_partner UUID REFERENCES firm_users(id),
    audit_manager UUID REFERENCES firm_users(id),
    audit_senior UUID REFERENCES firm_users(id),
    team_members UUID[], -- Array of firm_user IDs
    
    -- Status
    status VARCHAR(50) DEFAULT 'planning', -- planning, fieldwork, review, reporting, completed, archived
    
    -- Dates
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    report_date DATE,
    
    -- Budgets
    budgeted_hours DECIMAL(10,2),
    actual_hours DECIMAL(10,2) DEFAULT 0,
    
    -- Risk
    overall_risk_rating VARCHAR(50), -- low, medium, high
    materiality_amount DECIMAL(15,2),
    
    -- Notes
    description TEXT,
    scope TEXT,
    notes TEXT,
    
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_engagements_firm ON audit_engagements(firm_id);
CREATE INDEX idx_audit_engagements_client ON audit_engagements(client_id);
CREATE INDEX idx_audit_engagements_status ON audit_engagements(status);
CREATE INDEX idx_audit_engagements_fy ON audit_engagements(financial_year);

-- ============================================================================
-- PART 2: PBC (PROVIDED BY CLIENT) CHECKLISTS
-- ============================================================================

-- pbc_checklists: Documents and info required from client
CREATE TABLE IF NOT EXISTS pbc_checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    engagement_id UUID NOT NULL REFERENCES audit_engagements(id) ON DELETE CASCADE,
    
    item_name VARCHAR(255) NOT NULL,
    item_category VARCHAR(100), -- financials, bank_statements, invoices, agreements, regulatory, tax, other
    description TEXT,
    
    is_mandatory BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'pending', -- pending, requested, received, reviewed, accepted, rejected
    
    requested_date DATE,
    due_date DATE,
    received_date DATE,
    reviewed_by UUID REFERENCES firm_users(id),
    reviewed_date DATE,
    
    document_id UUID REFERENCES documents(id),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pbc_checklists_engagement ON pbc_checklists(engagement_id);
CREATE INDEX idx_pbc_checklists_status ON pbc_checklists(status);

-- ============================================================================
-- PART 3: WORKING PAPERS
-- ============================================================================

-- working_papers: Audit working papers
CREATE TABLE IF NOT EXISTS working_papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    engagement_id UUID NOT NULL REFERENCES audit_engagements(id) ON DELETE CASCADE,
    
    reference_number VARCHAR(50) NOT NULL, -- A1, A2, B1, etc.
    title VARCHAR(255) NOT NULL,
    section VARCHAR(100), -- planning, risk, assets, liabilities, income, expenses, closing
    
    -- Content
    description TEXT,
    procedure_performed TEXT,
    findings TEXT,
    conclusion TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, in_progress, review, approved
    
    -- Ownership
    prepared_by UUID REFERENCES firm_users(id),
    prepared_date DATE,
    reviewed_by UUID REFERENCES firm_users(id),
    reviewed_date DATE,
    approved_by UUID REFERENCES firm_users(id),
    approved_date DATE,
    
    -- Links
    document_ids UUID[], -- Linked evidence documents
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_working_papers_engagement ON working_papers(engagement_id);
CREATE INDEX idx_working_papers_section ON working_papers(section);
CREATE INDEX idx_working_papers_status ON working_papers(status);
CREATE INDEX idx_working_papers_reference ON working_papers(reference_number);

-- ============================================================================
-- PART 4: RISK ASSESSMENTS
-- ============================================================================

-- risk_assessments: Audit risk register
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    engagement_id UUID NOT NULL REFERENCES audit_engagements(id) ON DELETE CASCADE,
    
    risk_area VARCHAR(255) NOT NULL, -- revenue, inventory, payroll, investments, etc.
    risk_description TEXT NOT NULL,
    
    -- Risk ratings
    inherent_risk VARCHAR(50), -- low, medium, high
    control_risk VARCHAR(50),
    detection_risk VARCHAR(50),
    overall_risk VARCHAR(50),
    
    -- Mitigations
    controls_identified TEXT,
    audit_procedures TEXT,
    
    assessed_by UUID REFERENCES firm_users(id),
    assessed_date DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_assessments_engagement ON risk_assessments(engagement_id);
CREATE INDEX idx_risk_assessments_area ON risk_assessments(risk_area);

-- ============================================================================
-- PART 5: REVIEW NOTES
-- ============================================================================

-- review_notes: Review comments and queries
CREATE TABLE IF NOT EXISTS review_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    engagement_id UUID NOT NULL REFERENCES audit_engagements(id) ON DELETE CASCADE,
    working_paper_id UUID REFERENCES working_papers(id),
    
    note_type VARCHAR(50) DEFAULT 'review_point', -- review_point, query, suggestion, concern
    note_text TEXT NOT NULL,
    
    raised_by UUID NOT NULL REFERENCES firm_users(id),
    raised_date DATE NOT NULL,
    
    assigned_to UUID REFERENCES firm_users(id),
    
    status VARCHAR(50) DEFAULT 'open', -- open, addressed, cleared, deferred
    
    response_text TEXT,
    responded_by UUID REFERENCES firm_users(id),
    responded_date DATE,
    
    cleared_by UUID REFERENCES firm_users(id),
    cleared_date DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_notes_engagement ON review_notes(engagement_id);
CREATE INDEX idx_review_notes_wp ON review_notes(working_paper_id) WHERE working_paper_id IS NOT NULL;
CREATE INDEX idx_review_notes_status ON review_notes(status);

-- ============================================================================
-- PART 6: ACCOUNTING IMPORTS (Excel/CSV Data)
-- ============================================================================

-- accounting_imports: Track imported data files
CREATE TABLE IF NOT EXISTS accounting_imports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    engagement_id UUID REFERENCES audit_engagements(id),
    
    import_type VARCHAR(50) NOT NULL, -- trial_balance, ledger, bank_statement, gst, tds
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    
    -- Period
    period_start DATE,
    period_end DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'processing', -- processing, completed, failed, cancelled
    rows_imported INTEGER DEFAULT 0,
    rows_failed INTEGER DEFAULT 0,
    
    error_log TEXT,
    
    imported_by UUID NOT NULL REFERENCES firm_users(id),
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_accounting_imports_firm ON accounting_imports(firm_id);
CREATE INDEX idx_accounting_imports_client ON accounting_imports(client_id);
CREATE INDEX idx_accounting_imports_type ON accounting_imports(import_type);

-- ============================================================================
-- PART 7: TRIAL BALANCE
-- ============================================================================

-- trial_balance: Imported TB data
CREATE TABLE IF NOT EXISTS trial_balance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    import_id UUID REFERENCES accounting_imports(id) ON DELETE CASCADE,
    
    -- Account details
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_group VARCHAR(100), -- assets, liabilities, equity, income, expenses
    account_type VARCHAR(100), -- cash, receivables, payables, revenue, cogs, etc.
    
    -- Period
    period_date DATE NOT NULL,
    
    -- Balances
    opening_balance DECIMAL(15,2) DEFAULT 0,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    closing_balance DECIMAL(15,2) DEFAULT 0,
    
    -- Flags
    is_reconciled BOOLEAN DEFAULT false,
    has_variance BOOLEAN DEFAULT false,
    
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trial_balance_firm ON trial_balance(firm_id);
CREATE INDEX idx_trial_balance_client ON trial_balance(client_id);
CREATE INDEX idx_trial_balance_import ON trial_balance(import_id);
CREATE INDEX idx_trial_balance_account ON trial_balance(account_code);
CREATE INDEX idx_trial_balance_period ON trial_balance(period_date);

-- ============================================================================
-- PART 8: LEDGER ENTRIES
-- ============================================================================

-- ledger_entries: Imported GL entries
CREATE TABLE IF NOT EXISTS ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    import_id UUID REFERENCES accounting_imports(id) ON DELETE CASCADE,
    
    entry_date DATE NOT NULL,
    voucher_number VARCHAR(100),
    voucher_type VARCHAR(50), -- journal, payment, receipt, contra, sales, purchase
    
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(255),
    
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    
    narration TEXT,
    reference VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ledger_entries_firm ON ledger_entries(firm_id);
CREATE INDEX idx_ledger_entries_client ON ledger_entries(client_id);
CREATE INDEX idx_ledger_entries_date ON ledger_entries(entry_date);
CREATE INDEX idx_ledger_entries_account ON ledger_entries(account_code);

-- ============================================================================
-- PART 9: BANK RECONCILIATION
-- ============================================================================

-- bank_reconciliation: Bank reco data
CREATE TABLE IF NOT EXISTS bank_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    bank_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    
    reconciliation_date DATE NOT NULL,
    
    -- Book balance
    book_balance DECIMAL(15,2) NOT NULL,
    
    -- Bank balance
    bank_balance DECIMAL(15,2) NOT NULL,
    
    -- Reconciling items
    cheques_issued_not_presented DECIMAL(15,2) DEFAULT 0,
    deposits_not_cleared DECIMAL(15,2) DEFAULT 0,
    bank_charges DECIMAL(15,2) DEFAULT 0,
    interest_credited DECIMAL(15,2) DEFAULT 0,
    other_adjustments DECIMAL(15,2) DEFAULT 0,
    
    -- Calculated balance
    adjusted_book_balance DECIMAL(15,2),
    adjusted_bank_balance DECIMAL(15,2),
    difference DECIMAL(15,2),
    
    is_reconciled BOOLEAN DEFAULT false,
    
    notes TEXT,
    
    prepared_by UUID REFERENCES firm_users(id),
    reviewed_by UUID REFERENCES firm_users(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bank_reco_firm ON bank_reconciliation(firm_id);
CREATE INDEX idx_bank_reco_client ON bank_reconciliation(client_id);
CREATE INDEX idx_bank_reco_date ON bank_reconciliation(reconciliation_date);

-- ============================================================================
-- PART 10: GST RECONCILIATION
-- ============================================================================

-- gst_reconciliation: GST reco data
CREATE TABLE IF NOT EXISTS gst_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    month VARCHAR(7) NOT NULL, -- YYYY-MM
    gstin VARCHAR(20),
    
    -- Books
    books_taxable_sales DECIMAL(15,2) DEFAULT 0,
    books_cgst DECIMAL(15,2) DEFAULT 0,
    books_sgst DECIMAL(15,2) DEFAULT 0,
    books_igst DECIMAL(15,2) DEFAULT 0,
    books_total_gst DECIMAL(15,2) DEFAULT 0,
    
    -- GSTR-1
    gstr1_taxable_sales DECIMAL(15,2) DEFAULT 0,
    gstr1_cgst DECIMAL(15,2) DEFAULT 0,
    gstr1_sgst DECIMAL(15,2) DEFAULT 0,
    gstr1_igst DECIMAL(15,2) DEFAULT 0,
    gstr1_total_gst DECIMAL(15,2) DEFAULT 0,
    
    -- GSTR-3B
    gstr3b_taxable_sales DECIMAL(15,2) DEFAULT 0,
    gstr3b_cgst DECIMAL(15,2) DEFAULT 0,
    gstr3b_sgst DECIMAL(15,2) DEFAULT 0,
    gstr3b_igst DECIMAL(15,2) DEFAULT 0,
    gstr3b_total_gst DECIMAL(15,2) DEFAULT 0,
    
    -- Variances
    variance_taxable DECIMAL(15,2),
    variance_gst DECIMAL(15,2),
    
    is_reconciled BOOLEAN DEFAULT false,
    
    notes TEXT,
    
    prepared_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gst_reco_firm ON gst_reconciliation(firm_id);
CREATE INDEX idx_gst_reco_client ON gst_reconciliation(client_id);
CREATE INDEX idx_gst_reco_month ON gst_reconciliation(month);

-- ============================================================================
-- PART 11: TDS RECONCILIATION
-- ============================================================================

-- tds_reconciliation: TDS reco data
CREATE TABLE IF NOT EXISTS tds_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    quarter VARCHAR(7) NOT NULL, -- Q1-2024, Q2-2024, etc.
    tan VARCHAR(20),
    
    -- Books
    books_tds_deducted DECIMAL(15,2) DEFAULT 0,
    books_tds_deposited DECIMAL(15,2) DEFAULT 0,
    
    -- Form 26AS
    form26as_tds DECIMAL(15,2) DEFAULT 0,
    
    -- TDS Return
    tds_return_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Variance
    variance_amount DECIMAL(15,2),
    
    is_reconciled BOOLEAN DEFAULT false,
    
    notes TEXT,
    
    prepared_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tds_reco_firm ON tds_reconciliation(firm_id);
CREATE INDEX idx_tds_reco_client ON tds_reconciliation(client_id);
CREATE INDEX idx_tds_reco_quarter ON tds_reconciliation(quarter);

-- ============================================================================
-- PART 12: AUDIT TRAIL
-- ============================================================================

-- audit_trail: Comprehensive audit trail for all changes
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    
    -- What was changed
    entity_type VARCHAR(100) NOT NULL, -- audit_engagement, working_paper, trial_balance, etc.
    entity_id UUID NOT NULL,
    
    -- Action
    action VARCHAR(50) NOT NULL, -- created, updated, deleted, approved, rejected
    
    -- Who and when
    user_id UUID REFERENCES firm_users(id),
    user_name VARCHAR(255),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address VARCHAR(50),
    user_agent TEXT
);

CREATE INDEX idx_audit_trail_firm ON audit_trail(firm_id);
CREATE INDEX idx_audit_trail_entity ON audit_trail(entity_type, entity_id);
CREATE INDEX idx_audit_trail_user ON audit_trail(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(timestamp);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification queries
-- SELECT COUNT(*) FROM audit_engagements;
-- SELECT COUNT(*) FROM working_papers;
-- SELECT COUNT(*) FROM trial_balance;
