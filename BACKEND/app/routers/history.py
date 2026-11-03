import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.history import History
from app.models.user import User
from app.schemas_history import HistoryCreate, HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryResponse])
def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[History]:
    return (
        db.query(History)
        .filter(History.user_id == current_user.id)
        .order_by(History.created_at.desc())
        .all()
    )


@router.post("", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
def create_history_event(
    payload: HistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> History:
    history_entry = History(
        user_id=current_user.id,
        action_type=payload.action_type,
        action_description=payload.action_description,
        document_id=payload.document_id,
        notes_id=payload.notes_id,
        ip_address=payload.ip_address,
        user_agent=payload.user_agent,
        duration_seconds=payload.duration_seconds,
        metadata_json=payload.metadata,
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry
