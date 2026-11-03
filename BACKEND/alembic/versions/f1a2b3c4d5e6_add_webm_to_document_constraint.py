"""add webm to document file type constraint

Revision ID: f1a2b3c4d5e6
Revises: f0f588460941
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "f0f588460941"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'mp4', 'webm', 'jpg', 'jpeg', 'png')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'mp4', 'jpg', 'jpeg', 'png')",
    )
