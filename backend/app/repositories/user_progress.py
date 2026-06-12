from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from backend.app.db.enums import SubmissionStatus
from backend.app.models.submission import Submission
from backend.app.models.user_task_progress import UserTaskProgress


class UserProgressRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_and_task(
        self,
        *,
        user_id: int,
        task_id: int,
    ) -> UserTaskProgress | None:
        stmt = (
            select(UserTaskProgress)
            .options(selectinload(UserTaskProgress.best_submission))
            .where(
                UserTaskProgress.user_id == user_id,
                UserTaskProgress.task_id == task_id,
            )
        )
        return self.db.scalar(stmt)

    def create_progress(
        self,
        *,
        user_id: int,
        task_id: int,
        best_submission_id: int,
        first_submission_at: datetime,
        last_submission_at: datetime,
        attempts_count: int,
        is_solved: bool,
    ) -> UserTaskProgress:
        progress = UserTaskProgress(
            user_id=user_id,
            task_id=task_id,
            best_submission_id=best_submission_id,
            first_submission_at=first_submission_at,
            last_submission_at=last_submission_at,
            attempts_count=attempts_count,
            is_solved=is_solved,
        )
        self.db.add(progress)
        self.db.flush()
        self.db.refresh(progress)
        return progress

    def update_progress(
        self,
        progress: UserTaskProgress,
        *,
        best_submission_id: int | None = None,
        attempts_count: int | None = None,
        last_submission_at: datetime | None = None,
        is_solved: bool | None = None,
    ) -> None:
        if best_submission_id is not None:
            progress.best_submission_id = best_submission_id
        if attempts_count is not None:
            progress.attempts_count = attempts_count
        if last_submission_at is not None:
            progress.last_submission_at = last_submission_at
        if is_solved is not None:
            progress.is_solved = is_solved

    def get_total_best_score(self, *, user_id: int) -> int:
        stmt = (
            select(func.coalesce(func.sum(Submission.score), 0))
            .join(
                UserTaskProgress,
                UserTaskProgress.best_submission_id == Submission.id,
            )
            .where(
                UserTaskProgress.user_id == user_id,
                UserTaskProgress.is_solved.is_(True),
                Submission.status == SubmissionStatus.PASSED,
            )
        )
        result = self.db.scalar(stmt)
        return int(result or 0)

    def get_user_progress_rows(self, user_id: int) -> list[UserTaskProgress]:
        stmt = (
            select(UserTaskProgress)
            .options(
                selectinload(UserTaskProgress.task),
                selectinload(UserTaskProgress.best_submission),
            )
            .where(UserTaskProgress.user_id == user_id)
        )
        return list(self.db.scalars(stmt).all())
