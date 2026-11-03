import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.database import Base


class Visual(Base):
    __tablename__ = "visuals"
    __table_args__ = (
        CheckConstraint(
            "visual_type IN ('graph', 'diagram', 'chart', 'infographic')",
            name="ck_visuals_visual_type",
        ),
        CheckConstraint(
            "file_format IN ('png', 'jpg', 'svg', 'webp')",
            name="ck_visuals_file_format",
        ),
        CheckConstraint(
            "color_scheme IN ('light', 'dark', 'colorful')",
            name="ck_visuals_color_scheme",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notes_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    visual_type = Column(String(20), nullable=False)
    visual_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_format = Column(String(10), nullable=False)
    generation_prompt = Column(Text, nullable=True)
    generation_model = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    color_scheme = Column(String(20), nullable=True)
    position_in_notes = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    notes = relationship("Note", back_populates="visuals")
    user = relationship("User", back_populates="visuals")
