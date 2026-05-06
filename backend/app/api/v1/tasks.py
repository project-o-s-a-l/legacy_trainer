from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.task import TaskResponse
from backend.app.services.task import TaskService


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskResponse)
def get_random_task(
    language: str = Query(..., min_length=1),
    difficulty: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService(db).get_random_task(
        language=language,
        difficulty=difficulty,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    return TaskService(db).get_task(task_id)
