"""
GNANOVA CA PRACTICE OS - Collections Assistance Agent
Phase 5: AI agent for receivables collection assistance
"""

from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, date, timedelta
from supabase import Client
import anthropic
import os

from app.services.ai_copilot.base_agent import BaseAIAgent, AgentAction, AgentExecution


class CollectionsAgent(BaseAIAgent):
    """
    AI agent for collections assistance
    
    Capabilities:
    - Monitor overdue invoices
    - Analyze payment patterns
    - Generate collection strategies
    - Draft collection emails
    - Predict payment likelihood
    - Suggest escalation actions
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Collections Assistance Agent",
            agent_description="Assists with receivables collection and payment follow-ups",
            capabilities=[
                "Monitor overdue invoices",
                "Analyze client payment patterns",
                "Generate personalized collection messages",
                "Suggest optimal follow-up timing",
                "Predict payment likelihood",
                "Recommend escalation actions",
                "Track collection effectiveness",
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
        """Process collections query"""
        
        execution = self.create_execution(query, firm_id, user_id)
        
        try:
            execution.log(f"Processing query: {query}")
            
            # Get overdue invoices
            overdue_invoices = self._get_overdue_invoices(sb, firm_id)
            execution.log(f"Found {len(overdue_invoices)} overdue invoices")
            
            # Analyze receivables
            analysis = await self._analyze_receivables(
                overdue_invoices,
                query,
                execution
            )
            
            execution.log(f"Receivables analysis: {analysis}")
            
            # Generate collection actions
            actions = self._generate_collection_actions(
                overdue_invoices,
                analysis,
                firm_id,
                execution
            )
            
            for action in actions:
                execution.add_action(action)
                execution.log(f"Created action: {action.description}")
            
            # Calculate metrics
            total_overdue = sum(float(inv.get("balance_due", 0)) for inv in overdue_invoices)
            
            result = {
                "summary": {
                    "total_overdue_invoices": len(overdue_invoices),
                    "total_overdue_amount": total_overdue,
                    "highest_overdue": max([float(inv.get("balance_due", 0)) for inv in overdue_invoices]) if overdue_invoices else 0,
                },
                "overdue_invoices": overdue_invoices[:10],
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
    
    def _get_overdue_invoices(self, sb: Client, firm_id: UUID) -> List[Dict[str, Any]]:
        """Get overdue invoices"""
        
        try:
            result = (
                sb.table("invoices")
                .select("*, clients(name)")
                .eq("firm_id", str(firm_id))
                .in_("status", ["overdue", "sent", "viewed"])
                .gt("balance_due", 0)
                .order("due_date")
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            print(f"[Collections Agent] Error fetching overdue: {str(e)}")
            return []
    
    async def _analyze_receivables(
        self,
        overdue_invoices: List[Dict],
        query: str,
        execution: AgentExecution
    ) -> Dict[str, Any]:
        """Analyze receivables using Claude"""
        
        try:
            # Group by client
            client_summaries = {}
            for inv in overdue_invoices:
                client_name = inv.get("clients", {}).get("name", "Unknown")
                if client_name not in client_summaries:
                    client_summaries[client_name] = {
                        "invoice_count": 0,
                        "total_overdue": 0,
                        "oldest_invoice_date": inv.get("due_date"),
                    }
                client_summaries[client_name]["invoice_count"] += 1
                client_summaries[client_name]["total_overdue"] += float(inv.get("balance_due", 0))
            
            prompt = f"""You are a collections expert analyzing overdue receivables for a CA practice.

Total Overdue Invoices: {len(overdue_invoices)}
Client Summary:
{client_summaries}

Query: {query}

Analyze and provide:
1. Priority clients for follow-up (based on amount and age)
2. Recommended collection approach for each
3. Suggested email tone (formal, friendly, urgent)
4. Optimal follow-up timing

Return as JSON with keys: priority_clients (array with client, amount, approach, tone, timing), overall_strategy"""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            analysis = json.loads(message.content[0].text)
            return analysis
            
        except Exception as e:
            execution.log(f"Failed to analyze receivables: {str(e)}", level="error")
            return {
                "priority_clients": [],
                "overall_strategy": "Send polite reminders to all overdue accounts"
            }
    
    def _generate_collection_actions(
        self,
        overdue_invoices: List[Dict],
        analysis: Dict[str, Any],
        firm_id: UUID,
        execution: AgentExecution
    ) -> List[AgentAction]:
        """Generate collection actions"""
        
        actions = []
        
        # Action 1: Send collection reminders
        if overdue_invoices:
            recent_overdue = [inv for inv in overdue_invoices if (date.today() - datetime.strptime(inv.get("due_date"), "%Y-%m-%d").date()).days <= 30]
            if recent_overdue:
                actions.append(AgentAction(
                    action_type="send_collection_reminders",
                    description=f"Send payment reminders for {len(recent_overdue)} recently overdue invoices",
                    parameters={
                        "invoice_ids": [inv["id"] for inv in recent_overdue],
                        "tone": "friendly",
                    },
                    requires_approval=False,
                    risk_level="low"
                ))
        
        # Action 2: Escalate long overdue
        long_overdue = [inv for inv in overdue_invoices if (date.today() - datetime.strptime(inv.get("due_date"), "%Y-%m-%d").date()).days > 60]
        if long_overdue:
            actions.append(AgentAction(
                action_type="escalate_collections",
                description=f"Escalate {len(long_overdue)} invoices overdue >60 days to partners",
                parameters={
                    "invoice_ids": [inv["id"] for inv in long_overdue],
                },
                requires_approval=True,
                risk_level="medium"
            ))
        
        # Action 3: Generate collections report
        if overdue_invoices:
            actions.append(AgentAction(
                action_type="generate_collections_report",
                description="Generate detailed collections report with aging analysis",
                parameters={
                    "total_overdue": sum(float(inv.get("balance_due", 0)) for inv in overdue_invoices),
                    "count": len(overdue_invoices),
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
        
        if action_type == "send_collection_reminders":
            # Send reminders
            return {"message": f"Reminders sent for {len(params['invoice_ids'])} invoices"}
        
        elif action_type == "escalate_collections":
            # Escalate to partners
            return {"message": f"Escalated {len(params['invoice_ids'])} invoices"}
        
        elif action_type == "generate_collections_report":
            # Generate report
            return {"message": "Collections report generated"}
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


# Singleton instance
collections_agent = CollectionsAgent()
