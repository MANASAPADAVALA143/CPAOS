from __future__ import annotations

import uuid

from supabase import Client

from app.db import repo


def recompute_client_completion(sb: Client, client_id: uuid.UUID) -> int:
    items = repo.checklist_items_for_client(sb, client_id)
    if not items:
        pct = 0
    else:
        done = sum(1 for i in items if i.get("status") in ("verified", "waived"))
        pct = int(round(100 * done / len(items)))
    repo.update_client(sb, client_id, {"completion_pct": pct})
    return pct
