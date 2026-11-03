from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VisualCreate(BaseModel):
    visual_type: str = Field(..., pattern=r"^(graph|diagram|chart|infographic)$")
    visual_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    file_path: str = Field(..., min_length=1, max_length=1024)
    file_size: int = Field(..., ge=0)
    file_format: str = Field(..., pattern=r"^(png|jpg|svg|webp)$")
    generation_prompt: str = Field(..., min_length=1, max_length=4000)
    generation_model: str | None = None
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)
    color_scheme: str | None = Field(default=None, pattern=r"^(light|dark|colorful)$")
    position_in_notes: int = Field(default=0, ge=0)


class VisualGenerationRequest(BaseModel):
    visual_type: str = Field(..., pattern=r"^(graph|diagram|chart|infographic)$")
    prompt: str = Field(..., min_length=1, max_length=4000)
    file_format: str = Field(default="svg", pattern=r"^svg$")
    color_scheme: str = Field(default="light", pattern=r"^(light|dark|colorful)$")
    position_in_notes: int = Field(default=0, ge=0)


class VisualResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notes_id: UUID
    user_id: UUID
    visual_type: str
    visual_name: str
    description: str | None
    file_path: str
    file_size: int
    file_format: str
    generation_prompt: str | None
    generation_model: str | None
    width: int | None
    height: int | None
    color_scheme: str | None
    position_in_notes: int
    created_at: datetime
