from pydantic import BaseModel, Field


class NoteExportRequest(BaseModel):
    format: str = Field(pattern=r"^(pdf|pptx|docx|plain_text)$")
