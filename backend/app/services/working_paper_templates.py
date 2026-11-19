"""
GNANOVA CA PRACTICE OS - Working Paper Templates
Pre-defined templates for different audit types and sections
"""

from typing import List, Dict, Any


class WorkingPaperTemplates:
    """Library of working paper templates for audit engagements"""
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all working paper templates"""
        
        # Statutory Audit Templates
        self.templates['statutory_audit'] = {
            "planning": [
                {
                    "reference": "A1",
                    "title": "Audit Planning Memorandum",
                    "section": "planning",
                    "description": "Overall audit strategy and approach",
                    "procedure": "Document understanding of entity, assessment of risks, materiality determination, and audit approach",
                    "checklist": [
                        "Entity background and industry analysis",
                        "Key accounting policies",
                        "Materiality calculations",
                        "Audit scope and objectives",
                        "Resource allocation",
                    ]
                },
                {
                    "reference": "A2",
                    "title": "Materiality Calculation",
                    "section": "planning",
                    "description": "Determination of overall and performance materiality",
                    "procedure": "Calculate materiality based on appropriate benchmarks (revenue, assets, profit)",
                    "checklist": [
                        "Benchmark selection rationale",
                        "Overall materiality calculation",
                        "Performance materiality",
                        "Clearly trivial threshold",
                    ]
                },
                {
                    "reference": "A3",
                    "title": "Risk Assessment",
                    "section": "planning",
                    "description": "Assessment of risks of material misstatement",
                    "procedure": "Identify and assess risks at financial statement and assertion level",
                    "checklist": [
                        "Entity-level risks",
                        "Account-level risks",
                        "Fraud risk assessment",
                        "Significant risks",
                        "Response to assessed risks",
                    ]
                },
            ],
            "assets": [
                {
                    "reference": "B1",
                    "title": "Cash and Bank Balances",
                    "section": "assets",
                    "description": "Verification of cash and bank balances",
                    "procedure": "Obtain bank confirmations, review bank reconciliations, test cash counts",
                    "checklist": [
                        "Bank confirmation letters obtained",
                        "Bank reconciliations reviewed",
                        "Unreconciled items investigated",
                        "Cash count performed",
                        "Restrictions on cash disclosed",
                    ]
                },
                {
                    "reference": "B2",
                    "title": "Trade Receivables",
                    "section": "assets",
                    "description": "Verification of trade receivables and provision for doubtful debts",
                    "procedure": "Circularize debtors, age analysis, provision adequacy assessment",
                    "checklist": [
                        "Debtors circularization performed",
                        "Ageing analysis reviewed",
                        "Provision for doubtful debts assessed",
                        "Related party transactions identified",
                        "Subsequent collections reviewed",
                    ]
                },
                {
                    "reference": "B3",
                    "title": "Inventory",
                    "section": "assets",
                    "description": "Verification of inventory existence, valuation, and completeness",
                    "procedure": "Attend physical count, test NRV, review obsolescence",
                    "checklist": [
                        "Physical inventory count attended",
                        "Inventory valuation method reviewed",
                        "NRV testing performed",
                        "Obsolete inventory identified",
                        "Inventory cutoff tested",
                    ]
                },
                {
                    "reference": "B4",
                    "title": "Fixed Assets",
                    "section": "assets",
                    "description": "Verification of fixed assets and depreciation",
                    "procedure": "Verify additions, disposals, depreciation calculations, impairment",
                    "checklist": [
                        "Fixed asset register reviewed",
                        "Additions verified",
                        "Disposals verified",
                        "Depreciation calculations tested",
                        "Impairment assessment reviewed",
                    ]
                },
            ],
            "liabilities": [
                {
                    "reference": "C1",
                    "title": "Trade Payables",
                    "section": "liabilities",
                    "description": "Verification of trade payables",
                    "procedure": "Circularize creditors, review ageing, test completeness",
                    "checklist": [
                        "Creditors circularization performed",
                        "Ageing analysis reviewed",
                        "Reconciliations obtained",
                        "Unrecorded liabilities tested",
                        "Subsequent payments reviewed",
                    ]
                },
                {
                    "reference": "C2",
                    "title": "Borrowings",
                    "section": "liabilities",
                    "description": "Verification of loans and borrowings",
                    "procedure": "Obtain confirmations, verify terms, test compliance with covenants",
                    "checklist": [
                        "Loan confirmations obtained",
                        "Loan agreements reviewed",
                        "Interest calculations tested",
                        "Covenant compliance verified",
                        "Security disclosures reviewed",
                    ]
                },
                {
                    "reference": "C3",
                    "title": "Provisions and Contingencies",
                    "section": "liabilities",
                    "description": "Assessment of provisions and contingent liabilities",
                    "procedure": "Review management assessment, obtain legal confirmations",
                    "checklist": [
                        "Provision calculations reviewed",
                        "Legal confirmations obtained",
                        "Management representation obtained",
                        "Disclosure adequacy assessed",
                    ]
                },
            ],
            "income": [
                {
                    "reference": "D1",
                    "title": "Revenue Recognition",
                    "section": "income",
                    "description": "Verification of revenue recognition",
                    "procedure": "Test revenue transactions, assess revenue recognition policy compliance",
                    "checklist": [
                        "Revenue recognition policy reviewed",
                        "Sample transactions tested",
                        "Cutoff testing performed",
                        "Related party revenue identified",
                        "Revenue analytics reviewed",
                    ]
                },
            ],
            "expenses": [
                {
                    "reference": "E1",
                    "title": "Payroll and Staff Costs",
                    "section": "expenses",
                    "description": "Verification of payroll expenses",
                    "procedure": "Test payroll calculations, verify statutory compliance",
                    "checklist": [
                        "Payroll register reviewed",
                        "Sample employee costs tested",
                        "PF/ESI compliance verified",
                        "TDS compliance verified",
                        "Related party compensation identified",
                    ]
                },
                {
                    "reference": "E2",
                    "title": "Operating Expenses",
                    "section": "expenses",
                    "description": "Verification of operating expenses",
                    "procedure": "Test significant expenses, analytical procedures",
                    "checklist": [
                        "Analytical review performed",
                        "Sample transactions tested",
                        "Related party expenses identified",
                        "Capitalization policy reviewed",
                        "Expense cutoff tested",
                    ]
                },
            ],
            "closing": [
                {
                    "reference": "F1",
                    "title": "Subsequent Events Review",
                    "section": "closing",
                    "description": "Review of events after reporting date",
                    "procedure": "Review board minutes, management representations, subsequent transactions",
                    "checklist": [
                        "Board minutes reviewed",
                        "Management inquiries made",
                        "Subsequent transactions reviewed",
                        "Adjusting events identified",
                        "Non-adjusting events disclosed",
                    ]
                },
                {
                    "reference": "F2",
                    "title": "Going Concern Assessment",
                    "section": "closing",
                    "description": "Assessment of going concern assumption",
                    "procedure": "Review cash flow forecasts, assess liquidity, identify risks",
                    "checklist": [
                        "Cash flow forecasts reviewed",
                        "Liquidity position assessed",
                        "Debt covenant compliance",
                        "Management plans reviewed",
                        "Disclosure adequacy assessed",
                    ]
                },
            ],
        }
        
        # Tax Audit Templates
        self.templates['tax_audit'] = {
            "planning": [
                {
                    "reference": "T1",
                    "title": "Tax Audit Planning",
                    "section": "planning",
                    "description": "Tax audit planning and scope",
                    "procedure": "Understand tax positions, identify tax risks, plan procedures",
                    "checklist": [
                        "Tax returns reviewed",
                        "Tax positions identified",
                        "Transfer pricing assessment",
                        "Permanent establishment risks",
                    ]
                }
            ],
            "income": [
                {
                    "reference": "T2",
                    "title": "Income Verification - Income Tax",
                    "section": "income",
                    "description": "Verification of taxable income",
                    "procedure": "Reconcile book profits to taxable income",
                    "checklist": [
                        "Book profit to taxable income reconciliation",
                        "Disallowances identified",
                        "Exempt income verified",
                        "Capital gains reviewed",
                    ]
                }
            ],
            "deductions": [
                {
                    "reference": "T3",
                    "title": "Deductions under Chapter VIA",
                    "section": "deductions",
                    "description": "Verification of deductions claimed",
                    "procedure": "Verify deductions under various sections",
                    "checklist": [
                        "Section 80C deductions verified",
                        "Section 80D deductions verified",
                        "Other deductions reviewed",
                        "Eligibility criteria checked",
                    ]
                }
            ],
        }
        
        # Internal Audit Templates
        self.templates['internal_audit'] = {
            "planning": [
                {
                    "reference": "I1",
                    "title": "Internal Audit Plan",
                    "section": "planning",
                    "description": "Internal audit planning and risk assessment",
                    "procedure": "Identify key controls, assess control risks",
                    "checklist": [
                        "Control environment assessed",
                        "Key controls identified",
                        "Testing approach determined",
                    ]
                }
            ],
            "controls": [
                {
                    "reference": "I2",
                    "title": "Control Testing - Revenue Cycle",
                    "section": "controls",
                    "description": "Testing of revenue cycle controls",
                    "procedure": "Test control design and operating effectiveness",
                    "checklist": [
                        "Sales order controls tested",
                        "Credit approval controls tested",
                        "Revenue recognition controls tested",
                        "Collections controls tested",
                    ]
                }
            ],
        }
    
    def get_template_by_engagement_type(self, engagement_type: str) -> Dict[str, List[Dict]]:
        """Get all templates for an engagement type"""
        return self.templates.get(engagement_type, {})
    
    def get_template_by_section(self, engagement_type: str, section: str) -> List[Dict]:
        """Get templates for a specific section"""
        templates = self.templates.get(engagement_type, {})
        return templates.get(section, [])
    
    def generate_working_papers_for_engagement(
        self,
        engagement_type: str,
        selected_sections: List[str] = None
    ) -> List[Dict]:
        """Generate working papers for an engagement"""
        
        templates = self.templates.get(engagement_type, {})
        working_papers = []
        
        if selected_sections:
            # Generate only selected sections
            for section in selected_sections:
                section_templates = templates.get(section, [])
                working_papers.extend(section_templates)
        else:
            # Generate all sections
            for section, section_templates in templates.items():
                working_papers.extend(section_templates)
        
        return working_papers
    
    def get_all_engagement_types(self) -> List[str]:
        """Get list of all available engagement types"""
        return list(self.templates.keys())
    
    def get_sections_for_engagement(self, engagement_type: str) -> List[str]:
        """Get list of sections for an engagement type"""
        templates = self.templates.get(engagement_type, {})
        return list(templates.keys())


# Singleton instance
wp_templates = WorkingPaperTemplates()
