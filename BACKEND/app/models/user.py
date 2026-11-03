import uuid
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    documents = relationship("Document", back_populates="user")
    notes = relationship("Note", back_populates="user")
    visuals = relationship("Visual", back_populates="user")
    processing_jobs = relationship("ProcessingJob", back_populates="user")
    history = relationship("History", back_populates="user")
    settings = relationship("Setting", back_populates="user", uselist=False)
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )