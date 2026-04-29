-- CPAOS tables — run once in Supabase SQL Editor (requires pgcrypto for gen_random_uuid).
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS firms (
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

CREATE TABLE IF NOT EXISTS firm_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    supabase_user_id VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'staff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clients (
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

CREATE UNIQUE INDEX IF NOT EXISTS clients_onboarding_link_key ON clients (onboarding_link);

CREATE TABLE IF NOT EXISTS checklist_items (
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
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS documents (
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

CREATE TABLE IF NOT EXISTS whatsapp_logs (
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

CREATE TABLE IF NOT EXISTS onboarding_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    action VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    performed_by VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clients_firm_id ON clients (firm_id);
CREATE INDEX IF NOT EXISTS idx_checklist_client_id ON checklist_items (client_id);
CREATE INDEX IF NOT EXISTS idx_documents_client_firm ON documents (client_id, firm_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_client ON whatsapp_logs (client_id);
CREATE INDEX IF NOT EXISTS idx_activity_firm_created ON onboarding_activity (firm_id, created_at DESC);
