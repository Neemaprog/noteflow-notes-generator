from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID
    action_type: str
    action_description: str
    document_id: UUID | None
    notes_id: UUID | None
    ip_address: str | None
    user_agent: str | None
    duration_seconds: int | None
    metadata_json: dict | None = Field(
        default=None,
        validation_alias=AliasChoices("metadata_json", "metadata"),
        serialization_alias="metadata",
    )
    created_at: datetime


class HistoryCreate(BaseModel):
    action_type: str = Field(..., pattern=r"^(upload|generate|export|view|edit)$")
    action_description: str = Field(..., min_length=1)
    document_id: UUID | None = None
    notes_id: UUID | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    metadata: dict | None = None
