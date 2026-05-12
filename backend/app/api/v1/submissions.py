from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.submission import (
    SubmissionCheckResponse,
    SubmissionCreateRequest,
    SubmissionCreateResponse,
    SubmissionResponse,
)
from backend.app.services.submission import SubmissionService


router = APIRouter(prefix="/api/v1", tags=["submissions"])


@router.post(
    "/tasks/{task_id}/submit",
    response_model=SubmissionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_solution(
    task_id: int,
    data: SubmissionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionCreateResponse:
    return SubmissionService(db).submit(
        task_id=task_id,
        data=data,
        current_user=current_user,
    )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    return SubmissionService(db).get_submission(
        submission_id=submission_id,
        current_user=current_user,
    )


@router.get(
    "/submissions/{submission_id}/checks",
    response_model=list[SubmissionCheckResponse],
)
def get_submission_checks(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SubmissionCheckResponse]:
    return SubmissionService(db).get_submission_checks(
        submission_id=submission_id,
        current_user=current_user,
    )
