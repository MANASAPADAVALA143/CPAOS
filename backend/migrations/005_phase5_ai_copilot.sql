-- GNANOVA CA PRACTICE OS - Phase 5 Database Migration
-- Migration: 005_phase5_ai_copilot
-- Date: 2026-11-18
-- Description: AI Copilot - Agent execution logs and approval workflows

-- ============================================================================
-- AI AGENT EXECUTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_agent_executions (
    id UUID PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES firm_users(id) ON DELETE CASCADE,
    
    query TEXT NOT NULL,
    
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    
    status VARCHAR(50) NOT NULL DEFAULT 'running', -- running, completed, failed
    
    logs JSONB,
    actions JSONB,
    result JSONB,
    error TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_agent_executions_firm ON ai_agent_executions(firm_id);
CREATE INDEX idx_ai_agent_executions_user ON ai_agent_executions(user_id);
CREATE INDEX idx_ai_agent_executions_agent ON ai_agent_executions(agent_name);
CREATE INDEX idx_ai_agent_executions_status ON ai_agent_executions(status);
CREATE INDEX idx_ai_agent_executions_started ON ai_agent_executions(started_at DESC);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
