from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.enums import TaskDifficulty, TaskStatus, UserRole
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.user import User
from backend.app.services.security import hash_password
from backend.app.services.token import create_access_token


def create_user(
    db_session: Session,
    *,
    username: str = "submitter",
    email: str = "submitter@example.com",
    login: str = "submitter",
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
    name: str,
    display_name: str,
    version: str,
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
    status: TaskStatus,
) -> Task:
    task = Task(
        title=title,
        description=f"{title} description",
        requirements=f"{title} requirements",
        legacy_code=f"{title} legacy code",
        difficulty=difficulty,
        author_id=author.id,
        status=status,
        max_score=100,
        languages=[language],
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task


def create_submission_for_user(
    client: TestClient,
    db_session: Session,
) -> tuple[User, Task, int]:
    user = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Submission task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "def solve(x):\n    return x * 2\nprint(solve(2))",
            "language": "python",
        },
    )

    assert response.status_code == 201
    submission_id = response.json()["submissionId"]
    return user, task, submission_id


def test_submit_solution_success(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Submit success task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "def solve(x):\n    return x + 1\nprint(solve(2))",
            "language": "python",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["submissionId"] > 0
    assert body["taskId"] == task.id
    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "All tests passed"
    assert body["testPassed"] == 3


def test_submit_solution_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tasks/1/submit",
        json={
            "code": "print('hello')",
            "language": "python",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_submit_solution_returns_404_for_missing_task(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        "/api/v1/tasks/999/submit",
        json={
            "code": "print('hello')",
            "language": "python",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_submit_solution_returns_400_for_unsupported_language(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Unsupported language task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "print('hello')",
            "language": "java",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported language"


def test_submit_solution_returns_400_for_unavailable_task_language(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    create_language(
        db_session,
        name="cpp",
        display_name="C++",
        version="17",
    )
    task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Unavailable language task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "int main() { return 0; }",
            "language": "cpp",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Language is not available for this task"


def test_get_submission_returns_submission(
    client: TestClient,
    db_session: Session,
) -> None:
    user, task, submission_id = create_submission_for_user(client, db_session)

    response = client.get(f"/api/v1/submissions/{submission_id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == submission_id
    assert body["taskId"] == task.id
    assert body["userId"] == user.id
    assert body["language"] == "python"
    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["submittedAt"] is not None
    assert body["checkedAt"] is not None


def test_get_submission_checks_returns_checks(
    client: TestClient,
    db_session: Session,
) -> None:
    _, _, submission_id = create_submission_for_user(client, db_session)

    response = client.get(f"/api/v1/submissions/{submission_id}/checks")

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert body[0]["checkType"] == "tests"
    assert body[0]["status"] == "passed"
    assert body[0]["score"] == 100
    assert body[0]["report"]["passed"] == 3
    assert body[0]["report"]["failed"] == 0


def test_get_submission_returns_403_for_other_user(
    client: TestClient,
    db_session: Session,
) -> None:
    owner, _, submission_id = create_submission_for_user(client, db_session)

    other_user = create_user(
        db_session,
        username="other",
        email="other@example.com",
        login="other",
    )
    db_session.commit()

    authenticate_client(client, other_user)

    response = client.get(f"/api/v1/submissions/{submission_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"
