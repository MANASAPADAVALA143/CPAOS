"""bootstrap schema via SQLAlchemy metadata

Revision ID: 001
Revises:
Create Date: 2026-04-11

"""

from typing import Sequence, Union

from alembic import op

from app.db.base import Base

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from app.models import onboarding  # noqa: F401

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    from app.models import onboarding  # noqa: F401

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
