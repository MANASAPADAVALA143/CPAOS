-- GNANOVA CA PRACTICE OS - Phase 1 Database Migrations
-- Migration: 001_phase1_foundation
-- Date: 2026-11-16
-- Description: Extend existing tables and create assignment management tables

-- ============================================================================
-- PART 1: EXTEND EXISTING TABLES
-- ============================================================================

-- Extend clients table with CA practice fields
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_code VARCHAR(50) UNIQUE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pan VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS gstin VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS tan VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS cin VARCHAR(30);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_category VARCHAR(50) DEFAULT 'Standard';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS risk_classification VARCHAR(50) DEFAULT 'Medium';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS partner_in_charge UUID REFERENCES firm_users(id);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS manager_in_charge UUID REFERENCES firm_users(id);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS registered_address TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS state VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pincode VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS accounting_year_start DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS accounting_year_end DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_since DATE DEFAULT CURRENT_DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Extend firm_users table with employee details
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS designation VARCHAR(100);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS department VARCHAR(100);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS employee_code VARCHAR(50);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS phone VARCHAR(32);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS date_of_joining DATE;
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS reporting_to UUID REFERENCES firm_users(id);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS cost_per_hour DECIMAL(10,2);
ALTER TABLE firm_users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Add non-FK columns to documents and checklist_items now
ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_category VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS financial_year VARCHAR(20);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_date DATE;

-- Create indexes on existing foreign keys for performance
CREATE INDEX IF NOT EXISTS idx_clients_partner ON clients(partner_in_charge) WHERE partner_in_charge IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clients_manager ON clients(manager_in_charge) WHERE manager_in_charge IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_firm_users_reporting ON firm_users(reporting_to) WHERE reporting_to IS NOT NULL;

-- ============================================================================
-- PART 2: CREATE ASSIGNMENT MANAGEMENT TABLES
-- ============================================================================

-- assignments table (CORE TABLE for CA practice management)
CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    assignment_code VARCHAR(50) UNIQUE,
    assignment_name VARCHAR(255) NOT NULL,
    service_category VARCHAR(100) NOT NULL, -- GST, Income Tax, TDS, MCA, Audit, Accounting
    assignment_type VARCHAR(100) NOT NULL,  -- GSTR-1, ITR, Statutory Audit, etc.
    financial_year VARCHAR(20) NOT NULL,
    period_start DATE,
    period_end DATE,
    assigned_partner UUID REFERENCES firm_users(id),
    assigned_manager UUID REFERENCES firm_users(id),
    assigned_staff UUID REFERENCES firm_users(id),
    start_date DATE,
    due_date DATE NOT NULL,
    completed_date DATE,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'created',  -- created, assigned, in_progress, submitted, manager_review, partner_review, approved, completed
    completion_pct INTEGER DEFAULT 0,
    estimated_hours DECIMAL(10,2),
    actual_hours DECIMAL(10,2),
    description TEXT,
    internal_notes TEXT,
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for assignments table
CREATE INDEX IF NOT EXISTS idx_assignments_firm ON assignments(firm_id);
CREATE INDEX IF NOT EXISTS idx_assignments_client ON assignments(client_id);
CREATE INDEX IF NOT EXISTS idx_assignments_due_date ON assignments(due_date);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);
CREATE INDEX IF NOT EXISTS idx_assignments_partner ON assignments(assigned_partner) WHERE assigned_partner IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assignments_manager ON assignments(assigned_manager) WHERE assigned_manager IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assignments_staff ON assignments(assigned_staff) WHERE assigned_staff IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assignments_category ON assignments(service_category);
CREATE INDEX IF NOT EXISTS idx_assignments_fy ON assignments(financial_year);

-- assignment_reviews table (for manager and partner review workflow)
CREATE TABLE IF NOT EXISTS assignment_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES firm_users(id),
    review_level VARCHAR(50) NOT NULL, -- manager, partner
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, changes_requested
    comments TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assignment_reviews_assignment ON assignment_reviews(assignment_id);
CREATE INDEX IF NOT EXISTS idx_assignment_reviews_reviewer ON assignment_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_assignment_reviews_status ON assignment_reviews(status);
CREATE INDEX IF NOT EXISTS idx_assignment_reviews_level ON assignment_reviews(review_level);

-- ============================================================================
-- PART 3: ASSIGNMENT CODE SEQUENCE
-- ============================================================================

-- Create a sequence for assignment codes (per firm)
-- We'll use this in the application to generate: ASG-2024-0001, ASG-2024-0002, etc.
CREATE SEQUENCE IF NOT EXISTS assignment_code_seq START WITH 1 INCREMENT BY 1;

-- ============================================================================
-- PART 4: UPDATE EXISTING ACTIVITY LOG TO BE MORE GENERIC
-- ============================================================================

-- Rename onboarding_activity to activity_logs for generic use
ALTER TABLE onboarding_activity RENAME TO activity_logs;

-- Add new columns for generic activity tracking
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS entity_type VARCHAR(50) DEFAULT 'client';
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS entity_id UUID;
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES firm_users(id);

-- Update existing records to set entity_type and entity_id
UPDATE activity_logs SET entity_type = 'client', entity_id = client_id WHERE entity_type IS NULL;

-- Create index for new columns
CREATE INDEX IF NOT EXISTS idx_activity_logs_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id) WHERE user_id IS NOT NULL;

-- ============================================================================
-- PART 5: COMMUNICATION LOGS ENHANCEMENT
-- ============================================================================

-- Rename whatsapp_logs to communication_logs for generic use
ALTER TABLE whatsapp_logs RENAME TO communication_logs;

-- Add direction field (inbound/outbound)
ALTER TABLE communication_logs ADD COLUMN IF NOT EXISTS direction VARCHAR(20) DEFAULT 'outbound';

-- ============================================================================
-- PART 6: INSERT DEFAULT DATA
-- ============================================================================

-- Insert default assignment service categories and types
-- (Application will reference these, but they can be configurable later)

-- Note: We'll handle service categories and types in the application code
-- as enums for now, but this provides a structure for future customization

-- ============================================================================
-- PART 7: LINK DOCUMENTS AND CHECKLIST TO ASSIGNMENTS
-- ============================================================================

-- Now that assignments table exists, add foreign key columns
ALTER TABLE documents ADD COLUMN IF NOT EXISTS assignment_id UUID REFERENCES assignments(id);
ALTER TABLE checklist_items ADD COLUMN IF NOT EXISTS assignment_id UUID REFERENCES assignments(id);

-- Create indexes on assignment foreign keys
CREATE INDEX IF NOT EXISTS idx_documents_assignment ON documents(assignment_id) WHERE assignment_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_checklist_assignment ON checklist_items(assignment_id) WHERE assignment_id IS NOT NULL;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification queries (run these to verify migration)
-- SELECT COUNT(*) FROM assignments; -- Should return 0 initially
-- SELECT COUNT(*) FROM assignment_reviews; -- Should return 0 initially
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'clients' AND column_name = 'client_code'; -- Should return client_code
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'firm_users' AND column_name = 'designation'; -- Should return designation
