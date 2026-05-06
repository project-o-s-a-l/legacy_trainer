from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.enums import TaskDifficulty
from backend.app.models.task import Task
from backend.app.repositories.task import TaskRepository
from backend.app.schemas.task import TaskResponse


class TaskService:
    _LANGUAGE_ALIASES = {
        "python": ("python", "Python"),
        "c++": ("cpp", "C++"),
        "cpp": ("cpp", "C++"),
    }

    def __init__(self, db: Session) -> None:
        self.tasks = TaskRepository(db)

    def list_tasks(self, *, language: str, difficulty: str) -> list[TaskResponse]:
        language_name, language_display_name = self._normalize_language(language)
        difficulty_enum = self._normalize_difficulty(difficulty)

        tasks = self.tasks.get_tasks(
            language_name=language_name,
            language_display_name=language_display_name,
            difficulty=difficulty_enum,
        )

        return [
            self._to_response(
                task,
                preferred_language_name=language_name,
                preferred_language_display_name=language_display_name,
            )
            for task in tasks
        ]

    def get_task(self, task_id: int) -> TaskResponse:
        task = self.tasks.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return self._to_response(task)

    def _normalize_language(self, language: str) -> tuple[str, str]:
        normalized = language.strip().lower()
        result = self._LANGUAGE_ALIASES.get(normalized)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported language",
            )
        return result

    def _normalize_difficulty(self, difficulty: str) -> TaskDifficulty:
        normalized = difficulty.strip().lower()
        try:
            return TaskDifficulty(normalized)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported difficulty",
            ) from exc

    def _to_response(
        self,
        task: Task,
        *,
        preferred_language_name: str | None = None,
        preferred_language_display_name: str | None = None,
    ) -> TaskResponse:
        language = self._resolve_language(
            task,
            preferred_language_name=preferred_language_name,
            preferred_language_display_name=preferred_language_display_name,
        )

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            requirements=task.requirements,
            legacyCode=task.legacy_code,
            difficulty=task.difficulty.value,
            language=language,
        )

    def _resolve_language(
        self,
        task: Task,
        *,
        preferred_language_name: str | None = None,
        preferred_language_display_name: str | None = None,
    ) -> str:
        for item in task.languages:
            if (
                item.name == preferred_language_name
                or item.display_name == preferred_language_display_name
            ):
                return item.name

        if task.languages:
            return task.languages[0].name

        return ""
