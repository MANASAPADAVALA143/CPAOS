import os

from app.core.config import get_settings

SMS_TEMPLATES = {
    "welcome": "Hi {client_name}, {firm_name} has sent your doc portal: {portal_link} — {doc_count} documents needed.",
    "reminder_day2": "Reminder from {firm_name}: onboarding {completion_pct}% done. Upload here: {portal_link}",
    "reminder_day5": "Hi {client_name}, {firm_name} needs your documents by {deadline}: {portal_link}",
    "completion": (
        "Hi {client_name}, your onboarding with {firm_name} is complete! "
        "Our team will review everything and reach out within 24 hours. Thank you!"
    ),
    "portal_link_via_voice": (
        "Hi {client_name}, here's your document upload portal: {portal_link}. "
        "Upload outstanding documents and your accountant will be notified. — {firm_name}"
    ),
    "engagement_sign_reminder": (
        "Hi {client_name}, please sign your engagement letter from {firm_name}. "
        "Check your email for DocuSign or open your portal: {portal_link}"
    ),
    "engagement_letter": (
        "Hi {client_name}, {firm_name} sent your engagement letter. "
        "Sign here: {signing_url} - takes 2 mins."
    ),
}


def send_sms(phone: str, template: str, variables: dict) -> dict:
    s = get_settings()
    sid = s.twilio_account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = s.twilio_auth_token or os.getenv("TWILIO_AUTH_TOKEN")
    from_num = s.twilio_from_number or os.getenv("TWILIO_FROM_NUMBER")
    if not sid or not token or not from_num:
        return {"status": "error", "error": "Twilio not configured", "channel": "sms"}
    from twilio.rest import Client as TwilioClient

    twilio = TwilioClient(sid, token)
    body = SMS_TEMPLATES.get(template, "").format(**variables)
    try:
        msg = twilio.messages.create(body=body, from_=from_num, to=phone)
        return {"status": "sent", "sid": msg.sid, "channel": "sms"}
    except Exception as e:
        return {"status": "error", "error": str(e), "channel": "sms"}
