# DATABASE SCHEMA AUDIT
## CPAOS - Existing Database Structure

**Audit Date:** November 16, 2026

---

## OVERVIEW

The existing CPAOS database uses **PostgreSQL on Supabase** with a clean, normalized schema. The design follows these principles:

- ✅ Multi-tenant isolation via `firm_id` foreign keys
- ✅ UUID primary keys for all tables
- ✅ Timestamped records (`created_at`, `updated_at`)
- ✅ Proper foreign key relationships with CASCADE deletes
- ✅ Indexed columns for query performance
- ✅ JSONB for flexible data (services, issues)
- ✅ Enum-like VARCHAR constraints

**Total Tables:** 7 core tables  
**Extension Needed:** pgcrypto (for UUID generation)

---

## EXISTING TABLES

### 1. `firms`

**Purpose:** Multi-tenant firm accounts (CA firms, accounting firms)

```sql
CREATE TABLE firms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(128) NOT NULL UNIQUE,
    country VARCHAR(64) NOT NULL DEFAULT 'India',
    logo_url VARCHAR(1024),
    primary_color VARCHAR(16) NOT NULL DEFAULT '#2563EB',
    whatsapp_number VARCHAR(32),
    plan VARCHAR(32) NOT NULL DEFAULT 'starter',
    plan_client_limit INTEGER NOT NULL DEFAULT 10,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE on `slug`

**Data:**
- `plan` values: `starter`, `pro`, `agency`
- `plan_client_limit`: 10, 50, or 999999
- `country`: India, UAE, UK, US, Singapore, Australia, Other

**Tenant Isolation:** This is the root tenant table. Every other table references `firm_id`.

**Assessment:** ✅ **Solid foundation**. Add fields for:
- `address`, `city`, `state`, `pincode`, `gstin`, `pan`, `website`
- `founded_year`, `firm_type` (proprietorship, partnership, LLP, company)
- `subscription_start_date`, `subscription_end_date`
- `billing_email`, `technical_contact_email`

---

### 2. `firm_users`

**Purpose:** Staff members and firm owners (authenticated users)

```sql
CREATE TABLE firm_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    supabase_user_id VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'staff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Roles:**
- `owner` - Firm owner
- `admin` - Administrator
- `staff` - Staff member

**Assessment:** ⚠️ **Needs extension** for CA practice features:

**Add Fields:**
- `designation` VARCHAR(100) - Manager, Senior Accountant, Article
- `department` VARCHAR(100) - Audit, Tax, Accounting
- `employee_code` VARCHAR(50)
- `phone` VARCHAR(32)
- `date_of_joining` DATE
- `reporting_to` UUID REFERENCES firm_users(id) - Manager hierarchy
- `cost_per_hour` DECIMAL(10,2) - For billing calculations
- `address`, `city`, `state`, `pincode`
- `updated_at` TIMESTAMPTZ

**New Roles Needed:**
- `managing_partner`
- `partner`
- `manager`
- `senior_accountant`
- `accountant`
- `article_assistant`

---

### 3. `clients`

**Purpose:** Client records for onboarding and engagement

```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_name VARCHAR(255) NOT NULL,
    business_name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(32) NOT NULL,
    country VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    services JSONB NOT NULL DEFAULT '[]'::jsonb,
    industry VARCHAR(255),
    financial_year_end VARCHAR(32),
    status VARCHAR(64) NOT NULL DEFAULT 'invited',
    completion_pct INTEGER NOT NULL DEFAULT 0,
    onboarding_link VARCHAR(512) NOT NULL,
    onboarding_token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    assigned_to UUID REFERENCES firm_users(id),
    engagement_letter_sent BOOLEAN NOT NULL DEFAULT FALSE,
    engagement_letter_signed BOOLEAN NOT NULL DEFAULT FALSE,
    signature_envelope_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX clients_onboarding_link_key ON clients (onboarding_link);
CREATE INDEX idx_clients_firm_id ON clients (firm_id);
```

**Entity Types:**
- individual, sole_proprietor, partnership, llp, private_limited, public_limited, trust, llc, s_corp, c_corp, other

**Status Values:**
- invited, signature_pending, in_progress, documents_pending, under_review, completed, active

**Assessment:** ✅ **Good core structure**. Extend for CA practice:

