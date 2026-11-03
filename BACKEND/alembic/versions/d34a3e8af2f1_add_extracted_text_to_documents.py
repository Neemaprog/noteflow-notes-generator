"""add extracted text to documents

Revision ID: d34a3e8af2f1
Revises: b12a9d1d4c82
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d34a3e8af2f1"
down_revision: Union[str, Sequence[str], None] = "b12a9d1d4c82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "extracted_text")
