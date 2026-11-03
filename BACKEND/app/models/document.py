import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "file_type IN ('pdf', 'docx', 'pptx', 'mp3', 'wav', 'mp4', 'jpg', 'jpeg', 'png','webm')",
            name="ck_documents_file_type",
        ),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_documents_processing_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    mime_type = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    processing_status = Column(String(20), nullable=False, default="pending")
    processing_started = Column(DateTime(timezone=True), nullable=True)
    processing_completed = Column(DateTime(timezone=True), nullable=True)
    processing_time = Column(Integer, nullable=True)
    total_pages = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    notes_id = Column(
        UUID(as_uuid=True), ForeignKey("notes.id", use_alter=True), nullable=True, index=True
    )
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="documents")
    source_notes = relationship(
        "Note",
        back_populates="source_document",
        foreign_keys="Note.document_id",
    )
    processing_jobs = relationship("ProcessingJob", back_populates="document")
    history = relationship("History", back_populates="document")
    conversations = relationship("Conversation", back_populates="document")
