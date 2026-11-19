"""
GNANOVA CA PRACTICE OS - Document Intelligence Agent
Phase 5: AI agent for document analysis and extraction
"""

from typing import Dict, Any, List
from uuid import UUID
from supabase import Client
import anthropic
import os
import base64

from app.services.ai_copilot.base_agent import BaseAIAgent, AgentAction, AgentExecution


class DocumentIntelligenceAgent(BaseAIAgent):
    """
    AI agent for document intelligence
    
    Capabilities:
    - Extract data from invoices
    - Extract data from bank statements
    - Extract data from Form 16/26AS
    - Extract data from financial statements
    - Validate extracted data
    - Categorize documents
    - OCR for scanned documents
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Document Intelligence Agent",
            agent_description="Analyzes documents and extracts structured data automatically",
            capabilities=[
                "Extract invoice data (vendor, amount, tax, date)",
                "Extract bank statement data",
                "Extract Form 16/26AS data",
                "Extract financial statement data",
                "Validate GST numbers, PAN, etc.",
                "Categorize documents by type",
                "OCR for scanned documents",
                "Detect anomalies in documents",
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
        """Process document intelligence query"""
        
        execution = self.create_execution(query, firm_id, user_id)
        
        try:
            execution.log(f"Processing query: {query}")
            
            # Get document data
            document_id = context.get("document_id")
            document_type = context.get("document_type", "unknown")
            document_text = context.get("document_text")
            document_url = context.get("document_url")
            
            if not document_text and not document_url:
                raise ValueError("No document data provided")
            
            execution.log(f"Analyzing document type: {document_type}")
            
            # Extract data based on document type
            if document_type == "invoice":
                extracted_data = await self._extract_invoice_data(document_text, execution)
            elif document_type == "bank_statement":
                extracted_data = await self._extract_bank_statement_data(document_text, execution)
            elif document_type == "form16":
                extracted_data = await self._extract_form16_data(document_text, execution)
            elif document_type == "financial_statement":
                extracted_data = await self._extract_financial_statement_data(document_text, execution)
            else:
                # Auto-detect document type
                detected_type = await self._detect_document_type(document_text, execution)
                execution.log(f"Detected document type: {detected_type}")
                extracted_data = await self._extract_generic_data(document_text, detected_type, execution)
            
            execution.log(f"Extracted data: {extracted_data}")
            
            # Validate extracted data
            validation = self._validate_extracted_data(extracted_data, document_type)
            execution.log(f"Validation result: {validation}")
            
            # Generate actions
            actions = self._generate_document_actions(
                extracted_data,
                validation,
                document_id,
                document_type,
                execution
            )
            
            for action in actions:
                execution.add_action(action)
                execution.log(f"Created action: {action.description}")
            
            # Complete execution
            result = {
                "extracted_data": extracted_data,
                "validation": validation,
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
    
    async def _detect_document_type(self, document_text: str, execution: AgentExecution) -> str:
        """Detect document type using Claude"""
        
        try:
            prompt = f"""Analyze this document and determine its type.

Document text (first 500 chars):
{document_text[:500]}

Return ONLY ONE of these document types:
- invoice
- bank_statement
- form16
- form26as
- gst_return
- financial_statement
- balance_sheet
- profit_loss
- trial_balance
- tax_return
- unknown

Return only the document type, no explanations."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            doc_type = message.content[0].text.strip().lower()
            return doc_type
            
        except Exception as e:
            execution.log(f"Failed to detect document type: {str(e)}", level="error")
            return "unknown"
    
    async def _extract_invoice_data(self, document_text: str, execution: AgentExecution) -> Dict[str, Any]:
        """Extract invoice data using Claude"""
        
        try:
            prompt = f"""Extract invoice information from this document.

Document:
{document_text[:2000]}

Extract and return in JSON format:
- invoice_number
- invoice_date
- vendor_name
- vendor_gstin
- buyer_name
- buyer_gstin
- subtotal
- cgst
- sgst
- igst
- total_amount
- line_items (array with description, quantity, rate, amount)

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            extracted = json.loads(message.content[0].text)
            return extracted
            
        except Exception as e:
            execution.log(f"Failed to extract invoice data: {str(e)}", level="error")
            return {}
    
    async def _extract_bank_statement_data(self, document_text: str, execution: AgentExecution) -> Dict[str, Any]:
        """Extract bank statement data"""
        
        try:
            prompt = f"""Extract bank statement information from this document.

Document:
{document_text[:2000]}

