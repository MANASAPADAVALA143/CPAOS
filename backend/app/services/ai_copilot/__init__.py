"""
GNANOVA CA PRACTICE OS - AI Copilot Module
Phase 5: AI agents for practice management
"""

from app.services.ai_copilot.client_onboarding_agent import client_onboarding_agent
from app.services.ai_copilot.document_intelligence_agent import document_intelligence_agent
from app.services.ai_copilot.compliance_monitoring_agent import compliance_monitoring_agent
from app.services.ai_copilot.collections_agent import collections_agent

__all__ = [
    "client_onboarding_agent",
    "document_intelligence_agent",
    "compliance_monitoring_agent",
    "collections_agent",
]
