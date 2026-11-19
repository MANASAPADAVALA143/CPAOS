"""
GNANOVA CA PRACTICE OS - AI Copilot API Routes
Phase 5: API endpoints for AI agents
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.models import FirmUser
from app.services.ai_copilot import (
    client_onboarding_agent,
    document_intelligence_agent,
    compliance_monitoring_agent,
    collections_agent,
)

router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class AgentQueryRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}


class ApproveActionRequest(BaseModel):
    action_id: str
    approved: bool
    reason: Optional[str] = None


# ============================================================================
# CLIENT ONBOARDING AGENT ENDPOINTS
# ============================================================================

@router.post("/onboarding/query")
async def query_onboarding_agent(
    data: AgentQueryRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """
    Query the Client Onboarding Agent
    
    Example:
    {
        "query": "Help me onboard a new company client XYZ Ltd",
        "context": {
            "client_name": "XYZ Ltd",
            "client_type": "company",
            "document_text": "..."
        }
    }
    """
    execution = await client_onboarding_agent.process_query(
        query=data.query,
        context=data.context,
        sb=sb,
        firm_id=current.firm_id,
        user_id=current.id,
    )
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "result": execution.result,
        "logs": execution.logs,
        "actions": [
            {
                "id": a.id,
                "type": a.action_type,
                "description": a.description,
                "requires_approval": a.requires_approval,
                "risk_level": a.risk_level,
                "status": a.status,
            }
            for a in execution.actions
        ],
    }


# ============================================================================
# DOCUMENT INTELLIGENCE AGENT ENDPOINTS
# ============================================================================

@router.post("/document-intelligence/query")
async def query_document_intelligence_agent(
    data: AgentQueryRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """
    Query the Document Intelligence Agent
    
    Example:
    {
        "query": "Extract invoice data from this document",
        "context": {
            "document_id": "uuid",
            "document_type": "invoice",
            "document_text": "..."
        }
    }
    """
    execution = await document_intelligence_agent.process_query(
        query=data.query,
        context=data.context,
        sb=sb,
        firm_id=current.firm_id,
        user_id=current.id,
    )
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "result": execution.result,
        "logs": execution.logs,
        "actions": [
            {
                "id": a.id,
                "type": a.action_type,
                "description": a.description,
                "requires_approval": a.requires_approval,
                "status": a.status,
            }
            for a in execution.actions
        ],
    }


# ============================================================================
# COMPLIANCE MONITORING AGENT ENDPOINTS
# ============================================================================

@router.post("/compliance-monitoring/query")
async def query_compliance_monitoring_agent(
    data: AgentQueryRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """
    Query the Compliance Monitoring Agent
    
    Example:
    {
        "query": "Show me all overdue compliances and suggest actions",
        "context": {
            "time_horizon": 30
        }
    }
    """
    execution = await compliance_monitoring_agent.process_query(
        query=data.query,
        context=data.context,
        sb=sb,
        firm_id=current.firm_id,
        user_id=current.id,
    )
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "result": execution.result,
        "logs": execution.logs,
        "actions": [
            {
                "id": a.id,
                "type": a.action_type,
                "description": a.description,
                "requires_approval": a.requires_approval,
                "status": a.status,
            }
            for a in execution.actions
        ],
    }


# ============================================================================
# COLLECTIONS AGENT ENDPOINTS
# ============================================================================

@router.post("/collections/query")
async def query_collections_agent(
    data: AgentQueryRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """
    Query the Collections Assistance Agent
    
    Example:
    {
        "query": "Analyze overdue invoices and suggest collection actions",
        "context": {}
    }
    """
    execution = await collections_agent.process_query(
        query=data.query,
        context=data.context,
        sb=sb,
        firm_id=current.firm_id,
        user_id=current.id,
    )
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "result": execution.result,
        "logs": execution.logs,
        "actions": [
            {
                "id": a.id,
                "type": a.action_type,
                "description": a.description,
                "requires_approval": a.requires_approval,
                "status": a.status,
            }
            for a in execution.actions
        ],
    }


# ============================================================================
# ACTION APPROVAL ENDPOINTS
# ============================================================================

@router.post("/actions/approve")
async def approve_action(
    data: ApproveActionRequest,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Approve or reject an AI agent action"""
    
    # Try all agents
    agents = [
        client_onboarding_agent,
        document_intelligence_agent,
        compliance_monitoring_agent,
        collections_agent,
    ]
    
    for agent in agents:
        if data.approved:
            if agent.approve_action(data.action_id, current.id):
                return {
                    "success": True,
                    "action_id": data.action_id,
                    "status": "approved",
                    "message": "Action approved successfully"
                }
        else:
            if agent.reject_action(data.action_id, current.id, data.reason or "Rejected by user"):
                return {
                    "success": True,
                    "action_id": data.action_id,
                    "status": "rejected",
                    "message": "Action rejected"
                }
    
    raise HTTPException(status_code=404, detail="Action not found")


@router.post("/actions/{action_id}/execute")
async def execute_action(
    action_id: str,
    current: FirmUser = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Execute an approved action"""
    
    # Try all agents
    agents = [
        client_onboarding_agent,
        document_intelligence_agent,
        compliance_monitoring_agent,
        collections_agent,
    ]
    
    for agent in agents:
        for execution in agent.executions.values():
            for action in execution.actions:
                if action.id == action_id:
                    if action.status != "approved":
                        raise HTTPException(status_code=400, detail="Action not approved")
                    
                    result = await agent.execute_action(action, sb, current.firm_id, current.id)
                    return result
    
    raise HTTPException(status_code=404, detail="Action not found")


# ============================================================================
# AGENT INFO ENDPOINTS
# ============================================================================

@router.get("/agents")
async def list_agents(
    current: FirmUser = Depends(get_current_user),
):
    """List all available AI agents"""
    
    agents = [
        client_onboarding_agent,
        document_intelligence_agent,
        compliance_monitoring_agent,
        collections_agent,
    ]
    
    return {
        "agents": [agent.get_agent_info() for agent in agents]
    }


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    current: FirmUser = Depends(get_current_user),
):
    """Get execution details"""
    
    agents = [
        client_onboarding_agent,
        document_intelligence_agent,
        compliance_monitoring_agent,
        collections_agent,
    ]
    
    for agent in agents:
        execution = agent.get_execution(execution_id)
        if execution:
            return {
                "execution_id": execution.id,
                "agent_name": execution.agent_name,
                "query": execution.query,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "logs": execution.logs,
                "actions": [
                    {
                        "id": a.id,
                        "type": a.action_type,
                        "description": a.description,
                        "status": a.status,
                        "requires_approval": a.requires_approval,
                    }
                    for a in execution.actions
                ],
                "result": execution.result,
                "error": execution.error,
            }
    
    raise HTTPException(status_code=404, detail="Execution not found")
