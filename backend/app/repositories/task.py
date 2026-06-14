from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.enums import SubmissionCheckType, TaskDifficulty, TaskStatus
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.task_check_spec import TaskCheckSpec


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
            .options(
                selectinload(Task.languages),
                selectinload(Task.check_specs),
            )
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
            .options(
                selectinload(Task.languages),
                selectinload(Task.check_specs),
            )
            .where(
                Task.id == task_id,
                Task.status == TaskStatus.PUBLISHED,
            )
        )
        return self.db.scalar(stmt)

    def create_check_spec(
            self,
            *,
            task_id: int,
            check_type: SubmissionCheckType,
            name: str,
            weight: int = 100,
            timeout_seconds: int = 10,
            is_required: bool = True,
            order: int = 0,
            config_json: dict[str, Any] | None = None,
    ) -> TaskCheckSpec:
        check_spec = TaskCheckSpec(
            task_id=task_id,
            check_type=check_type,
            name=name,
            weight=weight,
            timeout_seconds=timeout_seconds,
            is_required=is_required,
            order=order,
            config_json=config_json or {},
        )
        self.db.add(check_spec)
        self.db.flush()
        self.db.refresh(check_spec)
        return check_spec

    def list_check_specs_by_task_id(self, task_id: int) -> list[TaskCheckSpec]:
        stmt = (
            select(TaskCheckSpec)
            .where(TaskCheckSpec.task_id == task_id)
            .order_by(TaskCheckSpec.order, TaskCheckSpec.id)
        )
        return list(self.db.scalars(stmt))
