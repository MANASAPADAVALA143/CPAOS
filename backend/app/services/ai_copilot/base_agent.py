"""
GNANOVA CA PRACTICE OS - AI Copilot Base Agent
Phase 5: Base class for all AI agents with firm isolation and approval workflows
"""

from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from abc import ABC, abstractmethod
from supabase import Client
import json

from app.services.email_service import email_service


class AgentAction:
    """Represents an action that an agent wants to execute"""
    
    def __init__(
        self,
        action_type: str,
        description: str,
        parameters: Dict[str, Any],
        requires_approval: bool = True,
        risk_level: str = "medium",  # low, medium, high
    ):
        self.id = str(uuid4())
        self.action_type = action_type
        self.description = description
        self.parameters = parameters
        self.requires_approval = requires_approval
        self.risk_level = risk_level
        self.status = "pending"  # pending, approved, rejected, executed, failed
        self.created_at = datetime.now().isoformat()
        self.approved_at = None
        self.approved_by = None
        self.executed_at = None
        self.execution_result = None
        self.error = None


class AgentExecution:
    """Represents an agent execution session with logs"""
    
    def __init__(self, agent_name: str, firm_id: UUID, user_id: UUID, query: str):
        self.id = str(uuid4())
        self.agent_name = agent_name
        self.firm_id = str(firm_id)
        self.user_id = str(user_id)
        self.query = query
        self.started_at = datetime.now().isoformat()
        self.completed_at = None
        self.status = "running"  # running, completed, failed
        self.logs = []
        self.actions = []
        self.result = None
        self.error = None
    
    def log(self, message: str, level: str = "info"):
        """Add log entry"""
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        })
    
    def add_action(self, action: AgentAction):
        """Add action to execution"""
        self.actions.append(action)
    
    def complete(self, result: Any):
        """Mark execution as completed"""
        self.completed_at = datetime.now().isoformat()
        self.status = "completed"
        self.result = result
    
    def fail(self, error: str):
        """Mark execution as failed"""
        self.completed_at = datetime.now().isoformat()
        self.status = "failed"
        self.error = error


class BaseAIAgent(ABC):
    """
    Base class for all AI agents in GNANOVA CA Practice OS
    
    Features:
    - Firm isolation (all queries are firm-scoped)
    - Permission-aware data retrieval
    - Human approval for consequential actions
    - Execution logging
    - Error handling
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_description: str,
        capabilities: List[str],
    ):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.capabilities = capabilities
        self.executions = {}  # Store execution sessions
    
    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        sb: Client,
        firm_id: UUID,
        user_id: UUID,
    ) -> AgentExecution:
        """
        Process a query from the user
        
        Args:
            query: User's natural language query
            context: Additional context (client_id, assignment_id, etc.)
            sb: Supabase client
            firm_id: Firm ID (for isolation)
            user_id: User ID (for permissions)
        
        Returns:
            AgentExecution with logs and actions
        """
        pass
    
    def create_execution(
        self,
        query: str,
        firm_id: UUID,
        user_id: UUID,
    ) -> AgentExecution:
        """Create new execution session"""
        execution = AgentExecution(self.agent_name, firm_id, user_id, query)
        self.executions[execution.id] = execution
        execution.log(f"Agent '{self.agent_name}' started execution")
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)
    
    async def execute_action(
        self,
        action: AgentAction,
        sb: Client,
        firm_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Execute an approved action
        
        Args:
            action: Approved action to execute
            sb: Supabase client
            firm_id: Firm ID
            user_id: User ID
        
        Returns:
            Execution result
        """
        try:
            if action.status != "approved":
                raise ValueError(f"Action {action.id} is not approved")
            
            # Execute action based on type
            result = await self._execute_action_impl(action, sb, firm_id, user_id)
            
            action.status = "executed"
            action.executed_at = datetime.now().isoformat()
            action.execution_result = result
            
            return {
                "success": True,
                "action_id": action.id,
                "result": result,
            }
            
        except Exception as e:
            action.status = "failed"
            action.error = str(e)
            
            return {
                "success": False,
                "action_id": action.id,
                "error": str(e),
            }
    
    @abstractmethod
    async def _execute_action_impl(
        self,
        action: AgentAction,
        sb: Client,
        firm_id: UUID,
        user_id: UUID,
    ) -> Any:
        """Implement action execution logic (must be overridden by subclasses)"""
        pass
    
    def approve_action(self, action_id: str, approved_by: UUID) -> bool:
        """Approve an action"""
        for execution in self.executions.values():
            for action in execution.actions:
                if action.id == action_id:
                    action.status = "approved"
                    action.approved_at = datetime.now().isoformat()
                    action.approved_by = str(approved_by)
                    return True
        return False
    
    def reject_action(self, action_id: str, rejected_by: UUID, reason: str) -> bool:
        """Reject an action"""
        for execution in self.executions.values():
            for action in execution.actions:
                if action.id == action_id:
                    action.status = "rejected"
                    action.error = f"Rejected by user: {reason}"
                    return True
        return False
    
    def save_execution_log(self, execution: AgentExecution, sb: Client):
        """Save execution log to database"""
        try:
            log_data = {
                "id": execution.id,
                "agent_name": execution.agent_name,
                "firm_id": execution.firm_id,
                "user_id": execution.user_id,
                "query": execution.query,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "status": execution.status,
                "logs": json.dumps(execution.logs),
                "actions": json.dumps([
                    {
                        "id": a.id,
                        "action_type": a.action_type,
                        "description": a.description,
                        "status": a.status,
                        "requires_approval": a.requires_approval,
                        "risk_level": a.risk_level,
                    }
                    for a in execution.actions
                ]),
                "result": json.dumps(execution.result) if execution.result else None,
                "error": execution.error,
            }
            
            sb.table("ai_agent_executions").upsert(log_data).execute()
            
        except Exception as e:
            print(f"[AI Agent] Failed to save execution log: {str(e)}")
    
    def query_firm_data(
        self,
        sb: Client,
        table: str,
        firm_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """
        Query firm data with automatic firm isolation
        
        Args:
            sb: Supabase client
            table: Table name
            firm_id: Firm ID (automatically applied)
            filters: Additional filters
        
        Returns:
            List of records
        """
        query = sb.table(table).select("*").eq("firm_id", str(firm_id))
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data or []
    
    def send_approval_request(
        self,
        action: AgentAction,
        user_email: str,
        user_name: str,
    ):
        """Send approval request email"""
        try:
            email_service.send_email(
                to_email=user_email,
                subject=f"Action Approval Required: {action.action_type}",
                html_body=f"""
                <h2>Action Approval Required</h2>
                <p>Dear {user_name},</p>
                <p>The AI Copilot has proposed the following action:</p>
                <ul>
                    <li><strong>Action:</strong> {action.action_type}</li>
                    <li><strong>Description:</strong> {action.description}</li>
                    <li><strong>Risk Level:</strong> {action.risk_level}</li>
                </ul>
                <p>Please review and approve/reject this action in the dashboard.</p>
                <p><strong>Action ID:</strong> {action.id}</p>
                """
            )
        except Exception as e:
            print(f"[AI Agent] Failed to send approval email: {str(e)}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "capabilities": self.capabilities,
            "total_executions": len(self.executions),
        }
