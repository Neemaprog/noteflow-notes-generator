"""fix document file type constraint

Revision ID: f6a7b8c9d012
Revises: b4d16e661f76
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f6a7b8c9d012"
down_revision: Union[str, Sequence[str], None] = "b4d16e661f76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'jpg', 'jpeg', 'png')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_documents_file_type", "documents", type_="check")
    op.create_check_constraint(
        "ck_documents_file_type",
        "documents",
        "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav')",
    )
