import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class History(Base):
    __tablename__ = "history"
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('upload', 'generate', 'export', 'view', 'edit')",
            name="ck_history_action_type",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(20), nullable=False)
    action_description = Column(Text, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True)
    notes_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="history")
    document = relationship("Document", back_populates="history")
    notes = relationship("Note", back_populates="history")
