"""merge migration heads

Revision ID: f6b09036bb7b
Revises: c8d2e1f4a6b0, f1a2b3c4d5e6
Create Date: 2026-09-15 23:17:12.154342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6b09036bb7b'
down_revision: Union[str, Sequence[str], None] = ('c8d2e1f4a6b0', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
