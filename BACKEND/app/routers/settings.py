import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.setting import Setting
from app.models.user import User
from app.schemas_settings import SettingsCreate, SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Setting:
    settings = db.query(Setting).filter(Setting.user_id == current_user.id).first()
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    return settings


@router.post("", response_model=SettingsResponse, status_code=status.HTTP_201_CREATED)
def create_settings(
    payload: SettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Setting:
    existing = db.query(Setting).filter(Setting.user_id == current_user.id).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Settings already exist for this user",
        )

    settings = Setting(
        user_id=current_user.id,
        default_notes_style=payload.default_notes_style,
        default_language=payload.default_language,
        export_format=payload.export_format,
        include_summary=payload.include_summary,
        include_visuals=payload.include_visuals,
        notes_tone=payload.notes_tone,
        theme_preference=payload.theme_preference,
        notifications_enabled=payload.notifications_enabled,
        email_notifications=payload.email_notifications,
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.put("", response_model=SettingsResponse)
def update_settings(
    payload: SettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Setting:
    settings = db.query(Setting).filter(Setting.user_id == current_user.id).first()
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")

    for field, value in payload.model_dump().items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings
