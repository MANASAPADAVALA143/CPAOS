"""Seed demo firm + 4 clients (Task 15). Run after migrations."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

load_dotenv()

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import SessionLocal
from app.models.onboarding import (
    ChecklistItem,
    ChecklistItemStatus,
    Client,
    ClientStatus,
    Country,
    EntityType,
    Firm,
    FirmUser,
    FirmUserRole,
    Plan,
)
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
            from supabase import create_client
        except ImportError as e:
            print(f"Supabase SDK import failed ({e}); set SEED_SUPABASE_USER_ID manually.")
            return "00000000-0000-0000-0000-0000000000demo"
        sb = create_client(url, key)
        try:
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
    db: Session = SessionLocal()
    try:
        if db.query(Firm).filter(Firm.slug == "demo-accounting").first():
            print("Seed already applied (firm slug demo-accounting exists).")
            return

        sid = _ensure_demo_supabase_user_id()

        firm = Firm(
            name="Demo Accounting LLP",
            slug="demo-accounting",
            country="India",
            plan=Plan.pro,
            plan_client_limit=50,
        )
        db.add(firm)
        db.flush()

        owner = FirmUser(
            firm_id=firm.id,
            supabase_user_id=sid,
            email=os.getenv("SEED_DEMO_EMAIL", "demo@cpaos.local"),
            full_name="Demo Owner",
            role=FirmUserRole.owner,
        )
        db.add(owner)
        db.flush()

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
            country: Country,
            entity: EntityType,
            status: ClientStatus,
            target_pct: int,
            token: uuid.UUID,
            services: list,
        ) -> None:
            c = Client(
                firm_id=firm.id,
                client_name=name,
                business_name=business,
                email=f"{name.lower().replace(' ', '')}@example.com",
                phone="+919999999999",
                country=country,
                entity_type=entity,
                services=services,
                status=status,
                completion_pct=0,
                onboarding_link="",
                onboarding_token=token,
                engagement_letter_sent=status == ClientStatus.signature_pending,
                engagement_letter_signed=status == ClientStatus.completed,
                completed_at=datetime.utcnow() if status == ClientStatus.completed else None,
            )
            c.onboarding_link = _portal_link(settings.frontend_url, firm.slug, token)
            db.add(c)
            db.flush()
            specs = checklist_generator.generate_checklist(country.value, entity.value, services)
            n = max(len(specs), 1)
            verified_cutoff = int(round(n * (target_pct / 100.0)))
            for idx, spec in enumerate(specs):
                if status == ClientStatus.completed:
                    st = ChecklistItemStatus.verified
                elif idx < verified_cutoff:
                    st = ChecklistItemStatus.verified
                elif idx < min(n, verified_cutoff + max(1, n // 8)):
                    st = ChecklistItemStatus.uploaded
                else:
                    st = ChecklistItemStatus.pending
                db.add(
                    ChecklistItem(
                        client_id=c.id,
                        category=spec["category"],
                        item_name=spec["item_name"],
                        description=spec["description"],
                        is_required=spec["is_required"],
                        status=st,
                        display_order=spec["display_order"],
                    )
                )
            recompute_client_completion(db, c)
            db.flush()

        add_client(
            name="Prism Manufacturing Ltd",
            business="Prism Manufacturing Ltd",
            country=Country.India,
            entity=EntityType.private_limited,
            status=ClientStatus.completed,
            target_pct=100,
            token=tokens["prism"],
            services=["bookkeeping", "tax", "gst"],
        )
        add_client(
            name="Ramesh Traders",
            business=None,
            country=Country.India,
            entity=EntityType.partnership,
            status=ClientStatus.in_progress,
            target_pct=55,
            token=tokens["ramesh"],
            services=["bookkeeping", "tax"],
        )
        add_client(
            name="Dubai Ventures LLC",
            business="Dubai Ventures LLC",
            country=Country.UAE,
            entity=EntityType.private_limited,
            status=ClientStatus.signature_pending,
            target_pct=20,
            token=tokens["dubai"],
            services=["bookkeeping", "vat"],
        )
        add_client(
            name="Horizon Consulting Ltd",
            business="Horizon Consulting Ltd",
            country=Country.UK,
            entity=EntityType.private_limited,
            status=ClientStatus.documents_pending,
            target_pct=75,
            token=tokens["horizon"],
            services=["bookkeeping", "tax"],
        )

        db.commit()
        print("Seed complete.")
        print("Demo portal URLs (public):")
        for label, tok in tokens.items():
            print(f"  {label}: {_portal_link(settings.frontend_url, firm.slug, tok)}")
        print(f"Demo owner email: {owner.email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
