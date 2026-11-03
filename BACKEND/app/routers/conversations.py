import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from app.models.user import User
from app.schemas_conversations import (
    ConversationCreate,
    ConversationMessageCreate,
    ConversationResponse,
)
from app.services.ai.qwen_service import QwenGenerationError, continue_conversation

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _get_conversation(conversation_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    conversation = Conversation(
        user_id=current_user.id,
        document_id=payload.document_id,
        title=payload.title.strip(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    return _get_conversation(conversation_id, current_user.id, db)


@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
def send_message(
    conversation_id: uuid.UUID,
    payload: ConversationMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    conversation = _get_conversation(conversation_id, current_user.id, db)
    user_message = ConversationMessage(
        conversation_id=conversation.id,
        role="user",
        content=payload.content.strip(),
    )
    db.add(user_message)
    db.flush()

    context = [{"role": message.role, "content": message.content} for message in conversation.messages]
    try:
        assistant_content = continue_conversation(context)
    except QwenGenerationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    db.add(
        ConversationMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_content,
        )
    )
    if conversation.title == "New conversation":
        conversation.title = payload.content.strip()[:80]
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
