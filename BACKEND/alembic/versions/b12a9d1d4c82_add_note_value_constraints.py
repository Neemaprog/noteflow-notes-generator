"""add note format and style constraints

Revision ID: b12a9d1d4c82
Revises: 9b7e2d4c6f10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b12a9d1d4c82"
down_revision: Union[str, Sequence[str], None] = "9b7e2d4c6f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_notes_format",
        "notes",
        "format IN ('markdown', 'html', 'plain_text')",
    )
    op.create_check_constraint(
        "ck_notes_style",
        "notes",
        "style IN ('study_notes', 'presentation', 'mind_map')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_notes_style", "notes", type_="check")
    op.drop_constraint("ck_notes_format", "notes", type_="check")
