import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.enums import (
    SubmissionCheckType,
    TaskDifficulty,
    TaskStatus,
    UserRole,
)
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.user import User
from backend.app.models.user_task_progress import UserTaskProgress
from backend.app.repositories.task import TaskRepository
from backend.app.services.security import hash_password
from backend.app.services.token import create_access_token
from backend.tests.sandbox_fakes import InProcessSandboxExecutor


@pytest.fixture(autouse=True)
def use_in_process_sandbox(monkeypatch) -> None:
    executor = InProcessSandboxExecutor()
    monkeypatch.setattr(
        "backend.app.services.checking.sandboxed_runner."
        "create_default_sandbox_executor",
        lambda: executor,
    )


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
    max_score: int = 100,
) -> Task:
    task = Task(
        title=title,
        description=f"{title} description",
        requirements=f"{title} requirements",
        legacy_code=f"{title} legacy code",
        difficulty=difficulty,
        author_id=author.id,
        status=status,
        max_score=max_score,
        languages=[language],
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task


def create_pytest_check_spec(
    db_session: Session,
    task: Task,
    *,
    test_code: str,
    timeout_seconds: int = 10,
    name: str = "pytest",
    weight: int = 100,
    order: int = 0,
) -> None:
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.TESTS,
        name=name,
        weight=weight,
        timeout_seconds=timeout_seconds,
        order=order,
        config_json={
            "entry_file": "solution.py",
            "test_file": "test_solution.py",
            "test_code": test_code,
            "visible": False,
        },
    )


def create_lint_check_spec(
    db_session: Session,
    task: Task,
    *,
    config_json: dict | None = None,
    name: str = "ruff",
    weight: int = 100,
    is_required: bool = True,
    order: int = 0,
) -> None:
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.LINT,
        name=name,
        weight=weight,
        is_required=is_required,
        order=order,
        config_json=config_json or {
            "entry_file": "solution.py",
            "select": ["F"],
        },
    )


def create_static_check_spec(
    db_session: Session,
    task: Task,
    *,
    config_json: dict,
    name: str = "static",
    weight: int = 100,
    order: int = 0,
) -> None:
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.STATIC,
        name=name,
        weight=weight,
        order=order,
        config_json=config_json,
    )


def create_architecture_check_spec(
    db_session: Session,
    task: Task,
    *,
    config_json: dict,
    name: str = "architecture",
    weight: int = 100,
    order: int = 0,
) -> None:
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.ARCHITECTURE,
        name=name,
        weight=weight,
        order=order,
        config_json=config_json,
    )


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


def create_check_spec(
    db_session: Session,
    task: Task,
    *,
    check_type: SubmissionCheckType,
    name: str,
    weight: int,
    order: int,
    is_required: bool = True,
    config_json: dict | None = None,
) -> None:
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=check_type,
        name=name,
        weight=weight,
        order=order,
        is_required=is_required,
        config_json=config_json or {},
    )


def submit_code(client: TestClient, task: Task, code: str) -> dict:
    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": code,
            "language": "python",
        },
    )

    assert response.status_code == 201
    return response.json()


def get_task_progress(
    db_session: Session,
    *,
    user: User,
    task: Task,
) -> UserTaskProgress:
    db_session.expire_all()
    progress = db_session.scalar(
        select(UserTaskProgress).where(
            UserTaskProgress.user_id == user.id,
            UserTaskProgress.task_id == task.id,
        )
    )
    assert progress is not None
    return progress


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


def test_submit_solution_runs_pytest_check_success(
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
        title="Pytest success task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        test_code=(
            "from solution import solve\n\n"
            "def test_double_positive():\n"
            "    assert solve(3) == 6\n\n"
            "def test_double_zero():\n"
            "    assert solve(0) == 0\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve(x):\n    return x * 2")

    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "All tests passed"
    assert body["testPassed"] == 2

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "tests"
    assert check["status"] == "passed"
    assert check["score"] == 100
    assert check["report"]["total"] == 2
    assert check["report"]["passed"] == 2
    assert check["report"]["failed"] == 0
    assert check["report"]["errors"] == 0
    assert check["report"]["metrics"]["runner"] == "python_pytest"
    assert check["report"]["artifacts"]["exit_code"] == 0


