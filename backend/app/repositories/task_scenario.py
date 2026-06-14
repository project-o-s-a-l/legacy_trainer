from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task_scenario import TaskScenario


class TaskScenarioRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_task(
        self,
        *,
        task_id: int,
        language_name: str,
    ) -> list[TaskScenario]:
        stmt = (
            select(TaskScenario)
            .where(
                TaskScenario.task_id == task_id,
                TaskScenario.language_name == language_name,
            )
            .order_by(TaskScenario.order_index.asc(), TaskScenario.id.asc())
        )
        return list(self.db.scalars(stmt).all())
