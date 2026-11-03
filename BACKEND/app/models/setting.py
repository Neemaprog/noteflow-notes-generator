import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_settings_user_id"),
        CheckConstraint(
            "default_notes_style IN ('summary', 'detailed', 'bullet_points')",
            name="ck_settings_default_notes_style",
        ),
        CheckConstraint(
            "export_format IN ('pdf', 'docx', 'markdown')",
            name="ck_settings_export_format",
        ),
        CheckConstraint(
            "notes_tone IN ('professional', 'casual', 'academic')",
            name="ck_settings_notes_tone",
        ),
        CheckConstraint(
            "theme_preference IN ('light', 'dark', 'system')",
            name="ck_settings_theme_preference",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    default_notes_style = Column(String(20), nullable=False, default="summary")
    default_language = Column(String(10), nullable=False, default="en")
    export_format = Column(String(20), nullable=False, default="pdf")
    include_summary = Column(Boolean, nullable=False, default=True)
    include_visuals = Column(Boolean, nullable=False, default=True)
    notes_tone = Column(String(20), nullable=False, default="professional")
    theme_preference = Column(String(10), nullable=False, default="system")
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    email_notifications = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="settings")
