from __future__ import annotations

import uuid


def portal_link(frontend_url: str, firm_slug: str, onboarding_token: str | uuid.UUID) -> str:
    return f"{frontend_url.rstrip('/')}/portal/{firm_slug}/{onboarding_token}"
