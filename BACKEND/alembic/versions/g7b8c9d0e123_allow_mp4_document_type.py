"""allow mp4 document type

Revision ID: g7b8c9d0e123
Revises: f6a7b8c9d012
"""

from typing import Sequence, Union

from alembic import op


revision: str = "g7b8c9d0e123"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'mp4', 'jpg', 'jpeg', 'png')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'jpg', 'jpeg', 'png')",
    )
