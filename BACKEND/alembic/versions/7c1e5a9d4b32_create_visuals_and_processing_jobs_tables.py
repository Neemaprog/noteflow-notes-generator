"""create visuals and processing_jobs tables

Revision ID: 7c1e5a9d4b32
Revises: 4a3d8f1e2b77
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "7c1e5a9d4b32"
down_revision: Union[str, Sequence[str], None] = "4a3d8f1e2b77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "visuals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notes_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("visual_type", sa.String(length=20), nullable=False),
        sa.Column("visual_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_format", sa.String(length=10), nullable=False),
        sa.Column("generation_prompt", sa.Text(), nullable=True),
        sa.Column("generation_model", sa.String(length=100), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("color_scheme", sa.String(length=20), nullable=True),
        sa.Column("position_in_notes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "visual_type IN ('graph', 'diagram', 'chart', 'infographic')",
            name="ck_visuals_visual_type",
        ),
        sa.CheckConstraint(
            "file_format IN ('png', 'jpg', 'svg', 'webp')",
            name="ck_visuals_file_format",
        ),
        sa.CheckConstraint(
            "color_scheme IN ('light', 'dark', 'colorful')",
            name="ck_visuals_color_scheme",
        ),
        sa.ForeignKeyConstraint(["notes_id"], ["notes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_visuals_notes_id", "visuals", ["notes_id"])
    op.create_index("ix_visuals_user_id", "visuals", ["user_id"])

    op.create_table(
        "processing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_time", sa.Integer(), nullable=True),
        sa.Column("actual_time", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("logs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "job_type IN ('upload', 'extract', 'summarize', 'export')",
            name="ck_processing_jobs_job_type",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_processing_jobs_status",
        ),
        sa.CheckConstraint(
            "progress_percentage BETWEEN 0 AND 100",
            name="ck_processing_jobs_progress_percentage",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_processing_jobs_user_id", "processing_jobs", ["user_id"])
    op.create_index("ix_processing_jobs_document_id", "processing_jobs", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_processing_jobs_document_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_user_id", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    op.drop_index("ix_visuals_user_id", table_name="visuals")
    op.drop_index("ix_visuals_notes_id", table_name="visuals")
    op.drop_table("visuals")
