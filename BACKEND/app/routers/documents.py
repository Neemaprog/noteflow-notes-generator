import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import SessionLocal, get_db
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.history import History
from app.models.note import Note
from app.models.processing_job import ProcessingJob
from app.models.user import User
from app.schemas_documents import DocumentResponse
from app.schemas_notes import NoteGenerationRequest, NoteResponse
from app.services.ai.gemini_service import extract_text_from_image
from app.services.ai.whisper_service import transcribe_audio
from app.services.ai.qwen_service import QwenGenerationError, generate_notes
from app.services.extraction import extract_document_text


router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"
ALLOWED_TYPES = {"pdf", "docx", "pptx", "mp3", "wav", "mp4", "jpg", "jpeg", "png","webm"}
TEXT_EXTRACTION_TYPES = {"pdf", "docx", "pptx"}
IMAGE_TYPES = {"jpg", "jpeg", "png"}
AUDIO_TYPES = {"mp3", "wav", "mp4","webm"}


def _process_uploaded_document(document_id: uuid.UUID, user_id: uuid.UUID) -> None:
    db = SessionLocal()
    document = None
    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )
        if document is None:
            return

        document.processing_status = "processing"
        document.processing_started = datetime.now(timezone.utc)
        db.commit()

        job = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.document_id == document_id, ProcessingJob.user_id == user_id)
            .order_by(ProcessingJob.created_at.desc())
            .first()
        )
        if job is not None:
            job.status = "running"
            job.progress_percentage = 25
            job.started_at = document.processing_started
            job.logs = {"message": "Text extraction started", "status": "running"}
            db.commit()

        file_path = Path(__file__).resolve().parents[2] / document.file_path
        if document.file_type in TEXT_EXTRACTION_TYPES:
            extracted_text = extract_document_text(file_path, document.file_type)
        elif document.file_type in IMAGE_TYPES:
            extracted_text = extract_text_from_image(str(file_path))
        elif document.file_type in AUDIO_TYPES:
            extracted_text = transcribe_audio(str(file_path))
        else:
            raise ValueError(f"Unsupported extraction type: {document.file_type}")

        document.extracted_text = extracted_text or None
        document.word_count = len((extracted_text or "").split())
        document.processing_status = "completed"
        document.processing_completed = datetime.now(timezone.utc)
        if document.processing_started is not None:
            delta = document.processing_completed - document.processing_started
            document.processing_time = int(delta.total_seconds())

        if job is not None:
            job.status = "completed"
            job.progress_percentage = 100
            job.completed_at = document.processing_completed
            job.actual_time = document.processing_time
            job.logs = {"message": "Text extraction completed", "status": "completed"}

        db.add(
            History(
                user_id=user_id,
                action_type="generate",
                action_description=f"Extracted text from document: {document.file_name}",
                document_id=document.id,
            )
        )
        db.commit()
    except Exception as exc:  # pragma: no cover - background task failure path
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )
        if document is not None:
            document.processing_status = "failed"
            document.processing_completed = datetime.now(timezone.utc)
            db.commit()

        job = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.document_id == document_id, ProcessingJob.user_id == user_id)
            .order_by(ProcessingJob.created_at.desc())
            .first()
        )
        if job is not None:
            job.status = "failed"
            job.progress_percentage = 0
            job.completed_at = datetime.now(timezone.utc)
            job.error_message = str(exc)
            job.logs = {"message": "Text extraction failed", "status": "failed", "error": str(exc)}
            db.commit()
    finally:
        db.close()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types: {', '.join(sorted(ALLOWED_TYPES))}",
        )

    user_directory = UPLOAD_ROOT / str(current_user.id)
    user_directory.mkdir(parents=True, exist_ok=True)
    stored_path = user_directory / f"{uuid.uuid4()}.{extension}"

    with stored_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

    file_size = stored_path.stat().st_size
    document = Document(
        user_id=current_user.id,
        file_name=file.filename or stored_path.name,
        file_path=str(stored_path.relative_to(UPLOAD_ROOT.parent)),
        file_size=file_size,
        file_type=extension,
        mime_type=file.content_type or "application/octet-stream",
        processing_status="pending",
    )
    db.add(document)
    db.flush()

    processing_job = ProcessingJob(
        user_id=current_user.id,
        document_id=document.id,
        job_type="extract",
        status="queued",
        progress_percentage=0,
    )
    db.add(processing_job)
    db.add(
        History(
            user_id=current_user.id,
            action_type="upload",
            action_description=f"Uploaded document: {document.file_name}",
            document_id=document.id,
        )
    )
    db.commit()
    db.refresh(document)

    background_tasks.add_task(_process_uploaded_document, document.id, current_user.id)

    return document


@router.post("/{document_id}/generate-notes", response_model=NoteResponse)
def generate_document_notes(
    document_id: uuid.UUID,
    payload: NoteGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.processing_status != "completed" or not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document text extraction is not completed",
        )

    try:
        generated = generate_notes(
            document.extracted_text,
            style=payload.style,
            language=payload.language,
            output_format=payload.format,
            custom_instruction=payload.custom_instruction,
        )
    except QwenGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    note = Note(
        user_id=current_user.id,
        document_id=document.id,
        title=generated["title"],
        content=generated["content"],
        summary=generated["summary"],
        format=payload.format,
        style=payload.style,
        language=payload.language,
        reading_time=max(1, len(generated["content"].split()) // 200),
        includes_summary=True,
    )
    db.add(note)
    db.flush()
    document.notes_id = note.id
    conversation = Conversation(
        user_id=current_user.id,
        document_id=document.id,
        title=generated["title"],
    )
    db.add(conversation)
    db.add(
        History(
            user_id=current_user.id,
            action_type="generate",
            action_description=f"Generated notes from document: {document.file_name}",
            document_id=document.id,
            notes_id=note.id,
            metadata_json={"model": settings.QWEN_MODEL, "conversation_id": str(conversation.id)},
        )
    )
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id, Document.is_deleted.is_(False))
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    document.is_deleted = True
    db.add(
        History(
            user_id=current_user.id,
            action_type="edit",
            action_description=f"Deleted document: {document.file_name}",
            document_id=document.id,
        )
    )
    db.commit()