**Add Fields:**
- `client_code` VARCHAR(50) UNIQUE - Auto-generated client code
- `pan` VARCHAR(20) - PAN number
- `tan` VARCHAR(20) - TAN number
- `gstin` VARCHAR(20) - GSTIN
- `cin` VARCHAR(30) - CIN for companies
- `registered_address` TEXT
- `city` VARCHAR(100)
- `state` VARCHAR(100)
- `pincode` VARCHAR(20)
- `billing_address` TEXT
- `primary_contact_person` VARCHAR(255)
- `secondary_contact_person` VARCHAR(255)
- `secondary_phone` VARCHAR(32)
- `accounting_year_start` DATE
- `accounting_year_end` DATE
- `client_since` DATE
- `client_category` VARCHAR(50) - Premium, Standard, Basic
- `risk_classification` VARCHAR(50) - High, Medium, Low
- `billing_cycle` VARCHAR(50) - Monthly, Quarterly, Yearly
- `payment_terms` VARCHAR(50) - Immediate, 15 days, 30 days
- `partner_in_charge` UUID REFERENCES firm_users(id)
- `manager_in_charge` UUID REFERENCES firm_users(id)
- `related_group` VARCHAR(255) - Group companies
- `is_active` BOOLEAN DEFAULT TRUE
- `deactivation_date` DATE
- `deactivation_reason` TEXT
- `updated_at` TIMESTAMPTZ

---

### 4. `checklist_items`

**Purpose:** Document collection checklist for client onboarding

```sql
CREATE TABLE checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    category VARCHAR(128) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    document_id UUID,
    waived_reason TEXT,
    waived_by UUID REFERENCES firm_users(id),
    display_order INTEGER NOT NULL DEFAULT 0,
    expiry_date DATE
);

CREATE INDEX idx_checklist_client_id ON checklist_items (client_id);
CREATE INDEX idx_checklist_expiry_date ON checklist_items (expiry_date) 
    WHERE expiry_date IS NOT NULL;
```

**Status Values:**
- pending, uploaded, verified, rejected, waived

**Categories (India example):**
- Identity, Business, Tax, Financial, MCA

**Assessment:** ✅ **Well-designed**. This table can be reused for:
- Client onboarding checklists (current use)
- Assignment checklists (extend with `assignment_id` nullable FK)
- General compliance tracking

**Potential Extension:**
- Add `assignment_id UUID REFERENCES assignments(id)` - Link to assignment instead of just client
- Add `created_at`, `updated_at` timestamps

---

### 5. `documents`

**Purpose:** Uploaded documents with AI classification

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES checklist_items(id),
    filename VARCHAR(512) NOT NULL,
    original_filename VARCHAR(512) NOT NULL,
    storage_path VARCHAR(1024) NOT NULL,
    storage_bucket VARCHAR(128) NOT NULL DEFAULT 'cpaos-documents',
    file_size INTEGER NOT NULL DEFAULT 0,
    mime_type VARCHAR(128) NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by VARCHAR(64) NOT NULL,
    ai_document_type VARCHAR(255),
    ai_confidence DOUBLE PRECISION,
    ai_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ai_issues JSONB NOT NULL DEFAULT '[]'::jsonb,
    reviewed_by UUID REFERENCES firm_users(id),
    reviewed_at TIMESTAMPTZ,
    review_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    rejection_reason TEXT
);

