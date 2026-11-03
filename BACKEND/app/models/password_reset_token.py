import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.sql import expression as sql_expression
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False, server_default=sql_expression.false())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="password_reset_tokens")

    @classmethod
    def create_reset_token(cls, user_id: uuid.UUID, email: str, token: str, expires_in_hours: int = 1):
        return cls(
            user_id=user_id,
            email=email,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        )

    def is_valid(self) -> bool:
        return (
            not self.is_used
            and self.expires_at > datetime.now(timezone.utc)
        )
