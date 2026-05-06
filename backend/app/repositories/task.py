from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.enums import TaskDifficulty, TaskStatus
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_random_task(
            self,
            *,
            language_name: str,
            language_display_name: str,
            difficulty: TaskDifficulty,
    ) -> Task | None:
        stmt = (
            select(Task)
            .join(Task.languages)
            .options(selectinload(Task.languages))
            .where(
                Task.status == TaskStatus.PUBLISHED,
                Task.difficulty == difficulty,
                or_(
                    ProgramLanguage.name == language_name,
                    ProgramLanguage.display_name == language_display_name,
                ),
            )
            .order_by(func.random())
            .limit(1)
        )

        return self.db.scalar(stmt)

    def get_task_by_id(self, task_id: int) -> Task | None:
        stmt = (
            select(Task)
            .options(selectinload(Task.languages))
            .where(
                Task.id == task_id,
                Task.status == TaskStatus.PUBLISHED,
            )
        )
        return self.db.scalar(stmt)