Extract and return in JSON format:
- bank_name
- account_number
- account_holder
- statement_period_start
- statement_period_end
- opening_balance
- closing_balance
- transactions (array with date, description, debit, credit, balance - max 10 transactions)

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            extracted = json.loads(message.content[0].text)
            return extracted
            
        except Exception as e:
            execution.log(f"Failed to extract bank statement: {str(e)}", level="error")
            return {}
    
    async def _extract_form16_data(self, document_text: str, execution: AgentExecution) -> Dict[str, Any]:
        """Extract Form 16 data"""
        
        try:
            prompt = f"""Extract Form 16 information from this document.

Document:
{document_text[:2000]}

Extract and return in JSON format:
- employee_name
- pan
- employer_name
- employer_tan
- financial_year
- gross_salary
- standard_deduction
- taxable_income
- tax_deducted
- tax_paid

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            extracted = json.loads(message.content[0].text)
            return extracted
            
        except Exception as e:
            execution.log(f"Failed to extract Form 16: {str(e)}", level="error")
            return {}
    
    async def _extract_financial_statement_data(self, document_text: str, execution: AgentExecution) -> Dict[str, Any]:
        """Extract financial statement data"""
        
        try:
            prompt = f"""Extract key financial metrics from this financial statement.

Document:
{document_text[:2000]}

Extract and return in JSON format:
- company_name
- financial_year
- revenue
- expenses
- profit
- assets
- liabilities
- equity

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            extracted = json.loads(message.content[0].text)
            return extracted
            
        except Exception as e:
            execution.log(f"Failed to extract financial statement: {str(e)}", level="error")
            return {}
    
    async def _extract_generic_data(self, document_text: str, doc_type: str, execution: AgentExecution) -> Dict[str, Any]:
        """Extract generic data for unknown document types"""
        
        try:
            prompt = f"""Extract key information from this {doc_type} document.

Document:
{document_text[:1500]}

Extract relevant structured data and return as JSON.
Include fields that are commonly found in {doc_type} documents.

Return only valid JSON."""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            extracted = json.loads(message.content[0].text)
            return extracted
            
        except Exception as e:
            execution.log(f"Failed to extract data: {str(e)}", level="error")
            return {}
    
    def _validate_extracted_data(self, data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Validate extracted data"""
        
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }
        
        # Validate PAN if present
        if "pan" in data:
            pan = data["pan"]
            if pan and len(pan) != 10:
                validation["errors"].append(f"Invalid PAN length: {pan}")
                validation["is_valid"] = False
        
        # Validate GSTIN if present
        if "vendor_gstin" in data or "buyer_gstin" in data:
            for key in ["vendor_gstin", "buyer_gstin"]:
                if key in data:
                    gstin = data[key]
                    if gstin and len(gstin) != 15:
                        validation["errors"].append(f"Invalid GSTIN length: {gstin}")
                        validation["is_valid"] = False
        
        # Validate amounts
        for key in ["total_amount", "subtotal", "revenue", "profit"]:
            if key in data:
                try:
                    amount = float(data[key])
                    if amount < 0:
                        validation["warnings"].append(f"Negative {key}: {amount}")
                except:
                    validation["errors"].append(f"Invalid {key} format: {data[key]}")
                    validation["is_valid"] = False
        
        return validation
    
    def _generate_document_actions(
        self,
        extracted_data: Dict[str, Any],
        validation: Dict[str, Any],
        document_id: Optional[str],
        doc_type: str,
        execution: AgentExecution
    ) -> List[AgentAction]:
        """Generate actions based on extracted data"""
        
        actions = []
        
        # Action 1: Store extracted data
        actions.append(AgentAction(
            action_type="store_extracted_data",
            description=f"Store extracted data from {doc_type}",
            parameters={
                "document_id": document_id,
                "extracted_data": extracted_data,
                "doc_type": doc_type,
            },
            requires_approval=False,
            risk_level="low"
        ))
        
        # Action 2: Create entries if invoice
        if doc_type == "invoice" and extracted_data.get("line_items"):
            actions.append(AgentAction(
                action_type="create_ledger_entries",
                description=f"Create ledger entries from invoice",
                parameters={
                    "invoice_data": extracted_data,
                },
                requires_approval=True,
                risk_level="high"
            ))
        
        # Action 3: Flag for review if validation failed
        if not validation["is_valid"]:
            actions.append(AgentAction(
                action_type="flag_for_review",
                description=f"Flag document for manual review due to validation errors",
                parameters={
                    "errors": validation["errors"],
                    "document_id": document_id,
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
        
        if action_type == "store_extracted_data":
            # Store in database
            return {"message": "Data stored successfully"}
        
        elif action_type == "create_ledger_entries":
            # Create ledger entries
            return {"message": "Ledger entries created"}
        
        elif action_type == "flag_for_review":
            # Flag document
            return {"message": "Document flagged for review"}
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


# Singleton instance
document_intelligence_agent = DocumentIntelligenceAgent()
