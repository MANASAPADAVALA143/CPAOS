from app.services.sms_service import send_sms
from app.services.whatsapp_service import send_whatsapp


def send_message(phone: str, template: str, variables: dict, prefer: str = "whatsapp") -> dict:
    if prefer == "whatsapp":
        result = send_whatsapp(phone, template, variables)
        if result["status"] in ("error", "failed", "no_webhook_configured"):
            result = send_sms(phone, template, variables)
            result["fallback"] = True
    else:
        result = send_sms(phone, template, variables)
    return result
