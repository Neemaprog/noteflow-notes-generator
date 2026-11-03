import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models.note import Note
from app.models.user import User
from app.models.visual import Visual
from app.schemas_visuals import VisualCreate, VisualGenerationRequest, VisualResponse
from app.services.ai.qwen_service import QwenGenerationError, generate_visual

router = APIRouter(prefix="/notes", tags=["visuals"])
VISUAL_ROOT = Path(__file__).resolve().parents[2] / "uploads"


@router.get("/visuals/{visual_id}/file")
def get_visual_file(
    visual_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    visual = (
        db.query(Visual)
        .filter(Visual.id == visual_id, Visual.user_id == current_user.id)
        .first()
    )
    if visual is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visual not found")
    file_path = Path(__file__).resolve().parents[2] / visual.file_path
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visual file not found")
    return Response(content=file_path.read_bytes(), media_type="image/svg+xml")


@router.get("/{note_id}/visuals", response_model=list[VisualResponse])
def list_visuals(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Visual]:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    return (
        db.query(Visual)
        .filter(Visual.notes_id == note_id, Visual.user_id == current_user.id)
        .order_by(Visual.created_at.desc())
        .all()
    )


@router.post(
    "/{note_id}/generate-visual",
    response_model=VisualResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_note_visual(
    note_id: uuid.UUID,
    payload: VisualGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Visual:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    try:
        generated = generate_visual(
            note.content,
            visual_type=payload.visual_type,
            prompt=payload.prompt,
            color_scheme=payload.color_scheme,
        )
    except QwenGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    visual_directory = VISUAL_ROOT / str(current_user.id) / "visuals"
    visual_directory.mkdir(parents=True, exist_ok=True)
    stored_path = visual_directory / f"{uuid.uuid4()}.svg"
    svg_bytes = generated["svg"].encode("utf-8")
    stored_path.write_bytes(svg_bytes)

    visual = Visual(
        notes_id=note.id,
        user_id=current_user.id,
        visual_type=payload.visual_type,
        visual_name=generated["name"].strip(),
        description=generated["description"].strip() or None,
        file_path=str(stored_path.relative_to(VISUAL_ROOT.parent)),
        file_size=len(svg_bytes),
        file_format="svg",
        generation_prompt=payload.prompt.strip(),
        generation_model=settings.QWEN_MODEL,
        width=1200,
        height=800,
        color_scheme=payload.color_scheme,
        position_in_notes=payload.position_in_notes,
    )
    db.add(visual)
    db.commit()
    db.refresh(visual)
    return visual


@router.post("/{note_id}/visuals", response_model=VisualResponse, status_code=status.HTTP_201_CREATED)
def create_visual(
    note_id: uuid.UUID,
    payload: VisualCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Visual:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    visual = Visual(
        notes_id=note.id,
        user_id=current_user.id,
        visual_type=payload.visual_type,
        visual_name=payload.visual_name.strip(),
        description=payload.description,
        file_path=payload.file_path,
        file_size=payload.file_size,
        file_format=payload.file_format,
        generation_prompt=payload.generation_prompt,
        generation_model=payload.generation_model,
        width=payload.width,
        height=payload.height,
        color_scheme=payload.color_scheme,
        position_in_notes=payload.position_in_notes,
        created_at=datetime.utcnow(),
    )
    db.add(visual)
    db.commit()
    db.refresh(visual)
    return visual
