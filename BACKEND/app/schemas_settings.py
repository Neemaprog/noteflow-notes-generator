from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SettingsCreate(BaseModel):
    default_notes_style: str = Field(..., pattern=r"^(summary|detailed|bullet_points)$")
    default_language: str = Field(..., min_length=2, max_length=10)
    export_format: str = Field(..., pattern=r"^(pdf|docx|markdown)$")
    include_summary: bool = True
    include_visuals: bool = True
    notes_tone: str = Field(..., pattern=r"^(professional|casual|academic)$")
    theme_preference: str = Field(..., pattern=r"^(light|dark|system)$")
    notifications_enabled: bool = True
    email_notifications: bool = True


class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    default_notes_style: str
    default_language: str
    export_format: str
    include_summary: bool
    include_visuals: bool
    notes_tone: str
    theme_preference: str
    notifications_enabled: bool
    email_notifications: bool
    created_at: datetime
    updated_at: datetime
