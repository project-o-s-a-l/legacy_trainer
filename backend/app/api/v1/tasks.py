from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.task import TaskResponse
from backend.app.services.task import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def get_tasks(
        language: str = Query(..., min_length=1),
        difficulty: str = Query(..., min_length=1),
        db: Session = Depends(get_db),
) -> list[TaskResponse]:
    return TaskService(db).list_tasks(
        language=language,
        difficulty=difficulty,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    return TaskService(db).get_task(task_id)
