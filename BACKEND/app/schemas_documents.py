from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    extracted_text: str | None
    processing_status: str
    processing_started: datetime | None
    processing_completed: datetime | None
    processing_time: int | None
    total_pages: int | None
    word_count: int | None
    notes_id: UUID | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
