from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task_check_rule import TaskCheckRule


class TaskCheckRuleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_task(
        self,
        *,
        task_id: int,
        language_name: str,
    ) -> list[TaskCheckRule]:
        stmt = (
            select(TaskCheckRule)
            .where(
                TaskCheckRule.task_id == task_id,
                TaskCheckRule.language_name == language_name,
            )
            .order_by(TaskCheckRule.id.asc())
        )
        return list(self.db.scalars(stmt).all())
