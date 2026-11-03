from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProcessingJobPatch(BaseModel):
    status: str | None = Field(default=None, pattern=r"^(queued|running|completed|failed)$")
    progress_percentage: int | None = Field(default=None, ge=0, le=100)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    estimated_time: int | None = Field(default=None, ge=0)
    actual_time: int | None = Field(default=None, ge=0)
    error_message: str | None = None
    error_code: str | None = None
    retry_count: int | None = Field(default=None, ge=0)
    max_retries: int | None = Field(default=None, ge=0)
    logs: dict | None = None


class ProcessingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document_id: UUID
    job_type: str
    status: str
    progress_percentage: int
    started_at: datetime | None
    completed_at: datetime | None
    estimated_time: int | None
    actual_time: int | None
    error_message: str | None
    error_code: str | None
    retry_count: int
    max_retries: int
    logs: dict | None
    created_at: datetime
    updated_at: datetime
