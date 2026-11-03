from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import (
    create_password_reset_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
)
from app.database import get_db
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest
from app.services.email_service import email_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    email = str(request.email).lower()
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return ForgotPasswordResponse(
            message="If an account with that email exists, a password reset link will be sent."
        )
    
    # Invalidate any existing reset tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False,
    ).update({"is_used": True})
    
    # Create new reset token
    reset_token_str = create_password_reset_token(user.id)
    reset_token = PasswordResetToken.create_reset_token(
        user_id=user.id,
        email=email,
        token=reset_token_str,
        expires_in_hours=1,
    )
    
    db.add(reset_token)
    db.commit()
    
    # Send email with reset link
    reset_link = f"http://localhost:5173/reset-password?token={reset_token_str}"
    email_service.send_password_reset_email(email, reset_link)
    
    return ForgotPasswordResponse(
        message="If an account with that email exists, a password reset link will be sent."
    )


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    user_id = verify_password_reset_token(request.token)
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request.token,
        PasswordResetToken.user_id == user_id,
    ).first()
    
    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    reset_token.is_used = True
    reset_token.used_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"message": "Password reset successful. You can now login with your new password."}
