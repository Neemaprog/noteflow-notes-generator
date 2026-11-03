"""merge migration heads

Revision ID: 0e4c3d810576
Revises: d9e3f2a5b7c1, f6b09036bb7b
Create Date: 2026-09-15 23:48:12.858523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e4c3d810576'
down_revision: Union[str, Sequence[str], None] = ('d9e3f2a5b7c1', 'f6b09036bb7b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