def test_submit_solution_runs_pytest_check_failure(
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
        title="Pytest failure task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        test_code=(
            "from solution import solve\n\n"
            "def test_expected_double():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve(x):\n    return x + 1")

    assert body["status"] == "failed"
    assert body["score"] == 0
    assert body["message"] == "0 of 1 tests passed"
    assert body["testPassed"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["status"] == "failed"
    assert check["report"]["total"] == 1
    assert check["report"]["passed"] == 0
    assert check["report"]["failed"] == 1
    assert check["report"]["errors"] == 0
    assert check["report"]["details"][0]["status"] == "failed"
    assert check["report"]["artifacts"]["exit_code"] == 1


def test_submit_solution_reports_pytest_timeout(
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
        title="Pytest timeout task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        timeout_seconds=1,
        test_code=(
            "from solution import solve\n\n"
            "def test_hangs():\n"
            "    solve()\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        "def solve():\n    while True:\n        pass",
    )

    assert body["status"] == "error"
    assert body["score"] == 0
    assert body["message"] == "Pytest timed out after 1 seconds"
    assert body["testPassed"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["status"] == "error"
    assert check["report"]["errors"] == 1
    assert check["report"]["details"][0]["details"]["timeout"] is True
    assert check["report"]["artifacts"]["exit_code"] is None


def test_submit_solution_reports_invalid_pytest_config(
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
        title="Invalid pytest config task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    TaskRepository(db_session).create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.TESTS,
        name="pytest invalid",
        config_json={
            "entry_file": "solution.py",
            "test_file": "test_solution.py",
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve(x):\n    return x")

    assert body["status"] == "error"
    assert body["score"] == 0
    assert body["message"] == "tests config_json.test_code must be a non-empty string"
    assert body["testPassed"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["status"] == "error"
    assert check["report"]["errors"] == 1
    assert check["report"]["details"][0]["details"]["error_type"] == "config_error"


def test_submit_solution_runs_lint_check_success(
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
        title="Lint success task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_lint_check_spec(db_session, task)
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve(x):\n    return x + 1\n")

    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "All checks passed"
    assert body["testPassed"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "lint"
    assert check["status"] == "passed"
    assert check["score"] == 100
    assert check["report"]["summary"] == "Lint passed"
    assert check["report"]["metrics"]["runner"] == "python_ruff_lint"
    assert check["report"]["artifacts"]["exit_code"] == 0


def test_submit_solution_runs_lint_check_failure(
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
        title="Lint failure task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_lint_check_spec(db_session, task)
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve():\n    return missing_name\n")

    assert body["status"] == "failed"
    assert body["score"] == 0
    assert body["message"] == "Some required checks failed"

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "lint"
    assert check["status"] == "failed"
    assert check["score"] == 0
    assert check["report"]["failed"] == 1
    assert check["report"]["details"][0]["name"] == "F821"
    assert check["report"]["details"][0]["line"] == 2
    assert check["report"]["artifacts"]["exit_code"] == 1


def test_submit_solution_runs_static_check_success(
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
        title="Static success task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_static_check_spec(
        db_session,
        task,
        config_json={
            "forbidden_imports": ["os"],
            "forbidden_calls": ["eval"],
            "required_symbols": ["Solution"],
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "class Solution:\n"
            "    def solve(self, value):\n"
            "        return value + 1\n"
        ),
    )

    assert body["status"] == "passed"
    assert body["score"] == 100

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "static"
    assert check["status"] == "passed"
    assert check["report"]["summary"] == "Static checks passed"
    assert check["report"]["metrics"]["runner"] == "python_static_ast"


def test_submit_solution_runs_static_check_failure(
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
        title="Static failure task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_static_check_spec(
        db_session,
        task,
        config_json={
            "forbidden_imports": ["os"],
            "forbidden_calls": ["eval"],
            "required_symbols": ["Solution"],
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "import os\n\n"
            "def solve(value):\n"
            "    return eval('value + 1')\n"
        ),
    )

    assert body["status"] == "failed"
    assert body["score"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "static"
    assert check["status"] == "failed"
    assert check["report"]["failed"] == 3
    assert {detail["name"] for detail in check["report"]["details"]} == {
        "forbidden_import",
        "forbidden_call",
        "required_symbol",
    }


def test_submit_solution_runs_architecture_check_success(
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
        title="Architecture success task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_architecture_check_spec(
        db_session,
        task,
        config_json={
            "required_classes": ["OrderService"],
            "required_methods": {"OrderService": ["calculate_total"]},
            "forbidden_functions": ["process_order"],
            "max_function_length": 4,
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "class OrderService:\n"
            "    def calculate_total(self, items):\n"
            "        return sum(items)\n"
        ),
    )

    assert body["status"] == "passed"
    assert body["score"] == 100

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "architecture"
    assert check["status"] == "passed"
    assert check["report"]["summary"] == "Architecture checks passed"
    assert check["report"]["metrics"]["runner"] == "python_architecture_ast"


def test_submit_solution_runs_architecture_check_failure(
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
        title="Architecture failure task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_architecture_check_spec(
        db_session,
        task,
        config_json={
            "required_classes": ["OrderService"],
            "required_methods": {"OrderService": ["calculate_total"]},
            "forbidden_functions": ["process_order"],
            "max_function_length": 3,
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "def process_order(order):\n"
            "    total = 0\n"
            "    for item in order:\n"
            "        total += item\n"
            "    return total\n\n"
            "class OrderService:\n"
            "    pass\n"
        ),
    )

    assert body["status"] == "failed"
    assert body["score"] == 0

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["checkType"] == "architecture"
    assert check["status"] == "failed"
    assert check["report"]["failed"] == 3
    assert {detail["name"] for detail in check["report"]["details"]} == {
        "forbidden_function",
        "max_function_length",
        "required_method",
    }


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


def test_submit_solution_runs_all_task_check_specs(
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
        title="Multi check task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        name="pytest",
        weight=40,
        order=1,
        test_code=(
            "from solution import solve\n\n"
            "def test_increment_two():\n"
            "    assert solve(2) == 3\n\n"
            "def test_increment_negative():\n"
            "    assert solve(-1) == 0\n\n"
            "def test_increment_zero():\n"
            "    assert solve(0) == 1\n"
        ),
    )
    create_lint_check_spec(
        db_session,
        task,
        name="ruff",
        weight=20,
        order=2,
        config_json={
            "entry_file": "solution.py",
            "select": ["F"],
        },
    )
    create_static_check_spec(
        db_session,
        task,
        name="static",
        weight=20,
        order=3,
        config_json={
            "forbidden_imports": ["subprocess"],
            "forbidden_calls": ["eval"],
            "required_symbols": ["solve", "OrderService"],
        },
    )
    create_architecture_check_spec(
        db_session,
        task,
        name="architecture",
        weight=20,
        order=4,
        config_json={
            "required_classes": ["OrderService"],
            "required_methods": {"OrderService": ["calculate_total"]},
            "forbidden_functions": ["process_order"],
            "max_function_length": 4,
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "class OrderService:\n"
            "    def calculate_total(self, items):\n"
            "        return sum(items)\n\n"
            "def solve(x):\n"
            "    service = OrderService()\n"
            "    return service.calculate_total([x, 1])\n"
        ),
    )

    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "All tests passed"
    assert body["testPassed"] == 3

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")

    assert checks_response.status_code == 200
    checks = checks_response.json()
    assert [check["checkType"] for check in checks] == [
        "tests",
        "lint",
        "static",
        "architecture",
    ]
    assert [check["status"] for check in checks] == [
        "passed",
        "passed",
        "passed",
        "passed",
    ]
    assert checks[0]["report"]["total"] == 3
    assert checks[0]["report"]["passed"] == 3
    assert checks[1]["report"]["metrics"]["runner"] == "python_ruff_lint"
    assert checks[2]["report"]["metrics"]["runner"] == "python_static_ast"
    assert checks[3]["report"]["metrics"]["runner"] == "python_architecture_ast"


def test_submit_solution_uses_weighted_score_with_optional_failed_check(
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
        title="Weighted optional spec task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        name="pytest",
        weight=75,
        order=1,
        test_code=(
            "from solution import solve\n\n"
            "def test_double():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    create_lint_check_spec(
        db_session,
        task,
        name="optional ruff",
        weight=25,
        order=2,
        is_required=False,
        config_json={
            "entry_file": "solution.py",
            "select": ["F"],
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(
        client,
        task,
        (
            "def solve(x):\n"
            "    return x * 2\n\n"
            "def unused_broken_function():\n"
            "    return missing_name\n"
        ),
    )

    assert body["status"] == "passed"
    assert body["score"] == 75
    assert body["message"] == "All tests passed"

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    checks = checks_response.json()
    assert [check["checkType"] for check in checks] == ["tests", "lint"]
    assert [check["status"] for check in checks] == ["passed", "failed"]
    assert [check["score"] for check in checks] == [100, 0]


def test_submit_solution_required_failed_check_sets_failed_status(
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
        title="Required failed spec task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        name="required tests",
        weight=100,
        order=1,
        test_code=(
            "from solution import solve\n\n"
            "def test_zero():\n"
            "    assert solve(0) == 0\n\n"
            "def test_one():\n"
            "    assert solve(1) == 2\n\n"
            "def test_two():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    body = submit_code(client, task, "def solve(x):\n    return 0\n")

    assert body["status"] == "failed"
    assert body["score"] == 33
    assert body["message"] == "1 of 3 tests passed"
    assert body["testPassed"] == 1


def test_submit_solution_updates_progress_attempts_best_and_solved(
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
        title="Progress lifecycle task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        test_code=(
            "from solution import solve\n\n"
            "def test_double_one():\n"
            "    assert solve(1) == 2\n\n"
            "def test_double_two():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    first = submit_code(client, task, "def solve(x):\n    return x + 1\n")
    progress = get_task_progress(db_session, user=user, task=task)
    assert progress.attempts_count == 1
    assert progress.best_submission_id == first["submissionId"]
    assert progress.is_solved is False
    assert progress.first_submission_at is not None
    assert progress.last_submission_at is not None
    db_session.refresh(user)
    assert user.total_score == 50

    second = submit_code(client, task, "def solve(x):\n    return 0\n")
    progress = get_task_progress(db_session, user=user, task=task)
    assert progress.attempts_count == 2
    assert progress.best_submission_id == first["submissionId"]
    assert progress.best_submission_id != second["submissionId"]
    assert progress.is_solved is False
    db_session.refresh(user)
    assert user.total_score == 50

    third = submit_code(client, task, "def solve(x):\n    return x * 2\n")
    progress = get_task_progress(db_session, user=user, task=task)
    assert progress.attempts_count == 3
    assert progress.best_submission_id == third["submissionId"]
    assert progress.is_solved is True
    db_session.refresh(user)
    assert user.total_score == 100


def test_submit_solution_prefers_passed_best_when_scores_tie(
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
        title="Best status tie task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        task,
        name="required tests",
        weight=50,
        order=1,
        test_code=(
            "from solution import solve\n\n"
            "def test_double():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    create_lint_check_spec(
        db_session,
        task,
        name="optional ruff",
        weight=50,
        order=2,
        is_required=False,
        config_json={
            "entry_file": "solution.py",
            "select": ["F"],
        },
    )
    db_session.commit()

    authenticate_client(client, user)

    failed_with_50 = submit_code(client, task, "def solve(x):\n    return x + 1\n")
    passed_with_50 = submit_code(
        client,
        task,
        (
            "def solve(x):\n"
            "    return x * 2\n\n"
            "def unused_broken_function():\n"
            "    return missing_name\n"
        ),
    )

    assert failed_with_50["status"] == "failed"
    assert failed_with_50["score"] == 50
    assert passed_with_50["status"] == "passed"
    assert passed_with_50["score"] == 50

    progress = get_task_progress(db_session, user=user, task=task)
    assert progress.best_submission_id == passed_with_50["submissionId"]
    assert progress.attempts_count == 2
    assert progress.is_solved is False
    db_session.refresh(user)
    assert user.total_score == 50


def test_submit_solution_recalculates_total_score_from_best_submissions(
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
    first_task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Total score partial task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    second_task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Total score solved task",
        difficulty=TaskDifficulty.MEDIUM,
        status=TaskStatus.PUBLISHED,
    )
    create_pytest_check_spec(
        db_session,
        first_task,
        test_code=(
            "from solution import solve\n\n"
            "def test_double_one():\n"
            "    assert solve(1) == 2\n\n"
            "def test_double_two():\n"
            "    assert solve(2) == 4\n"
        ),
    )
    db_session.commit()

    authenticate_client(client, user)

    submit_code(client, first_task, "def solve(x):\n    return x + 1\n")
    submit_code(
        client,
        second_task,
        (
            "def solve(x):\n"
            "    return x\n\n"
            "print(solve(1))\n"
        ),
    )
    db_session.refresh(user)
    assert user.total_score == 150

    submit_code(client, first_task, "def solve(x):\n    return x * 2\n")
    db_session.refresh(user)
    assert user.total_score == 200


def test_list_submissions_returns_only_current_user_history(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    other_user = create_user(
        db_session,
        username="other-history",
        email="other-history@example.com",
        login="other-history",
    )
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
        title="History task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    other_task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Other history task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)
    first = submit_code(client, task, "print('first')\nprint('done')\nprint('ok')\n")
    second = submit_code(client, task, "print('second')\nprint('done')\nprint('ok')\n")
    other_task_submission = submit_code(
        client,
        other_task,
        "print('other task')\nprint('done')\nprint('ok')\n",
    )

    authenticate_client(client, other_user)
    other_user_submission = submit_code(
        client,
        task,
        "print('other user')\nprint('done')\nprint('ok')\n",
    )

    authenticate_client(client, user)
    response = client.get(f"/api/v1/submissions?taskId={task.id}")

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == [
        second["submissionId"],
        first["submissionId"],
    ]
    assert other_task_submission["submissionId"] not in [
        item["id"]
        for item in body
    ]
    assert other_user_submission["submissionId"] not in [
        item["id"]
        for item in body
    ]
    assert {item["taskId"] for item in body} == {task.id}
    assert {item["userId"] for item in body} == {user.id}


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


def test_failed_submission_awards_partial_points_but_does_not_solve_task(
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
        title="Failed score task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "pass",
            "language": "python",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"
    assert body["score"] == 33

    db_session.expire_all()

    refreshed_user = db_session.scalar(select(User).where(User.id == user.id))
    progress = db_session.scalar(
        select(UserTaskProgress).where(
            UserTaskProgress.user_id == user.id,
            UserTaskProgress.task_id == task.id,
        )
    )

    assert refreshed_user is not None
    assert refreshed_user.total_score == 33
    assert progress is not None
    assert progress.best_submission_id == body["submissionId"]
    assert progress.is_solved is False
    assert progress.attempts_count == 1


def test_passed_submission_awards_points_and_persists_after_later_failure(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="winner",
        email="winner@example.com",
        login="winner",
    )
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
        title="Solved score task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    db_session.commit()

    authenticate_client(client, user)

    passed_response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "def solve(x):\n    return x + 1\nprint(solve(2))",
            "language": "python",
        },
    )

    assert passed_response.status_code == 201
    assert passed_response.json()["status"] == "passed"
    assert passed_response.json()["score"] == 100

    failed_response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": "pass",
            "language": "python",
        },
    )

    assert failed_response.status_code == 201
    assert failed_response.json()["status"] == "failed"

    db_session.expire_all()

    refreshed_user = db_session.scalar(select(User).where(User.id == user.id))
    progress = db_session.scalar(
        select(UserTaskProgress).where(
            UserTaskProgress.user_id == user.id,
            UserTaskProgress.task_id == task.id,
        )
    )

    assert refreshed_user is not None
    assert refreshed_user.total_score == 100
    assert progress is not None
    assert progress.is_solved is True
    assert progress.attempts_count == 2
