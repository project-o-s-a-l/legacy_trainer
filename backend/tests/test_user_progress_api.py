from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.enums import SubmissionStatus, TaskDifficulty, TaskStatus, UserRole
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.submission import Submission
from backend.app.models.task import Task
from backend.app.models.user import User
from backend.app.models.user_task_progress import UserTaskProgress
from backend.app.services.security import hash_password
from backend.app.services.token import create_access_token


def create_user(
    db_session: Session,
    *,
    username: str = "tester",
    email: str = "tester@example.com",
    login: str = "tester",
    password: str = "password123",
) -> User:
    user = User(
        username=username,
        email=email,
        login=login,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def authenticate_client(client: TestClient, user: User) -> None:
    token = create_access_token(user.id)
    client.cookies.set("access_token", token)


def create_language(
    db_session: Session,
    *,
    name: str = "python",
    display_name: str = "Python",
    version: str = "3.12",
) -> ProgramLanguage:
    language = ProgramLanguage(
        name=name,
        display_name=display_name,
        version=version,
    )
    db_session.add(language)
    db_session.flush()
    db_session.refresh(language)
    return language


def create_task(
    db_session: Session,
    *,
    author: User,
    language: ProgramLanguage,
    title: str,
    difficulty: TaskDifficulty,
) -> Task:
    task = Task(
        title=title,
        description=f"{title} description",
        requirements=f"{title} requirements",
        legacy_code=f"{title} legacy code",
        difficulty=difficulty,
        author_id=author.id,
        status=TaskStatus.PUBLISHED,
        max_score=100,
        languages=[language],
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task


def create_submission(
    db_session: Session,
    *,
    user: User,
    task: Task,
    language: ProgramLanguage,
    score: int,
    status: SubmissionStatus = SubmissionStatus.PASSED,
) -> Submission:
    submission = Submission(
        task_id=task.id,
        user_id=user.id,
        language_id=language.id,
        source_code="print('hello')",
        status=status,
        score=score,
        checked_at=datetime.now(timezone.utc),
        memory_used_kb=256,
        execution_time_ms=10,
    )
    db_session.add(submission)
    db_session.flush()
    db_session.refresh(submission)
    return submission


def create_progress(
    db_session: Session,
    *,
    user: User,
    task: Task,
    best_submission: Submission,
    attempts_count: int,
    is_solved: bool,
) -> UserTaskProgress:
    progress = UserTaskProgress(
        user_id=user.id,
        task_id=task.id,
        best_submission_id=best_submission.id,
        attempts_count=attempts_count,
        is_solved=is_solved,
    )
    db_session.add(progress)
    db_session.flush()
    db_session.refresh(progress)
    return progress


def test_get_me_progress_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/users/me/progress")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_me_progress_returns_zero_stats_for_new_user(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    db_session.commit()

    authenticate_client(client, user)

    response = client.get("/api/v1/users/me/progress")

    assert response.status_code == 200
    body = response.json()

    assert body["tasksCompleted"] == {
        "easy": 0,
        "medium": 0,
        "hard": 0,
    }
    assert body["averageGrade"] == {
        "easy": 0,
        "medium": 0,
        "hard": 0,
    }


def test_get_me_progress_returns_aggregated_stats(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    language = create_language(db_session)

    easy_task_1 = create_task(
        db_session,
        author=user,
        language=language,
        title="Easy task 1",
        difficulty=TaskDifficulty.EASY,
    )
    easy_task_2 = create_task(
        db_session,
        author=user,
        language=language,
        title="Easy task 2",
        difficulty=TaskDifficulty.EASY,
    )
    medium_task = create_task(
        db_session,
        author=user,
        language=language,
        title="Medium task",
        difficulty=TaskDifficulty.MEDIUM,
    )
    hard_task = create_task(
        db_session,
        author=user,
        language=language,
        title="Hard task",
        difficulty=TaskDifficulty.HARD,
    )

    easy_submission_1 = create_submission(
        db_session,
        user=user,
        task=easy_task_1,
        language=language,
        score=80,
    )
    easy_submission_2 = create_submission(
        db_session,
        user=user,
        task=easy_task_2,
        language=language,
        score=100,
    )
    medium_submission = create_submission(
        db_session,
        user=user,
        task=medium_task,
        language=language,
        score=70,
        status=SubmissionStatus.FAILED,
    )
    hard_submission = create_submission(
        db_session,
        user=user,
        task=hard_task,
        language=language,
        score=60,
    )

    create_progress(
        db_session,
        user=user,
        task=easy_task_1,
        best_submission=easy_submission_1,
        attempts_count=2,
        is_solved=True,
    )
    create_progress(
        db_session,
        user=user,
        task=easy_task_2,
        best_submission=easy_submission_2,
        attempts_count=1,
        is_solved=True,
    )
    create_progress(
        db_session,
        user=user,
        task=medium_task,
        best_submission=medium_submission,
        attempts_count=3,
        is_solved=False,
    )
    create_progress(
        db_session,
        user=user,
        task=hard_task,
        best_submission=hard_submission,
        attempts_count=1,
        is_solved=True,
    )

    db_session.commit()

    authenticate_client(client, user)

    response = client.get("/api/v1/users/me/progress")

    assert response.status_code == 200
    body = response.json()

    assert body["tasksCompleted"] == {
        "easy": 2,
        "medium": 0,
        "hard": 1,
    }
    assert body["averageGrade"] == {
        "easy": 90,
        "medium": 70,
        "hard": 60,
    }
