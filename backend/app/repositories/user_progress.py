from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.user_task_progress import UserTaskProgress


class UserProgressRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

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
