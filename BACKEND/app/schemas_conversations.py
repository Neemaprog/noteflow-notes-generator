from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document_id: UUID | None
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageResponse] = []


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=255)
    document_id: UUID | None = None


class ConversationMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
