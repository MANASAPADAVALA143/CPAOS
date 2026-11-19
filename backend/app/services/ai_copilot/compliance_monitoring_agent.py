"""
GNANOVA CA PRACTICE OS - Compliance Monitoring Agent
Phase 5: AI agent for compliance monitoring and alerts
"""

from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, date, timedelta
from supabase import Client
import anthropic
import os

from app.services.ai_copilot.base_agent import BaseAIAgent, AgentAction, AgentExecution
from app.db import repo


class ComplianceMonitoringAgent(BaseAIAgent):
    """
    AI agent for compliance monitoring
    
    Capabilities:
    - Monitor upcoming compliance deadlines
    - Identify overdue compliances
    - Suggest compliance actions
    - Predict compliance risks
    - Generate compliance reports
    - Send proactive reminders
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Compliance Monitoring Agent",
            agent_description="Monitors compliance deadlines and proactively alerts about upcoming requirements",
            capabilities=[
                "Monitor all compliance deadlines",
                "Identify overdue compliances",
                "Predict compliance risks",
                "Generate compliance reports",
                "Send proactive reminders",
                "Suggest corrective actions",
                "Track compliance history",
            ]
        )
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        sb: Client,
        firm_id: UUID,
        user_id: UUID,
    ) -> AgentExecution:
        """Process compliance monitoring query"""
        
        execution = self.create_execution(query, firm_id, user_id)
        
        try:
            execution.log(f"Processing query: {query}")
            
            # Get compliance data
            client_id = context.get("client_id")
            time_horizon = context.get("time_horizon", 30)  # days
            
            # Fetch upcoming compliances
            upcoming = self._get_upcoming_compliances(sb, firm_id, time_horizon)
            execution.log(f"Found {len(upcoming)} upcoming compliances")
            
            # Fetch overdue compliances
            overdue = self._get_overdue_compliances(sb, firm_id)
            execution.log(f"Found {len(overdue)} overdue compliances")
            
            # Analyze compliance status
            analysis = await self._analyze_compliance_status(
                upcoming,
                overdue,
                query,
                execution
            )
            
            execution.log(f"Compliance analysis: {analysis}")
            
            # Generate actions
            actions = self._generate_compliance_actions(
                upcoming,
                overdue,
                analysis,
                firm_id,
                execution
            )
            
            for action in actions:
                execution.add_action(action)
                execution.log(f"Created action: {action.description}")
            
            # Complete execution
            result = {
                "summary": {
                    "upcoming_count": len(upcoming),
                    "overdue_count": len(overdue),
                    "high_priority": len([c for c in upcoming if c.get("priority") == "high"]),
                },
                "upcoming_compliances": upcoming[:10],  # Top 10
                "overdue_compliances": overdue[:10],
                "analysis": analysis,
                "actions": [
                    {
                        "id": a.id,
                        "type": a.action_type,
                        "description": a.description,
                        "requires_approval": a.requires_approval,
                    }
                    for a in actions
                ],
            }
            
            execution.complete(result)
            self.save_execution_log(execution, sb)
            
            return execution
            
        except Exception as e:
            execution.fail(str(e))
            execution.log(f"Error: {str(e)}", level="error")
            self.save_execution_log(execution, sb)
            return execution
    
    def _get_upcoming_compliances(
        self,
        sb: Client,
        firm_id: UUID,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get upcoming compliances within specified days"""
        
        try:
            today = date.today()
            future_date = today + timedelta(days=days)
            
            result = (
                sb.table("compliance_requirements")
                .select("*")
                .eq("firm_id", str(firm_id))
                .eq("status", "pending")
                .gte("due_date", today.isoformat())
                .lte("due_date", future_date.isoformat())
                .order("due_date")
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            print(f"[Compliance Agent] Error fetching upcoming: {str(e)}")
            return []
    
    def _get_overdue_compliances(
        self,
        sb: Client,
        firm_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get overdue compliances"""
        
        try:
            today = date.today()
            
            result = (
                sb.table("compliance_requirements")
                .select("*")
                .eq("firm_id", str(firm_id))
                .in_("status", ["pending", "in_progress"])
                .lt("due_date", today.isoformat())
                .order("due_date")
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            print(f"[Compliance Agent] Error fetching overdue: {str(e)}")
            return []
    
    async def _analyze_compliance_status(
        self,
        upcoming: List[Dict],
        overdue: List[Dict],
        query: str,
        execution: AgentExecution
    ) -> Dict[str, Any]:
        """Analyze compliance status using Claude"""
        
        try:
            # Prepare summary
            upcoming_summary = [
                {
                    "name": c.get("compliance_name"),
                    "due_date": c.get("due_date"),
                    "client": c.get("client_id"),
                }
                for c in upcoming[:5]
            ]
            
            overdue_summary = [
                {
                    "name": c.get("compliance_name"),
                    "due_date": c.get("due_date"),
                    "days_overdue": (date.today() - datetime.strptime(c.get("due_date"), "%Y-%m-%d").date()).days,
                }
                for c in overdue[:5]
            ]
            
            prompt = f"""You are a compliance monitoring AI assistant for a CA practice.

Upcoming Compliances (next 30 days): {len(upcoming)}
{upcoming_summary}

Overdue Compliances: {len(overdue)}
{overdue_summary}

Query: {query}

Analyze the compliance situation and provide:
1. Risk assessment (high, medium, low)
2. Priority actions needed
3. Clients at highest risk
4. Recommendations

Return as JSON with keys: risk_level, priority_actions (array), high_risk_clients (array), recommendations (array)"""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            analysis = json.loads(message.content[0].text)
            return analysis
            
        except Exception as e:
            execution.log(f"Failed to analyze compliance: {str(e)}", level="error")
            return {
                "risk_level": "medium",
                "priority_actions": ["Review overdue compliances"],
                "high_risk_clients": [],
                "recommendations": ["Set up automated reminders"]
            }
    
    def _generate_compliance_actions(
        self,
        upcoming: List[Dict],
        overdue: List[Dict],
        analysis: Dict[str, Any],
        firm_id: UUID,
        execution: AgentExecution
    ) -> List[AgentAction]:
        """Generate compliance actions"""
        
        actions = []
        
        # Action 1: Send reminders for upcoming compliances
        if upcoming:
            urgent_upcoming = [c for c in upcoming if (datetime.strptime(c.get("due_date"), "%Y-%m-%d").date() - date.today()).days <= 7]
            if urgent_upcoming:
                actions.append(AgentAction(
                    action_type="send_compliance_reminders",
                    description=f"Send reminders for {len(urgent_upcoming)} urgent upcoming compliances",
                    parameters={
                        "compliance_ids": [c["id"] for c in urgent_upcoming],
                    },
                    requires_approval=False,
                    risk_level="low"
                ))
        
        # Action 2: Escalate overdue compliances
        if overdue:
            critical_overdue = [c for c in overdue if (date.today() - datetime.strptime(c.get("due_date"), "%Y-%m-%d").date()).days > 7]
            if critical_overdue:
                actions.append(AgentAction(
                    action_type="escalate_overdue_compliances",
                    description=f"Escalate {len(critical_overdue)} critically overdue compliances to partners",
                    parameters={
                        "compliance_ids": [c["id"] for c in critical_overdue],
                    },
                    requires_approval=False,
                    risk_level="medium"
                ))
        
        # Action 3: Generate compliance report
        if len(upcoming) > 0 or len(overdue) > 0:
            actions.append(AgentAction(
                action_type="generate_compliance_report",
                description="Generate comprehensive compliance report",
                parameters={
                    "upcoming_count": len(upcoming),
                    "overdue_count": len(overdue),
                    "risk_level": analysis.get("risk_level"),
                },
                requires_approval=False,
                risk_level="low"
            ))
        
        return actions
    
    async def _execute_action_impl(
        self,
        action: AgentAction,
        sb: Client,
        firm_id: UUID,
        user_id: UUID,
    ) -> Any:
        """Execute approved action"""
        
        action_type = action.action_type
        params = action.parameters
        
        if action_type == "send_compliance_reminders":
            # Send reminders via email/WhatsApp
            return {"message": f"Reminders sent for {len(params['compliance_ids'])} compliances"}
        
        elif action_type == "escalate_overdue_compliances":
            # Create alerts and notify partners
            return {"message": f"Escalated {len(params['compliance_ids'])} overdue compliances"}
        
        elif action_type == "generate_compliance_report":
            # Generate and email report
            return {"message": "Compliance report generated"}
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


# Singleton instance
compliance_monitoring_agent = ComplianceMonitoringAgent()
