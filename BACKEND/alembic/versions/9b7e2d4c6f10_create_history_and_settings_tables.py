"""create history and settings tables

Revision ID: 9b7e2d4c6f10
Revises: 7c1e5a9d4b32
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "9b7e2d4c6f10"
down_revision: Union[str, Sequence[str], None] = "7c1e5a9d4b32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=20), nullable=False),
        sa.Column("action_description", sa.Text(), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "action_type IN ('upload', 'generate', 'export', 'view', 'edit')",
            name="ck_history_action_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["notes_id"], ["notes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_history_user_id", "history", ["user_id"])
    op.create_index("ix_history_document_id", "history", ["document_id"])
    op.create_index("ix_history_notes_id", "history", ["notes_id"])

    op.create_table(
        "settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("default_notes_style", sa.String(length=20), nullable=False),
        sa.Column("default_language", sa.String(length=10), nullable=False),
        sa.Column("export_format", sa.String(length=20), nullable=False),
        sa.Column("include_summary", sa.Boolean(), nullable=False),
        sa.Column("include_visuals", sa.Boolean(), nullable=False),
        sa.Column("notes_tone", sa.String(length=20), nullable=False),
        sa.Column("theme_preference", sa.String(length=10), nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_notifications", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "default_notes_style IN ('summary', 'detailed', 'bullet_points')",
            name="ck_settings_default_notes_style",
        ),
        sa.CheckConstraint(
            "export_format IN ('pdf', 'docx', 'markdown')",
            name="ck_settings_export_format",
        ),
        sa.CheckConstraint(
            "notes_tone IN ('professional', 'casual', 'academic')",
            name="ck_settings_notes_tone",
        ),
        sa.CheckConstraint(
            "theme_preference IN ('light', 'dark', 'system')",
            name="ck_settings_theme_preference",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_settings_user_id"),
    )
    op.create_index("ix_settings_user_id", "settings", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_settings_user_id", table_name="settings")
    op.drop_table("settings")
    op.drop_index("ix_history_notes_id", table_name="history")
    op.drop_index("ix_history_document_id", table_name="history")
    op.drop_index("ix_history_user_id", table_name="history")
    op.drop_table("history")
