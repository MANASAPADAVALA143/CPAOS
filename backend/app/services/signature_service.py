"""DocuSign engagement letters — PDF generation + envelope send when configured."""

from __future__ import annotations

import base64
import time
import uuid
from datetime import datetime
from typing import Any

import requests
from jose import jwt
from supabase import Client

from app.core.config import get_settings
from app.db import repo
from app.models.enums import ClientStatus


def generate_engagement_letter_pdf(client: dict[str, Any], firm: dict[str, Any]) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LETTER OF ENGAGEMENT", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"Date: {datetime.utcnow().strftime('%d %B %Y')}", ln=True)
    pdf.cell(0, 8, f"To: {client['client_name']}", ln=True)
    bn = client.get("business_name") or client["client_name"]
    pdf.cell(0, 8, f"Re: {bn}", ln=True)
    pdf.ln(8)

    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        0,
        8,
        f"Dear {client['client_name']},\n\n"
        f"We are pleased to confirm our engagement with {bn} "
        f"for the following professional services:\n",
    )

    services = client.get("services") or []
    if not services:
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 8, "  • As agreed", ln=True)
    else:
        for service in services:
            title = str(service).title() if isinstance(service, str) else str(service)
            pdf.cell(0, 8, f"  • {title}", ln=True)

    pdf.ln(6)
    pdf.multi_cell(
        0,
        8,
        "Our services will commence upon receipt of all required documents "
        "via your secure client portal. Fees will be as per our proposal.\n\n"
        "Please sign below to confirm your acceptance of this engagement.\n\n"
        "/sn1/\n\n"
        f"Yours sincerely,\n{firm['name']}",
    )

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)


def get_docusign_access_token() -> str:
    s = get_settings()
    ik = s.docusign_integration_key or ""
    uid = s.docusign_user_id or ""
    pk = (s.docusign_private_key or "").replace("\\n", "\n")
    if not ik or not uid or not pk:
        raise RuntimeError("DocuSign JWT credentials not configured")
    aud = "account-d.docusign.com" if (s.docusign_env or "demo") != "production" else "account.docusign.com"
    now = int(time.time())
    claims = {
        "iss": ik,
        "sub": uid,
        "aud": aud,
        "iat": now,
        "exp": now + 600,
        "scope": "signature impersonation",
    }
    assertion = jwt.encode(claims, pk, algorithm="RS256")
    url = f"https://{aud}/oauth/token"
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }
    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return str(resp.json()["access_token"])


def get_signing_url(client: dict[str, Any], firm: dict[str, Any], envelope_id: str) -> str | None:
    """Embedded/captive signing URL for the client (requires client_user_id on Signer)."""
    if not envelope_id:
        return None
    s = get_settings()
    if not all([s.docusign_account_id, s.docusign_integration_key, s.docusign_private_key, s.docusign_user_id]):
        return None
    try:
        from docusign_esign import ApiClient, EnvelopeViewsApi, RecipientViewRequest
    except ImportError:
        return None
    try:
        token = get_docusign_access_token()
        host = "https://demo.docusign.net/restapi" if (s.docusign_env or "demo") != "production" else "https://na1.docusign.net/restapi"
        api_client = ApiClient()
        api_client.host = host
        api_client.set_default_header("Authorization", f"Bearer {token}")
        base = get_settings().frontend_url.rstrip("/")
        return_url = f"{base}/portal/{firm['slug']}/{client['onboarding_token']}?engagement=return"
        view = RecipientViewRequest(
            authentication_method="none",
            client_user_id=str(client["id"]),
            recipient_id="1",
            return_url=return_url,
            user_name=client["client_name"],
            email=client["email"],
        )
        views = EnvelopeViewsApi(api_client)
        result = views.create_recipient_view(s.docusign_account_id, envelope_id, recipient_view_request=view)
        return getattr(result, "url", None)
    except Exception:
        return None


