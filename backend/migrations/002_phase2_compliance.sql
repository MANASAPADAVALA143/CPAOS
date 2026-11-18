-- GNANOVA CA PRACTICE OS - Phase 2 Database Migrations
-- Migration: 002_phase2_compliance
-- Date: 2026-11-18
-- Description: Compliance calendars, reminders, escalation rules, and document tracking

-- ============================================================================
-- PART 1: COMPLIANCE TEMPLATES (Master Compliance Rules)
-- ============================================================================

-- compliance_templates: Configurable compliance rules by country
CREATE TABLE IF NOT EXISTS compliance_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID REFERENCES firms(id) ON DELETE CASCADE, -- NULL for system templates
    country VARCHAR(10) NOT NULL, -- IN, AE, etc.
    service_category VARCHAR(100) NOT NULL, -- GST, Income Tax, TDS, MCA, Audit
    compliance_name VARCHAR(255) NOT NULL,
    compliance_code VARCHAR(50), -- GSTR-1, GSTR-3B, ITR, etc.
    description TEXT,
    frequency VARCHAR(50) NOT NULL, -- monthly, quarterly, annual, event_based
    due_day_of_month INTEGER, -- For monthly (e.g., 20th of next month)
    due_month INTEGER, -- For annual (e.g., 7 for July)
    due_days_after_period_end INTEGER, -- For relative deadlines (e.g., 10 days after quarter end)
    applies_to_entity_types TEXT[], -- ['company', 'llp', 'partnership'] etc.
    is_active BOOLEAN DEFAULT true,
    is_system_template BOOLEAN DEFAULT false, -- System vs firm-specific
    documents_required TEXT[], -- List of required document types
    auto_create_assignment BOOLEAN DEFAULT true, -- Auto-create assignments
    priority VARCHAR(20) DEFAULT 'medium', -- Default priority
    estimated_hours DECIMAL(10,2), -- Default estimated hours
    penalty_info TEXT, -- Info about late filing penalties
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_templates_firm ON compliance_templates(firm_id) WHERE firm_id IS NOT NULL;
CREATE INDEX idx_compliance_templates_country ON compliance_templates(country);
CREATE INDEX idx_compliance_templates_category ON compliance_templates(service_category);
CREATE INDEX idx_compliance_templates_active ON compliance_templates(is_active) WHERE is_active = true;

-- ============================================================================
-- PART 2: COMPLIANCE REQUIREMENTS (Client-Specific Calendar)
-- ============================================================================

-- compliance_requirements: Client-specific compliance instances
CREATE TABLE IF NOT EXISTS compliance_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    template_id UUID REFERENCES compliance_templates(id) ON DELETE SET NULL,
    compliance_name VARCHAR(255) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    financial_year VARCHAR(20) NOT NULL, -- FY 2024-25
    period_start DATE, -- For quarterly, monthly
    period_end DATE,
    due_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, overdue, not_applicable
    completion_date DATE,
    assignment_id UUID REFERENCES assignments(id) ON DELETE SET NULL, -- Linked assignment
    assigned_to UUID REFERENCES firm_users(id), -- Staff assigned
    priority VARCHAR(20) DEFAULT 'medium',
    is_enabled BOOLEAN DEFAULT true, -- Can be disabled for specific clients
    notes TEXT,
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_req_firm ON compliance_requirements(firm_id);
CREATE INDEX idx_compliance_req_client ON compliance_requirements(client_id);
CREATE INDEX idx_compliance_req_due_date ON compliance_requirements(due_date);
CREATE INDEX idx_compliance_req_status ON compliance_requirements(status);
CREATE INDEX idx_compliance_req_assignment ON compliance_requirements(assignment_id) WHERE assignment_id IS NOT NULL;
CREATE INDEX idx_compliance_req_fy ON compliance_requirements(financial_year);
CREATE INDEX idx_compliance_req_category ON compliance_requirements(service_category);

-- ============================================================================
-- PART 3: COMPLIANCE REMINDERS (Reminder Rules)
-- ============================================================================

-- compliance_reminders: Configurable reminder and escalation rules
CREATE TABLE IF NOT EXISTS compliance_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    template_id UUID REFERENCES compliance_templates(id) ON DELETE CASCADE,
    reminder_name VARCHAR(255) NOT NULL,
    days_before_due INTEGER NOT NULL, -- Negative for after due (overdue reminders)
    reminder_type VARCHAR(50) NOT NULL, -- notification, email, whatsapp, escalation
    escalate_to_role VARCHAR(50), -- manager, partner (for escalations)
    is_active BOOLEAN DEFAULT true,
    message_template TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_reminders_firm ON compliance_reminders(firm_id);
CREATE INDEX idx_compliance_reminders_template ON compliance_reminders(template_id);
CREATE INDEX idx_compliance_reminders_active ON compliance_reminders(is_active) WHERE is_active = true;

-- ============================================================================
-- PART 4: COMPLIANCE ALERTS (Generated Notifications)
-- ============================================================================

