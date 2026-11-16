"""Seed demo firm + 4 clients. Run after supabase_schema.sql is applied in Supabase SQL Editor."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

load_dotenv()

from supabase import create_client

from app.core.config import get_settings
from app.models.enums import ChecklistItemStatus, ClientStatus, Country, EntityType, FirmUserRole, Plan
from app.services import checklist_generator
from app.services.completion import recompute_client_completion


def _portal_link(frontend: str, slug: str, token: uuid.UUID) -> str:
    return f"{frontend.rstrip('/')}/portal/{slug}/{token}"


def _ensure_demo_supabase_user_id() -> str:
    existing = os.getenv("SEED_SUPABASE_USER_ID")
    if existing:
        print("Using SEED_SUPABASE_USER_ID for demo owner.")
        return existing.strip()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    email = os.getenv("SEED_DEMO_EMAIL", "demo@cpaos.local")
    password = os.getenv("SEED_DEMO_PASSWORD", "DemoPass123!")
    if url and key:
        try:
            sb = create_client(url, key)
            created = sb.auth.admin.create_user(
                {"email": email, "password": password, "email_confirm": True}
            )
            print(f"Created Supabase user {email} (password: {password})")
            return str(created.user.id)
        except Exception as e:
            print(f"Could not create Supabase user automatically ({e}).")
            print("Set SEED_SUPABASE_USER_ID to a real auth.users id, then re-run seed.")
    return "00000000-0000-0000-0000-0000000000demo"


def seed() -> None:
    settings = get_settings()
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    if not url or not key:
        print("Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
        return
    sb = create_client(url, key)

    if sb.table("firms").select("id").eq("slug", "sterling-tax-advisory").execute().data:
        print("Seed already applied (firm slug sterling-tax-advisory exists).")
        return

    sid = _ensure_demo_supabase_user_id()

    fr = (
        sb.table("firms")
        .insert(
            {
                "name": "Sterling Tax & Advisory",
                "slug": "sterling-tax-advisory",
                "country": "US",
                "plan": Plan.pro.value,
                "plan_client_limit": 50,
            }
        )
        .execute()
    )
    if not fr.data:
        print("Failed to insert firm")
        return
    firm = fr.data[0]
    firm_id = uuid.UUID(str(firm["id"]))

    sb.table("firm_users").insert(
        {
            "firm_id": str(firm_id),
            "supabase_user_id": sid,
            "email": os.getenv("SEED_DEMO_EMAIL", "demo@cpaos.local"),
            "full_name": "Demo Owner",
            "role": FirmUserRole.owner.value,
        }
    ).execute()

    tokens = {
        "prism": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "ramesh": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "dubai": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "horizon": uuid.UUID("44444444-4444-4444-4444-444444444444"),
    }

    def add_client(
        *,
        name: str,
        business: str | None,
        email: str | None,
        country: Country,
        entity: EntityType,
        status: ClientStatus,
        target_pct: int,
        token: uuid.UUID,
        services: list,
    ) -> uuid.UUID:
        link = _portal_link(settings.frontend_url, firm["slug"], token)
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "firm_id": str(firm_id),
            "client_name": name,
            "business_name": business,
            "email": email or f"{name.lower().replace(' ', '')}@example.com".lower(),
            "phone": "+919999999999",
            "country": country.value,
            "entity_type": entity.value,
            "services": services,
            "status": status.value,
            "completion_pct": 0,
            "onboarding_link": link,
            "onboarding_token": str(token),
            "engagement_letter_sent": status == ClientStatus.signature_pending,
            "engagement_letter_signed": status == ClientStatus.completed,
            "completed_at": now if status == ClientStatus.completed else None,
        }
        ins = sb.table("clients").insert(row).execute()
        if not ins.data:
            raise RuntimeError(f"Failed to insert client {name}")
        c = ins.data[0]
        cid = uuid.UUID(str(c["id"]))
        specs = checklist_generator.generate_checklist(country.value, entity.value, services)
        n = max(len(specs), 1)
        verified_cutoff = int(round(n * (target_pct / 100.0)))
        checklist_rows = []
        for idx, spec in enumerate(specs):
            if status == ClientStatus.completed:
                st = ChecklistItemStatus.verified.value
            elif idx < verified_cutoff:
                st = ChecklistItemStatus.verified.value
            elif idx < min(n, verified_cutoff + max(1, n // 8)):
                st = ChecklistItemStatus.uploaded.value
            else:
                st = ChecklistItemStatus.pending.value
            checklist_rows.append(
                {
                    "client_id": str(cid),
                    "category": spec["category"],
                    "item_name": spec["item_name"],
                    "description": spec["description"],
                    "is_required": spec["is_required"],
                    "status": st,
                    "display_order": spec["display_order"],
                }
            )
        if checklist_rows:
            sb.table("checklist_items").insert(checklist_rows).execute()
        recompute_client_completion(sb, cid)
        return cid

    add_client(
        name="Prism Corp",
        business="Prism Corp",
        email="test@sterlingtax.com",
        country=Country.US,
        entity=EntityType.c_corp,
        status=ClientStatus.completed,
        target_pct=100,
        token=tokens["prism"],
        services=["bookkeeping", "tax"],
    )
    add_client(
        name="Johnson LLC",
        business="Johnson LLC",
        email=None,
        country=Country.US,
        entity=EntityType.llc,
        status=ClientStatus.in_progress,
        target_pct=55,
        token=tokens["ramesh"],
        services=["bookkeeping", "tax"],
    )
    add_client(
        name="Dubai Ventures",
        business="Dubai Ventures",
        email=None,
        country=Country.UAE,
        entity=EntityType.private_limited,
        status=ClientStatus.signature_pending,
        target_pct=20,
        token=tokens["dubai"],
        services=["bookkeeping", "vat"],
    )
    add_client(
        name="Horizon Ltd",
        business="Horizon Ltd",
        email=None,
        country=Country.UK,
        entity=EntityType.private_limited,
        status=ClientStatus.documents_pending,
        target_pct=75,
        token=tokens["horizon"],
        services=["bookkeeping", "tax"],
    )

    print("Seed complete.")
    print("Demo portal URLs (public):")
    for label, tok in tokens.items():
        print(f"  {label}: {_portal_link(settings.frontend_url, firm['slug'], tok)}")
    print(f"Demo owner email: {os.getenv('SEED_DEMO_EMAIL', 'demo@cpaos.local')}")


if __name__ == "__main__":
    seed()
