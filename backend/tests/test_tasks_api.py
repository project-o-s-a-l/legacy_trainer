from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.enums import TaskDifficulty, TaskStatus, UserRole
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.user import User


def create_user(db_session: Session) -> User:
    user = User(
        username="author",
        email="author@example.com",
        login="author",
        password_hash="hashed-password",
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


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


def test_get_random_task_returns_one_matching_task(
    client: TestClient,
    db_session: Session,
) -> None:
    author = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    cpp_language = create_language(
        db_session,
        name="cpp",
        display_name="C++",
        version="17",
    )

    matching_task_1 = create_task(
        db_session,
        author=author,
        language=python_language,
        title="Python easy task 1",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    matching_task_2 = create_task(
        db_session,
        author=author,
        language=python_language,
        title="Python easy task 2",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )

    create_task(
        db_session,
        author=author,
        language=python_language,
        title="Python hard task",
        difficulty=TaskDifficulty.HARD,
        status=TaskStatus.PUBLISHED,
    )
    create_task(
        db_session,
        author=author,
        language=cpp_language,
        title="Cpp easy task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_task(
        db_session,
        author=author,
        language=python_language,
        title="Draft python easy task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.DRAFT,
    )
    db_session.commit()

    response = client.get(
        "/api/v1/tasks",
        params={"language": "Python", "difficulty": "Easy"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"] in {matching_task_1.id, matching_task_2.id}
    assert body["title"] in {"Python easy task 1", "Python easy task 2"}
    assert body["description"] in {
        "Python easy task 1 description",
        "Python easy task 2 description",
    }
    assert body["requirements"] in {
        "Python easy task 1 requirements",
        "Python easy task 2 requirements",
    }
    assert body["legacyCode"] in {
        "Python easy task 1 legacy code",
        "Python easy task 2 legacy code",
    }
    assert body["difficulty"] == "easy"
    assert body["language"] == "python"


def test_get_random_task_returns_404_when_no_matches(
    client: TestClient,
    db_session: Session,
) -> None:
    author = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )

    create_task(
        db_session,
        author=author,
        language=python_language,
        title="Only hard task",
        difficulty=TaskDifficulty.HARD,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    response = client.get(
        "/api/v1/tasks",
        params={"language": "python", "difficulty": "easy"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_random_task_returns_400_for_unsupported_language(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/tasks",
        params={"language": "java", "difficulty": "easy"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported language"


def test_get_random_task_returns_400_for_unsupported_difficulty(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/tasks",
        params={"language": "python", "difficulty": "legendary"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported difficulty"


def test_get_task_by_id_returns_task(
    client: TestClient,
    db_session: Session,
) -> None:
    author = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=author,
        language=python_language,
        title="Task by id",
        difficulty=TaskDifficulty.MEDIUM,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    response = client.get(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == task.id
    assert body["title"] == "Task by id"
    assert body["description"] == "Task by id description"
    assert body["requirements"] == "Task by id requirements"
    assert body["legacyCode"] == "Task by id legacy code"
    assert body["difficulty"] == "medium"
    assert body["language"] == "python"


def test_get_task_by_id_returns_404_for_missing_task(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