def send_engagement_letter(client: dict[str, Any], firm: dict[str, Any], sb: Client) -> dict:
    s = get_settings()
    cid = uuid.UUID(str(client["id"]))
    fid = uuid.UUID(str(client["firm_id"]))

    if not all([s.docusign_integration_key, s.docusign_account_id, s.docusign_private_key, s.docusign_user_id]):
        repo.update_client(
            sb,
            cid,
            {"engagement_letter_sent": True, "status": ClientStatus.signature_pending.value},
        )
        return {
            "envelope_id": None,
            "status": "skipped",
            "detail": "DocuSign not configured — client marked signature_pending",
        }

    try:
        from docusign_esign import ApiClient, Document, EnvelopeDefinition, EnvelopesApi, Recipients, SignHere, Signer, Tabs
    except ImportError as e:
        raise RuntimeError("docusign-esign package required") from e

    letter_pdf = generate_engagement_letter_pdf(client, firm)
    b64_pdf = base64.b64encode(letter_pdf).decode()

    token = get_docusign_access_token()
    host = "https://demo.docusign.net/restapi" if (s.docusign_env or "demo") != "production" else "https://na1.docusign.net/restapi"

    api_client = ApiClient()
    api_client.host = host
    api_client.set_default_header("Authorization", f"Bearer {token}")

    document = Document(
        document_base64=b64_pdf,
        name="Engagement Letter",
        file_extension="pdf",
        document_id="1",
    )

    sign_here = SignHere(
        anchor_string="/sn1/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20",
    )

    signer = Signer(
        email=client["email"],
        name=client["client_name"],
        recipient_id="1",
        routing_order="1",
        client_user_id=str(client["id"]),
        tabs=Tabs(sign_here_tabs=[sign_here]),
    )

    envelope_definition = EnvelopeDefinition(
        email_subject=f"Please sign: Engagement Letter — {firm['name']}",
        documents=[document],
        recipients=Recipients(signers=[signer]),
        status="sent",
    )

    account_id = s.docusign_account_id
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.create_envelope(account_id, envelope_definition=envelope_definition)

    repo.update_client(
        sb,
        cid,
        {
            "engagement_letter_sent": True,
            "signature_envelope_id": results.envelope_id,
            "status": ClientStatus.signature_pending.value,
        },
    )
    repo.insert_activity(
        sb,
        client_id=cid,
        firm_id=fid,
        action="engagement_letter_sent",
        description=f"DocuSign envelope {results.envelope_id} sent to {client['email']}",
        performed_by="system",
    )

    signing_url: str | None = None
    try:
        signing_url = get_signing_url(client, firm, results.envelope_id)
    except Exception:
        signing_url = None
    if not signing_url and results.envelope_id:
        signing_url = f"https://app.docusign.com/sign/{results.envelope_id}"

    portal = f"{get_settings().frontend_url.rstrip('/')}/portal/{firm['slug']}/{client['onboarding_token']}"
    effective_signing = signing_url or portal

    from app.services.email_service import send_engagement_email

    send_engagement_email(
        client["email"],
        client["client_name"],
        firm["name"],
        effective_signing,
        firm_whatsapp=firm.get("whatsapp_number") or "",
    )

    try:
        from app.services.messaging import send_message

        variables: dict[str, str] = {
            "client_name": client["client_name"],
            "firm_name": firm["name"],
            "signing_url": effective_signing,
        }
        send_message(client["phone"], "engagement_letter", variables)
    except Exception:
        pass

    return {"envelope_id": results.envelope_id, "status": "sent"}


def check_signature_status(envelope_id: str) -> str:
    if not envelope_id:
        return "voided"
    s = get_settings()
    if not s.docusign_account_id:
        return "sent"
    return "sent"


def handle_docusign_webhook(payload: dict, sb: Client) -> None:
    envelope_id = payload.get("envelopeId") or payload.get("envelope_id")
    status = (payload.get("status") or "").lower()
    if status == "completed" and envelope_id:
        client = repo.client_by_envelope(sb, envelope_id)
        if client:
            cid = uuid.UUID(str(client["id"]))
            repo.update_client(
                sb,
                cid,
                {
                    "engagement_letter_signed": True,
                    "status": ClientStatus.in_progress.value,
                },
            )


def render_engagement_letter_text(client: dict[str, Any], firm: dict[str, Any]) -> str:
    services = client.get("services") or []
    services_list = "\n".join(f"- {x}" for x in services) or "- As agreed"
    bn = client.get("business_name") or client["client_name"]
    return (
        f"LETTER OF ENGAGEMENT\n\nDate: {datetime.utcnow().strftime('%Y-%m-%d')}\n"
        f"To: {client['client_name']}\nRe: {bn}\n\n"
        f"Dear {client['client_name']},\n\nWe are pleased to confirm our engagement for the following professional services:\n"
        f"{services_list}\n\nYours sincerely,\n{firm['name']}"
    ).strip()