CREATE INDEX idx_documents_client_firm ON documents (client_id, firm_id);
```

**Review Status:**
- pending, approved, rejected

**Assessment:** ✅ **Excellent structure**. Extend for CA practice:

**Add Fields:**
- `assignment_id UUID REFERENCES assignments(id)` - Link to assignment
- `document_category` VARCHAR(100) - Tax, Audit, Accounting, Statutory
- `financial_year` VARCHAR(20) - FY 2023-24
- `document_date` DATE - Date on the document
- `period_start` DATE - For periodic documents (bank statements)
- `period_end` DATE
- `version_number` INTEGER - Document versioning
- `replaced_by` UUID REFERENCES documents(id) - For version tracking
- `tags` JSONB - Flexible tagging
- `is_archived` BOOLEAN DEFAULT FALSE

---

### 6. `whatsapp_logs`

**Purpose:** Communication history (WhatsApp and SMS)

```sql
CREATE TABLE whatsapp_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    channel VARCHAR(32) NOT NULL DEFAULT 'whatsapp',
    message_type VARCHAR(64) NOT NULL,
    phone_number VARCHAR(32) NOT NULL,
    message_content TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'sent',
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_whatsapp_client ON whatsapp_logs (client_id);
```

**Channels:**
- whatsapp, sms

**Status:**
- sent, delivered, failed

**Assessment:** ✅ **Good for communication logging**. Consider:

**Rename to:** `communication_logs` (more generic)

**Add Fields:**
- `direction` VARCHAR(20) - inbound, outbound
- `message_id` VARCHAR(255) - External provider message ID
- `error_message` TEXT - If delivery failed
- `delivered_at` TIMESTAMPTZ
- `read_at` TIMESTAMPTZ
- `reply_to_message_id` UUID REFERENCES communication_logs(id) - Threading

---

### 7. `onboarding_activity`

**Purpose:** Audit trail for all client actions

```sql
CREATE TABLE onboarding_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    action VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    performed_by VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activity_firm_created ON onboarding_activity (firm_id, created_at DESC);
```

**Assessment:** ✅ **Good audit trail design**. Consider:

**Rename to:** `activity_logs` (more generic)

**Add Fields:**
- `entity_type` VARCHAR(50) - client, assignment, document, invoice, etc.
- `entity_id` UUID - Generic reference to any entity
- `user_id` UUID REFERENCES firm_users(id) - Link to actual user
- `ip_address` VARCHAR(50)
- `user_agent` TEXT
- `changes` JSONB - Before/after values for updates

---

## MISSING TABLES FOR CA PRACTICE OS

### 1. `assignments` ⚠️ CRITICAL NEW TABLE

**Purpose:** Core practice management - client assignments/tasks

```sql
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    assignment_code VARCHAR(50) UNIQUE,
    assignment_name VARCHAR(255) NOT NULL,
    service_category VARCHAR(100) NOT NULL, -- GST, Income Tax, TDS, Audit, Accounting, MCA
    assignment_type VARCHAR(100) NOT NULL, -- GSTR-1, ITR, Statutory Audit, etc.
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
    status VARCHAR(50) DEFAULT 'created', -- created, assigned, in_progress, submitted, review, approved, completed
    completion_pct INTEGER DEFAULT 0,
    estimated_hours DECIMAL(10,2),
    actual_hours DECIMAL(10,2),
    billing_status VARCHAR(50) DEFAULT 'pending', -- pending, invoiced, paid
    invoice_id UUID, -- References invoices table
    description TEXT,
    internal_notes TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100), -- monthly, quarterly, yearly
    parent_assignment_id UUID REFERENCES assignments(id), -- For recurring assignments
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assignments_firm ON assignments(firm_id);
CREATE INDEX idx_assignments_client ON assignments(client_id);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);
CREATE INDEX idx_assignments_status ON assignments(status);
CREATE INDEX idx_assignments_assigned_partner ON assignments(assigned_partner);
```

---

### 2. `assignment_reviews` ⚠️ CRITICAL NEW TABLE

**Purpose:** Review workflow for assignments

```sql
CREATE TABLE assignment_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES firm_users(id),
    review_level VARCHAR(50) NOT NULL, -- manager, partner
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, changes_requested
    comments TEXT,
    checklist JSONB, -- Review checklist items
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assignment_reviews_assignment ON assignment_reviews(assignment_id);
CREATE INDEX idx_assignment_reviews_reviewer ON assignment_reviews(reviewer_id);
```

---

### 3. `compliance_obligations` ⚠️ CRITICAL NEW TABLE

**Purpose:** Statutory compliance rules and due dates

```sql
CREATE TABLE compliance_obligations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID REFERENCES firms(id) ON DELETE CASCADE, -- NULL = system-wide default
    country VARCHAR(64) NOT NULL,
    compliance_type VARCHAR(100) NOT NULL, -- GST, TDS, Income Tax, MCA, VAT, CT
    compliance_name VARCHAR(255) NOT NULL, -- GSTR-1, GSTR-3B, 26AS, etc.
    description TEXT,
    frequency VARCHAR(50), -- monthly, quarterly, yearly, one-time
    applicable_to JSONB, -- Entity types this applies to
    due_date_rule VARCHAR(255), -- "7th of next month", "30th July", etc.
    reminder_days_before INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_obligations_country ON compliance_obligations(country);
CREATE INDEX idx_compliance_obligations_type ON compliance_obligations(compliance_type);
```

---

### 4. `compliance_filings` ⚠️ NEW TABLE

**Purpose:** Track client compliance filings

```sql
CREATE TABLE compliance_filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    obligation_id UUID REFERENCES compliance_obligations(id),
    compliance_type VARCHAR(100) NOT NULL,
    compliance_name VARCHAR(255) NOT NULL,
    period_start DATE,
    period_end DATE,
    due_date DATE NOT NULL,
    filed_date DATE,
    acknowledgement_number VARCHAR(255),
    acknowledgement_document_id UUID REFERENCES documents(id),
    status VARCHAR(50) DEFAULT 'pending', -- pending, filed, overdue
    assigned_to UUID REFERENCES firm_users(id),
    reviewed_by UUID REFERENCES firm_users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_filings_client ON compliance_filings(client_id);
CREATE INDEX idx_compliance_filings_due_date ON compliance_filings(due_date);
CREATE INDEX idx_compliance_filings_status ON compliance_filings(status);
```

---

### 5. `invoices` ⚠️ CRITICAL NEW TABLE

**Purpose:** Billing and invoicing

```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    financial_year VARCHAR(20),
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    paid_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    balance_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, partial, paid, overdue, cancelled
    payment_terms VARCHAR(100),
    notes TEXT,
    internal_notes TEXT,
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoices_firm ON invoices(firm_id);
CREATE INDEX idx_invoices_client ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
```

---

### 6. `invoice_items` ⚠️ NEW TABLE

**Purpose:** Line items for invoices

```sql
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES assignments(id),
    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity DECIMAL(10,2) DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
