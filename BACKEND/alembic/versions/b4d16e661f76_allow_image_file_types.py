"""allow image file types

Revision ID: b4d16e661f76
Revises: d34a3e8af2f1
Create Date: 2026-09-06 00:15:08.644039

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b4d16e661f76'
down_revision: Union[str, Sequence[str], None] = 'd34a3e8af2f1'
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
