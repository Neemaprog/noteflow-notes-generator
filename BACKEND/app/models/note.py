import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        CheckConstraint(
            "format IN ('markdown', 'html', 'plain_text')",
            name="ck_notes_format",
        ),
        CheckConstraint(
            "style IN ('study_notes', 'presentation', 'mind_map')",
            name="ck_notes_style",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    format = Column(String(20), nullable=False, default="markdown")
    style = Column(String(20), nullable=False, default="study_notes")
    language = Column(String(10), nullable=False, default="en")
    reading_time = Column(Integer, nullable=True)
    includes_visuals = Column(Boolean, nullable=False, default=False)
    includes_tables = Column(Boolean, nullable=False, default=False)
    includes_summary = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)
    is_favorite = Column(Boolean, nullable=False, default=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="notes")
    source_document = relationship(
        "Document", back_populates="source_notes", foreign_keys=[document_id]
    )
    visuals = relationship("Visual", back_populates="notes")
    history = relationship("History", back_populates="notes")