```

---

### 7. `payments` ⚠️ NEW TABLE

**Purpose:** Payment tracking

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id),
    payment_number VARCHAR(50) UNIQUE,
    payment_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_mode VARCHAR(50), -- cash, cheque, bank_transfer, upi, card
    reference_number VARCHAR(255),
    notes TEXT,
    created_by UUID REFERENCES firm_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_firm ON payments(firm_id);
CREATE INDEX idx_payments_client ON payments(client_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
```

---

### 8. `timesheets` ⚠️ NEW TABLE

**Purpose:** Staff time tracking

```sql
CREATE TABLE timesheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES firm_users(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES assignments(id),
    client_id UUID REFERENCES clients(id),
    date DATE NOT NULL,
    hours DECIMAL(5,2) NOT NULL,
    description TEXT,
    is_billable BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, approved, rejected
    approved_by UUID REFERENCES firm_users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timesheets_user ON timesheets(user_id);
CREATE INDEX idx_timesheets_assignment ON timesheets(assignment_id);
CREATE INDEX idx_timesheets_date ON timesheets(date);
```

---

### 9. `audit_engagements` ⚠️ NEW TABLE

**Purpose:** Audit-specific engagements

```sql
CREATE TABLE audit_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    engagement_name VARCHAR(255) NOT NULL,
    engagement_type VARCHAR(100), -- statutory_audit, internal_audit, tax_audit
    financial_year VARCHAR(20) NOT NULL,
    audit_partner UUID REFERENCES firm_users(id),
    audit_manager UUID REFERENCES firm_users(id),
    audit_team JSONB, -- Array of user IDs
    planning_materiality DECIMAL(15,2),
    risk_assessment VARCHAR(50), -- low, medium, high
    start_date DATE,
    fieldwork_start_date DATE,
    fieldwork_end_date DATE,
    report_date DATE,
    status VARCHAR(50) DEFAULT 'planning',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_engagements_client ON audit_engagements(client_id);
CREATE INDEX idx_audit_engagements_partner ON audit_engagements(audit_partner);
```

---

### 10. `audit_workpapers` ⚠️ NEW TABLE

**Purpose:** Audit working papers

```sql
CREATE TABLE audit_workpapers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES audit_engagements(id) ON DELETE CASCADE,
    section VARCHAR(100), -- planning, risk_assessment, testing, review
    reference_number VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_id UUID REFERENCES documents(id),
    prepared_by UUID REFERENCES firm_users(id),
    reviewed_by UUID REFERENCES firm_users(id),
    status VARCHAR(50) DEFAULT 'draft', -- draft, prepared, reviewed, approved
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_workpapers_engagement ON audit_workpapers(engagement_id);
```

---

### 11. `notifications` ⚠️ NEW TABLE

**Purpose:** In-app notifications

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES firm_users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50), -- assignment, document, compliance, payment, system
    entity_type VARCHAR(50), -- assignment, client, invoice, etc.
    entity_id UUID,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

---

## SUMMARY: DATABASE TRANSFORMATION PLAN

### ✅ KEEP AS-IS (7 tables)
1. firms
2. firm_users (extend with new fields)
3. clients (extend with new fields)
4. checklist_items (extend for assignments)
5. documents (extend for assignments)
6. whatsapp_logs (rename to communication_logs)
7. onboarding_activity (rename to activity_logs, make generic)

### ⚠️ ADD NEW TABLES (11 tables)
1. assignments ⭐ CRITICAL
2. assignment_reviews ⭐ CRITICAL
3. compliance_obligations ⭐ CRITICAL
4. compliance_filings
5. invoices ⭐ CRITICAL
6. invoice_items
7. payments
8. timesheets
9. audit_engagements
10. audit_workpapers
11. notifications

### 📊 TOTAL SCHEMA
- **Existing:** 7 tables
- **New:** 11 tables
- **Total:** 18 tables

### 🔐 ROW LEVEL SECURITY (RLS)
**Not currently implemented.** Recommend enabling RLS on all tables with policies:
- Staff can only access their firm's data (`firm_id = current_firm_id()`)
- Clients can only access their own records
- Partners/managers can access team assignments

### 📈 MIGRATION STRATEGY
1. **Phase 1:** Extend existing tables (add columns)
2. **Phase 2:** Add assignment and compliance tables
3. **Phase 3:** Add billing tables
4. **Phase 4:** Add audit tables
5. **Phase 5:** Add notifications

**No data loss. All existing tables and data preserved.**
