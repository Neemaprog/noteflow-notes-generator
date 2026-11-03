from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    document_id: UUID
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    summary: str | None = None
    format: str = "markdown"
    style: str = "study_notes"
    language: str = "en"
    reading_time: int | None = None
    includes_visuals: bool = False
    includes_tables: bool = False
    includes_summary: bool = False
    version: int = 1
    is_favorite: bool = False
    is_archived: bool = False


class NoteGenerationRequest(BaseModel):
    document_id: UUID
    style: str = Field(
        default="study_notes",
        pattern=r"^(study_notes|exam_summary|simple_explanation|presentation|mind_map)$",
    )
    language: str = Field(default="en", min_length=2, max_length=10)
    format: str = Field(default="plain_text", pattern=r"^(markdown|html|plain_text)$")
    custom_instruction: str | None = Field(default=None, max_length=2000)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    format: str | None = None
    style: str | None = None
    language: str | None = None
    reading_time: int | None = None
    includes_visuals: bool | None = None
    includes_tables: bool | None = None
    includes_summary: bool | None = None
    version: int | None = None
    is_favorite: bool | None = None
    is_archived: bool | None = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document_id: UUID
    title: str
    content: str
    summary: str | None
    format: str
    style: str
    language: str
    reading_time: int | None
    includes_visuals: bool
    includes_tables: bool
    includes_summary: bool
    version: int
    is_favorite: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
