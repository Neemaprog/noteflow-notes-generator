import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.processing_job import ProcessingJob
from app.models.user import User
from app.schemas_processing_jobs import ProcessingJobPatch, ProcessingJobResponse

router = APIRouter(prefix="/processing-jobs", tags=["processing-jobs"])


@router.get("", response_model=list[ProcessingJobResponse])
def list_processing_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProcessingJob]:
    return (
        db.query(ProcessingJob)
        .filter(ProcessingJob.user_id == current_user.id)
        .order_by(ProcessingJob.created_at.desc())
        .all()
    )


@router.get("/{job_id}", response_model=ProcessingJobResponse)
def get_processing_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProcessingJob:
    job = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.id == job_id, ProcessingJob.user_id == current_user.id)
        .first()
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found",
        )
    return job


@router.patch("/{job_id}", response_model=ProcessingJobResponse)
def update_processing_job(
    job_id: uuid.UUID,
    payload: ProcessingJobPatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProcessingJob:
    job = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.id == job_id, ProcessingJob.user_id == current_user.id)
        .first()
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    if payload.status is not None and payload.status == "running" and job.started_at is None:
        job.started_at = datetime.now(timezone.utc)
    if payload.status is not None and payload.status == "completed" and job.completed_at is None:
        job.completed_at = datetime.now(timezone.utc)
    if payload.status is not None and payload.status == "failed" and job.completed_at is None:
        job.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(job)
    return job
