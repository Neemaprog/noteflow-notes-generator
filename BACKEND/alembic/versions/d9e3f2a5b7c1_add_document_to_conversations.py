"""add document to conversations

Revision ID: d9e3f2a5b7c1
Revises: c8d2e1f4a6b0
Create Date: 2026-09-15 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d9e3f2a5b7c1"
down_revision: Union[str, Sequence[str], None] = "c8d2e1f4a6b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_conversations_document_id", "conversations", ["document_id"])
    op.create_foreign_key(
        "fk_conversations_document_id_documents",
        "conversations",
        "documents",
        ["document_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_conversations_document_id_documents", "conversations", type_="foreignkey")
    op.drop_index("ix_conversations_document_id", table_name="conversations")
    op.drop_column("conversations", "document_id")
