from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.onboarding import ChecklistItem, ChecklistItemStatus, Client


def recompute_client_completion(db: Session, client: Client) -> int:
    items = db.query(ChecklistItem).filter(ChecklistItem.client_id == client.id).all()
    if not items:
        client.completion_pct = 0
        return 0
    done = sum(
        1
        for i in items
        if i.status in (ChecklistItemStatus.verified, ChecklistItemStatus.waived)
    )
    pct = int(round(100 * done / len(items)))
    client.completion_pct = pct
    return pct
