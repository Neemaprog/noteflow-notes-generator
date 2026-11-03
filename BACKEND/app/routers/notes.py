import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.document import Document
from app.models.note import Note
from app.models.user import User
from app.schemas_exports import NoteExportRequest
from app.schemas_notes import NoteCreate, NoteGenerationRequest, NoteResponse, NoteUpdate
from app.services.note_export import export_note_response
from app.services.ai.qwen_service import generate_notes, QwenGenerationError

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
def list_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Note]:
    return (
        db.query(Note)
        .filter(Note.user_id == current_user.id)
        .order_by(Note.created_at.desc())
        .all()
    )


@router.post("/generate", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def generate_note(
    payload: NoteGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    document = (
        db.query(Document)
        .filter(
            Document.id == payload.document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.processing_status != "completed" or not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not ready yet. Wait for extraction to complete.",
        )

    try:
        result = generate_notes(
            document.extracted_text,
            style=payload.style,
            language=payload.language,
            output_format=payload.format,
            custom_instruction=payload.custom_instruction,
        )
    except QwenGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    note = Note(
        user_id=current_user.id,
        document_id=document.id,
        title=result["title"],
        content=result["content"],
        summary=result["summary"],
        format=payload.format,
        style=payload.style,
        language=payload.language,
        includes_summary=True,
    )
    db.add(note)
    db.flush()
    if document.notes_id is None:
        document.notes_id = note.id
    db.add(document)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/{note_id}/export")
def export_note(
    note_id: uuid.UUID,
    payload: NoteExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return export_note_response(note, payload.format)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    document = (
        db.query(Document)
        .filter(
            Document.id == payload.document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or not owned by user",
        )

    note = Note(
        user_id=current_user.id,
        document_id=document.id,
        title=payload.title.strip(),
        content=payload.content,
        summary=payload.summary,
        format=payload.format,
        style=payload.style,
        language=payload.language,
        reading_time=payload.reading_time,
        includes_visuals=payload.includes_visuals,
        includes_tables=payload.includes_tables,
        includes_summary=payload.includes_summary,
        version=payload.version,
        is_favorite=payload.is_favorite,
        is_archived=payload.is_archived,
    )
    db.add(note)
    db.flush()

    if document.notes_id is None:
        document.notes_id = note.id

    db.add(document)
    db.commit()
    db.refresh(note)
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: uuid.UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    if payload.title is not None:
        note.title = payload.title.strip()

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    db.delete(note)
    db.commit()
