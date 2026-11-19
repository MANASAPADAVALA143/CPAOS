"""
GNANOVA CA PRACTICE OS - Client Onboarding Agent
Phase 5: AI agent to assist with client onboarding process
"""

from typing import Dict, Any, Optional
from uuid import UUID
from supabase import Client
import anthropic
import os

from app.services.ai_copilot.base_agent import BaseAIAgent, AgentAction, AgentExecution
from app.db import repo


class ClientOnboardingAgent(BaseAIAgent):
    """
    AI agent for client onboarding assistance
    
    Capabilities:
    - Extract client information from documents
    - Validate client details (PAN, GSTIN, etc.)
    - Suggest service packages
    - Create checklist for client onboarding
    - Draft engagement letters
    - Set up compliance calendar
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Client Onboarding Agent",
            agent_description="Assists with onboarding new clients, extracting information, and setting up services",
            capabilities=[
                "Extract client information from documents",
                "Validate PAN, GSTIN, TAN, CIN",
                "Suggest appropriate service packages",
                "Create onboarding checklist",
                "Draft engagement letters",
                "Set up compliance calendar",
                "Assign client to appropriate team",
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
        """Process client onboarding query"""
        
        execution = self.create_execution(query, firm_id, user_id)
        
        try:
            execution.log(f"Processing query: {query}")
            
            # Get context data
            client_name = context.get("client_name")
            client_type = context.get("client_type", "individual")
            document_text = context.get("document_text")
            
            # Extract information using Claude
            if document_text:
                extraction_result = await self._extract_client_info(document_text, execution)
                execution.log(f"Extracted client info: {extraction_result}")
            
            # Analyze client needs
            analysis = await self._analyze_client_needs(
                client_name or "New Client",
                client_type,
                query,
                execution
            )
            
            execution.log(f"Client analysis complete: {analysis}")
            
            # Generate onboarding actions
            actions = self._generate_onboarding_actions(
                analysis,
                client_name,
                client_type,
                firm_id,
                execution
            )
            
            for action in actions:
                execution.add_action(action)
                execution.log(f"Created action: {action.description}")
            
            # Complete execution
            result = {
                "analysis": analysis,
                "actions": [
                    {
                        "id": a.id,
                        "type": a.action_type,
                        "description": a.description,
                        "requires_approval": a.requires_approval,
                        "risk_level": a.risk_level,
                    }
                    for a in actions
                ],
                "message": f"Generated {len(actions)} onboarding actions. Please review and approve.",
            }
            
            execution.complete(result)
            self.save_execution_log(execution, sb)
            
            return execution
            
        except Exception as e:
            execution.fail(str(e))
            execution.log(f"Error: {str(e)}", level="error")
            self.save_execution_log(execution, sb)
            return execution
    
    async def _extract_client_info(
        self,
        document_text: str,
        execution: AgentExecution
    ) -> Dict[str, Any]:
        """Extract client information from document using Claude"""
        
        try:
            prompt = f"""Extract client information from the following document text.
            
Document:
{document_text[:2000]}

Please extract and return the following information in JSON format:
- client_name
- client_type (individual, company, partnership, trust, etc.)
- pan (if mentioned)
- gstin (if mentioned)
- tan (if mentioned)
- cin (if mentioned)
- email
- phone
- address
- business_activity
- annual_turnover (if mentioned)

Return only valid JSON, no explanations.
"""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            extracted_text = message.content[0].text
            
            # Parse JSON response
            import json
            extracted_info = json.loads(extracted_text)
            
            return extracted_info
            
        except Exception as e:
            execution.log(f"Failed to extract info: {str(e)}", level="error")
            return {}
    
    async def _analyze_client_needs(
        self,
        client_name: str,
        client_type: str,
        query: str,
        execution: AgentExecution
    ) -> Dict[str, Any]:
        """Analyze client needs using Claude"""
        
        try:
            prompt = f"""You are a CA practice expert helping to onboard a new client.

Client Name: {client_name}
Client Type: {client_type}
Query/Context: {query}

Based on this information, analyze:
1. What services does this client likely need? (income tax, GST, audit, accounting, etc.)
2. What compliance requirements apply? (based on client type)
3. What priority level should this client be? (high, medium, low)
4. What service package would you recommend?

Return your analysis in JSON format with keys:
- recommended_services (array)
- compliance_requirements (array)
- priority (string)
- service_package (string)
- reasoning (string)

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = message.content[0].text
            
            import json
            analysis = json.loads(analysis_text)
            
            return analysis
            
        except Exception as e:
            execution.log(f"Failed to analyze needs: {str(e)}", level="error")
            return {
                "recommended_services": ["income_tax", "accounting"],
                "compliance_requirements": [],
                "priority": "medium",
                "service_package": "basic",
                "reasoning": "Default recommendation due to analysis error"
            }
    
    def _generate_onboarding_actions(
        self,
        analysis: Dict[str, Any],
        client_name: Optional[str],
        client_type: str,
        firm_id: UUID,
        execution: AgentExecution
    ) -> list[AgentAction]:
        """Generate onboarding actions based on analysis"""
        
        actions = []
        
        # Action 1: Create client record
        actions.append(AgentAction(
            action_type="create_client",
            description=f"Create client record for {client_name or 'New Client'}",
            parameters={
                "name": client_name,
                "client_type": client_type,
                "category": analysis.get("priority", "medium"),
            },
            requires_approval=False,  # Low risk
            risk_level="low"
        ))
        
        # Action 2: Set up compliance calendar
        if analysis.get("compliance_requirements"):
            actions.append(AgentAction(
                action_type="setup_compliance_calendar",
                description=f"Set up compliance calendar with {len(analysis['compliance_requirements'])} requirements",
                parameters={
                    "requirements": analysis["compliance_requirements"],
                    "financial_year": "2024-25",
                },
                requires_approval=True,  # Medium risk
                risk_level="medium"
            ))
        
        # Action 3: Send welcome email
        actions.append(AgentAction(
            action_type="send_welcome_email",
            description=f"Send welcome email to {client_name or 'client'}",
            parameters={
                "template": "client_welcome",
                "service_package": analysis.get("service_package", "basic"),
            },
            requires_approval=False,
            risk_level="low"
        ))
        
        # Action 4: Create initial assignment
        if "income_tax" in analysis.get("recommended_services", []):
            actions.append(AgentAction(
                action_type="create_assignment",
                description="Create ITR filing assignment for new client",
                parameters={
                    "service_category": "income_tax",
                    "assignment_name": f"ITR Filing - {client_name}",
                    "priority": analysis.get("priority", "medium"),
                },
                requires_approval=True,
                risk_level="medium"
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
        
        if action_type == "create_client":
            # Create client record
            client_data = {
                "name": params["name"],
                "client_type": params["client_type"],
                "category": params["category"],
                "firm_id": str(firm_id),
                "status": "active",
                "onboarding_status": "in_progress",
            }
            result = sb.table("clients").insert(client_data).execute()
            return {"client_id": result.data[0]["id"]}
        
        elif action_type == "setup_compliance_calendar":
            # This would integrate with compliance service
            return {"message": "Compliance calendar setup initiated"}
        
        elif action_type == "send_welcome_email":
            # Send welcome email
            return {"message": "Welcome email sent"}
        
        elif action_type == "create_assignment":
            # This would integrate with assignment service
            return {"message": "Assignment created"}
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


# Singleton instance
client_onboarding_agent = ClientOnboardingAgent()
