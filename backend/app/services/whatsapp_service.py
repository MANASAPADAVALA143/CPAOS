import os

import requests

from app.core.config import get_settings

WHATSAPP_TEMPLATES = {
    "welcome": (
        "Hi {client_name} 👋\n\nWelcome to {firm_name}!\n\nYour document portal is ready:\n{portal_link}\n\n"
        "Documents needed: {doc_count}\nDeadline: {deadline}\n\nQuestions? Reply here."
    ),
    "reminder_day2": (
        "Hi {client_name} 👋\n\nQuick reminder from {firm_name}.\n\nYour onboarding is {completion_pct}% complete.\n\n"
        "Still pending:\n{pending_items}\n\nUpload here: {portal_link}\n\nTakes just 10 minutes! 🙏"
    ),
    "reminder_day5": (
        "Hi {client_name},\n\nWe still need a few documents:\n\n{pending_items}\n\nPortal: {portal_link}\n\n"
        "Please upload by {deadline}.\n\n{firm_name}"
    ),
    "completion": (
        "Hi {client_name} 🎉\n\nYour onboarding is complete!\n\nOur team will review your documents and reach out within 24 hours.\n\n"
        "Thank you for choosing {firm_name}!"
    ),
    "engagement_sign_reminder": (
        "Hi {client_name},\n\nPlease sign your engagement letter from {firm_name}.\n\n"
        "Check your email for DocuSign or open your portal:\n{portal_link}"
    ),
    "engagement_letter": (
        "Hi {client_name} 👋\n\n"
        "{firm_name} has sent you an engagement letter to sign.\n\n"
        "✍️ Sign here (takes 2 minutes):\n"
        "{signing_url}\n\n"
        "Once signed, you'll receive your document upload portal link.\n\n"
        "Questions? Reply to this message."
    ),
}


def send_whatsapp(phone: str, template: str, variables: dict) -> dict:
    url = get_settings().n8n_webhook_url or os.getenv("N8N_WEBHOOK_URL", "")
    if not url:
        return {"status": "no_webhook_configured", "channel": "whatsapp"}
    message = WHATSAPP_TEMPLATES.get(template, "").format(**variables).strip()
    try:
        resp = requests.post(
            url,
            json={"phone": phone, "message": message, "template": template},
            timeout=10,
        )
        return {"status": "sent" if resp.status_code == 200 else "failed", "channel": "whatsapp"}
    except Exception as e:
        return {"status": "error", "error": str(e), "channel": "whatsapp"}