-- compliance_alerts: Generated alerts and notifications
CREATE TABLE IF NOT EXISTS compliance_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    requirement_id UUID NOT NULL REFERENCES compliance_requirements(id) ON DELETE CASCADE,
    reminder_id UUID REFERENCES compliance_reminders(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL, -- reminder, overdue, escalation, completed
    severity VARCHAR(20) DEFAULT 'info', -- info, warning, critical
    recipient_id UUID NOT NULL REFERENCES firm_users(id), -- User to notify
    message TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    notification_sent BOOLEAN DEFAULT false, -- For email/WhatsApp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_alerts_firm ON compliance_alerts(firm_id);
CREATE INDEX idx_compliance_alerts_requirement ON compliance_alerts(requirement_id);
CREATE INDEX idx_compliance_alerts_recipient ON compliance_alerts(recipient_id);
CREATE INDEX idx_compliance_alerts_read ON compliance_alerts(read_at) WHERE read_at IS NULL;
CREATE INDEX idx_compliance_alerts_dismissed ON compliance_alerts(dismissed_at) WHERE dismissed_at IS NULL;
CREATE INDEX idx_compliance_alerts_sent ON compliance_alerts(sent_at);

-- ============================================================================
-- PART 5: DOCUMENT REQUIREMENTS (Document Tracking)
-- ============================================================================

-- document_requirements: Track required documents for compliance
CREATE TABLE IF NOT EXISTS document_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    requirement_id UUID NOT NULL REFERENCES compliance_requirements(id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(100), -- From compliance template
    is_mandatory BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'pending', -- pending, uploaded, verified, rejected
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL, -- Linked uploaded document
    uploaded_at TIMESTAMPTZ,
    verified_by UUID REFERENCES firm_users(id),
    verified_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_doc_req_firm ON document_requirements(firm_id);
CREATE INDEX idx_doc_req_requirement ON document_requirements(requirement_id);
CREATE INDEX idx_doc_req_status ON document_requirements(status);
CREATE INDEX idx_doc_req_document ON document_requirements(document_id) WHERE document_id IS NOT NULL;

-- ============================================================================
-- PART 6: ENHANCE EXISTING TABLES
-- ============================================================================

-- Add compliance tracking to assignments
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS compliance_requirement_id UUID REFERENCES compliance_requirements(id);
CREATE INDEX IF NOT EXISTS idx_assignments_compliance ON assignments(compliance_requirement_id) WHERE compliance_requirement_id IS NOT NULL;

-- Add compliance metadata to documents
ALTER TABLE documents ADD COLUMN IF NOT EXISTS compliance_requirement_id UUID REFERENCES compliance_requirements(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_statutory BOOLEAN DEFAULT false;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS statutory_period_start DATE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS statutory_period_end DATE;
CREATE INDEX IF NOT EXISTS idx_documents_compliance ON documents(compliance_requirement_id) WHERE compliance_requirement_id IS NOT NULL;

-- ============================================================================
-- PART 7: INSERT DEFAULT INDIA COMPLIANCE TEMPLATES
-- ============================================================================

-- GST Compliance Templates (India)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, due_day_of_month, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
-- Monthly GST Returns
('IN', 'GST', 'GSTR-1 Filing', 'GSTR-1', 'Details of outward supplies of goods and services', 'monthly', 11, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['Sales invoices', 'Credit notes', 'Debit notes'], true, 'high', 4.0, 'Late fee: Rs. 50 per day (max Rs. 10,000)'),
('IN', 'GST', 'GSTR-3B Filing', 'GSTR-3B', 'Summary return of outward and inward supplies', 'monthly', 20, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['GSTR-1', 'Purchase register', 'ITC statement'], true, 'high', 6.0, 'Late fee: Rs. 50 per day per act (CGST+SGST)'),

-- Quarterly GST Returns
('IN', 'GST', 'GSTR-3B Quarterly Filing (QRMP)', 'GSTR-3B-Q', 'Quarterly return for QRMP scheme taxpayers', 'quarterly', 22, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['GSTR-1', 'Purchase register', 'ITC statement'], true, 'high', 8.0, 'Late fee applicable'),

-- Annual GST Returns
('IN', 'GST', 'GSTR-9 Annual Return', 'GSTR-9', 'Annual return for regular taxpayers', 'annual', 31, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['All GSTR-1', 'All GSTR-3B', 'Purchase register', 'ITC reconciliation'], true, 'high', 16.0, 'Late fee: Rs. 200 per day (max 0.25% of turnover)'),
('IN', 'GST', 'GSTR-9C Reconciliation', 'GSTR-9C', 'Reconciliation statement and certification by CA/CMA', 'annual', 31, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['Audited financials', 'GSTR-9', 'Reconciliation statement'], true, 'high', 20.0, 'Late fee applicable if GSTR-9 is delayed');

-- Income Tax Compliance Templates (India)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, due_month, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('IN', 'Income Tax', 'ITR-3 Filing (Business)', 'ITR-3', 'Return for individuals/HUFs having business income', 'annual', 7, ARRAY['proprietorship', 'individual', 'huf'], true, ARRAY['P&L', 'Balance sheet', 'Books of accounts', 'Bank statements'], true, 'high', 12.0, 'Late fee: Rs. 5,000 (if filed by Dec 31), Rs. 10,000 thereafter'),
('IN', 'Income Tax', 'ITR-6 Filing (Company)', 'ITR-6', 'Return for companies other than section 11', 'annual', 10, ARRAY['company'], true, ARRAY['Audited financials', 'Tax audit report', 'Computation of income'], true, 'high', 16.0, 'Late fee: Rs. 10,000 (if filed by Dec 31), penalty thereafter'),
('IN', 'Income Tax', 'Tax Audit Report (Form 3CA/3CB/3CD)', 'TAR', 'Tax audit report for businesses exceeding threshold', 'annual', 9, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['Audited financials', 'Books of accounts', 'Supporting schedules'], true, 'high', 24.0, 'Penalty for non-filing: 0.5% of total sales/turnover');

-- TDS Compliance Templates (India)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, due_day_of_month, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('IN', 'TDS', 'TDS Return Filing (Form 24Q)', '24Q', 'Quarterly TDS return for salary', 'quarterly', 31, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['Salary register', 'Form 16', 'TDS payment challans'], true, 'high', 6.0, 'Late fee: Rs. 200 per day'),
('IN', 'TDS', 'TDS Return Filing (Form 26Q)', '26Q', 'Quarterly TDS return for payments other than salary', 'quarterly', 31, ARRAY['company', 'llp', 'partnership', 'proprietorship'], true, ARRAY['Payment register', 'TDS certificates', 'TDS payment challans'], true, 'high', 8.0, 'Late fee: Rs. 200 per day');

-- ============================================================================
-- PART 8: INSERT DEFAULT UAE COMPLIANCE TEMPLATES
-- ============================================================================

-- VAT Compliance Templates (UAE)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, due_day_of_month, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('AE', 'VAT', 'VAT Return Filing', 'VAT-201', 'Quarterly/Monthly VAT return filing', 'quarterly', 28, ARRAY['company', 'llp', 'fze', 'fzco'], true, ARRAY['Sales invoices', 'Purchase invoices', 'VAT account'], true, 'high', 8.0, 'Penalty: AED 1,000 for first offense, AED 2,000 thereafter'),
('AE', 'VAT', 'VAT Refund Application', 'VAT-311', 'Application for VAT refund (if applicable)', 'quarterly', 28, ARRAY['company', 'llp', 'fze', 'fzco'], true, ARRAY['VAT return', 'Supporting invoices', 'Bank details'], true, 'medium', 6.0, 'Delayed refund if not filed on time');

-- Corporate Tax Compliance (UAE) - Effective from June 2023
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, due_month, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('AE', 'Corporate Tax', 'Corporate Tax Return Filing', 'CT-1', 'Annual corporate tax return (9% on profits above AED 375,000)', 'annual', 9, ARRAY['company', 'fze', 'fzco'], true, ARRAY['Audited financials', 'Tax computation', 'Transfer pricing documentation'], true, 'high', 20.0, 'Penalty: AED 10,000 for late filing'),
('AE', 'Corporate Tax', 'Tax Registration', 'CT-REG', 'Registration for corporate tax (one-time)', 'event_based', NULL, ARRAY['company', 'fze', 'fzco'], true, ARRAY['Trade license', 'Emirates ID', 'Financials'], true, 'high', 4.0, 'Penalty for non-registration');

-- ESR Compliance (UAE)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('AE', 'ESR', 'Economic Substance Report Filing', 'ESR', 'Annual ESR filing for relevant activities', 'annual', ARRAY['company', 'fze', 'fzco'], true, ARRAY['Audited financials', 'CIGA test', 'Substance documentation'], true, 'high', 12.0, 'Penalty: AED 20,000 for first late filing, AED 50,000 thereafter');

-- Audit Requirements (UAE)
INSERT INTO compliance_templates (
    country, service_category, compliance_name, compliance_code, description,
    frequency, applies_to_entity_types, is_system_template,
    documents_required, auto_create_assignment, priority, estimated_hours, penalty_info
) VALUES
('AE', 'Audit', 'Annual Statutory Audit', 'AUDIT', 'Annual financial audit as per UAE Commercial Companies Law', 'annual', ARRAY['company', 'fze', 'fzco', 'llc'], true, ARRAY['Books of accounts', 'Bank statements', 'Supporting vouchers'], true, 'high', 40.0, 'Penalties for non-compliance with MoE');

-- ============================================================================
-- PART 9: DEFAULT REMINDER RULES
-- ============================================================================

-- Create default reminder rules for all compliance types
-- These will be applied unless firm creates custom rules

-- We'll handle this in application code for now, as it needs to reference template_id

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification queries (run these to verify migration)
-- SELECT COUNT(*) FROM compliance_templates WHERE country = 'IN'; -- Should return multiple India templates
-- SELECT COUNT(*) FROM compliance_templates WHERE country = 'AE'; -- Should return multiple UAE templates
-- SELECT compliance_name, frequency, due_day_of_month FROM compliance_templates WHERE service_category = 'GST';
