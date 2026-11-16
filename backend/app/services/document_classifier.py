from __future__ import annotations

import base64
import json
import re

from anthropic import Anthropic

from app.core.config import get_settings

COUNTRY_CONTEXT = {
    "India": "Indian documents: PAN, Aadhaar, GSTIN, CIN, DIN, TAN, Form 16, ITR",
    "UAE": "UAE documents: Trade License, TRN, Emirates ID, VAT return, CT registration",
    "UK": "UK documents: UTR, NI number, Companies House CRN, HMRC letters, CT600, SA302",
    "US": "US documents: EIN, SSN, IRS notices, W-2, 1099, 1040, K-1, Articles of Incorporation",
    "Singapore": "Singapore documents: ACRA BizFile, NRIC, CPF, IRAS filing, GST registration",
}


def _client() -> Anthropic | None:
    key = get_settings().anthropic_api_key
    if not key:
        return None
    return Anthropic(api_key=key)


def classify_by_filename(filename: str) -> str:
    name = filename.lower()
    if "pan" in name:
        return "PAN Card"
    if "gst" in name:
        return "GST Certificate"
    if "itr" in name:
        return "Income Tax Return"
    if "bank" in name:
        return "Bank Statement"
    if "form16" in name or "form 16" in name:
        return "Form 16"
    if "balance" in name or " bs" in name:
        return "Balance Sheet"
    if "p&l" in name or " pl" in name:
        return "P&L Statement"
    if "passport" in name:
        return "Passport"
    if "aadhaar" in name or "aadhar" in name:
        return "Aadhaar Card"
    if "trade" in name and "license" in name:
        return "Trade License"
    if "ct600" in name:
        return "CT600 Return"
    if "ein" in name:
        return "EIN Document"
    return "Document"


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group())
    return json.loads(text)


def classify_document(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    expected_type: str | None = None,
    country: str = "India",
) -> dict:
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        content_type = "document"
        media_type = "application/pdf"
    elif ext in ["jpg", "jpeg", "png", "webp"]:
        content_type = "image"
        media_type = f"image/{ext.replace('jpg', 'jpeg')}"
    else:
        return {
            "document_type": classify_by_filename(filename),
            "confidence": 0.70,
            "verified": True,
            "issues": [],
            "extracted_data": {},
        }

    claude = _client()
    if not claude:
        return {
            "document_type": expected_type or classify_by_filename(filename),
            "confidence": 0.6,
            "verified": False,
            "issues": ["ANTHROPIC_API_KEY not set"],
            "extracted_data": {},
        }

    b64 = base64.b64encode(file_bytes).decode()
    ctx = COUNTRY_CONTEXT.get(country, "")

    prompt = f"""Analyse this document and return JSON only. No other text.

Country context: {ctx}
Filename: {filename}
Expected document type: {expected_type or "Any"}

Return this exact JSON structure:
{{
  "document_type": "specific document type name",
  "confidence": 0.0,
  "verified": true,
  "issues": [],
  "extracted_data": {{
    "entity_name": "",
    "date": "",
    "period": "",
    "id_number": ""
  }}
}}

Check: correct type, complete, legible, appears genuine.
Return ONLY valid JSON."""

    if content_type == "document":
        msg_content = [
            {"type": "document", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": prompt},
        ]
    else:
        msg_content = [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": prompt},
        ]

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": msg_content}],
        )
        block = response.content[0]
        text = getattr(block, "text", None) or str(block)
        return _extract_json(text)
    except Exception as e:
        return {
            "document_type": expected_type or classify_by_filename(filename),
            "confidence": 0.5,
            "verified": False,
            "issues": [f"Classification error: {str(e)}"],
            "extracted_data": {},
        }
