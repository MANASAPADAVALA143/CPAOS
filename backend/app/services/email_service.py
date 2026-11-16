from __future__ import annotations

import html
import os
from typing import Any

import requests

from app.core.config import get_settings


def send_document_alert(
    to_email: str,
    client_name: str,
    document_type: str,
    confidence: float,
    client_id: str,
    firm_name: str,
) -> dict[str, Any]:
    key = get_settings().resend_api_key or os.getenv("RESEND_API_KEY")
    from_email = get_settings().from_email or os.getenv("FROM_EMAIL")
    if not key or not from_email:
        return {"sent": False, "reason": "Resend not configured"}
    try:
        import resend

        resend.api_key = key
    except ImportError:
        return {"sent": False, "reason": "resend package not installed"}

    dashboard_url = get_settings().frontend_url.rstrip("/")
    pct = int(round(float(confidence or 0) * 100))
    resend.Emails.send(
        {
            "from": from_email,
            "to": [to_email],
            "subject": f"New document uploaded — {client_name}",
            "html": f"""
          <h2>New document uploaded</h2>
          <p><strong>{client_name}</strong> uploaded <strong>{document_type or "a file"}</strong>
          (AI confidence: {pct}%).</p>
          <p><a href="{dashboard_url}/clients/{client_id}"
             style="background:#2563EB;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;">
            Review document
          </a></p>
          <p style="color:#64748b;font-size:12px;">{firm_name} · CPAOS</p>
        """,
        }
    )
    return {"sent": True}


def send_engagement_email(
    to_email: str,
    client_name: str,
    firm_name: str,
    signing_url: str,
    firm_whatsapp: str = "",
) -> None:
    """Send engagement letter signing email via Resend. Does not raise if Resend fails."""
    try:
        key = get_settings().resend_api_key or os.getenv("RESEND_API_KEY")
        from_addr = os.getenv("FROM_EMAIL", "onboarding@cpaos.app")
        if not key or not from_addr:
            return
        import resend

        resend.api_key = key
        cn = html.escape(client_name)
        fn = html.escape(firm_name)
        su = html.escape(signing_url, quote=True)
        wa = html.escape(firm_whatsapp) if firm_whatsapp else ""
        wa_block = (
            f'<p style="margin: 20px 0 0; font-size: 13px; color: #94a3b8;">Questions? WhatsApp us: {wa}</p>'
            if firm_whatsapp
            else ""
        )
        resend.Emails.send(
            {
                "from": f"{firm_name} <{from_addr}>",
                "to": [to_email],
                "subject": f"Action required: Please sign your engagement letter — {firm_name}",
                "html": f"""<!DOCTYPE html>
<html>
<body style="font-family: 'DM Sans', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 40px 0;">
  <div style="max-width: 520px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden;
              border: 1px solid #e2e8f0;">
    <div style="background: #1e293b; padding: 24px 32px;">
      <h1 style="color: white; font-size: 20px; margin: 0; font-weight: 700;">{fn}</h1>
      <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0;">Client Onboarding</p>
    </div>
    <div style="padding: 32px;">
      <p style="color: #1e293b; font-size: 16px; font-weight: 600; margin: 0 0 8px;">Hi {cn},</p>
      <p style="color: #475569; font-size: 14px; line-height: 1.7; margin: 0 0 24px;">
        Your engagement letter from <strong>{fn}</strong> is ready for your signature.
        Please click the button below to review and sign it electronically. This takes less than 2 minutes.
      </p>
      <div style="text-align: center; margin: 0 0 28px;">
        <a href="{su}"
           style="display: inline-block; background: #2563eb; color: white; font-size: 15px; font-weight: 600;
                  padding: 14px 32px; border-radius: 8px; text-decoration: none;">
          Sign Engagement Letter →
        </a>
      </div>
      <div style="background: #f1f5f9; border-radius: 8px; padding: 16px; font-size: 13px; color: #64748b; line-height: 1.6;">
        <strong style="color: #475569;">What happens next?</strong><br>
        Once signed, your onboarding portal will activate and you can start uploading your documents.
        Our team will be notified immediately.
      </div>
      {wa_block}
    </div>
    <div style="background: #f8fafc; padding: 16px 32px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
      Powered by CPAOS · This link expires in 30 days
    </div>
  </div>
</body>
</html>""",
            }
        )
    except Exception as e:
        print(f"Engagement email failed: {e}")


def send_onboarding_complete_staff_email(
    to_email: str,
    client_name: str,
    client_id: str,
    firm_name: str,
) -> dict[str, Any]:
    key = get_settings().resend_api_key or os.getenv("RESEND_API_KEY")
    from_email = get_settings().from_email or os.getenv("FROM_EMAIL")
    if not key or not from_email:
        return {"sent": False, "reason": "Resend not configured"}
    try:
        import resend
    except ImportError:
        return {"sent": False, "reason": "resend package not installed"}

    resend.api_key = key
    dashboard_url = get_settings().frontend_url.rstrip("/")
    resend.Emails.send(
        {
            "from": from_email,
            "to": [to_email],
            "subject": f"{client_name} onboarding is 100% complete",
            "html": f"""
          <p><strong>{client_name}</strong> finished all required checklist items.</p>
          <p><a href="{dashboard_url}/clients/{client_id}">Open client</a></p>
          <p style="color:#64748b;font-size:12px;">{firm_name}</p>
        """,
        }
    )
    return {"sent": True}


def send_slack_alert(webhook_url: str | None, text: str) -> dict[str, Any]:
    if not webhook_url:
        return {"sent": False, "reason": "No webhook"}
    try:
        r = requests.post(webhook_url, json={"text": text}, timeout=10)
        r.raise_for_status()
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "reason": str(e)}
