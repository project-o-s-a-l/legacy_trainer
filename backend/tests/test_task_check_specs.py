from sqlalchemy.orm import Session

from backend.app.db.enums import (
    CheckStatus,
    SubmissionCheckType,
    TaskDifficulty,
    TaskStatus,
    UserRole,
)
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.user import User
from backend.app.repositories.task import TaskRepository
from backend.app.schemas.check import (
    CheckReport,
    CheckReportDetail,
    InternalCheckResult,
    TaskCheckSpecContract,
)


def create_user(db_session: Session) -> User:
    user = User(
        username="spec-author",
        email="spec-author@example.com",
        login="spec-author",
        password_hash="hashed-password",
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def create_language(db_session: Session) -> ProgramLanguage:
    language = ProgramLanguage(
        name="python",
        display_name="Python",
        version="3.12",
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
) -> Task:
    task = Task(
        title="Task with specs",
        description="Task with specs description",
        requirements="Task with specs requirements",
        legacy_code="print('legacy')",
        difficulty=TaskDifficulty.EASY,
        author_id=author.id,
        status=TaskStatus.PUBLISHED,
        max_score=100,
        languages=[language],
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task


def test_task_repository_creates_and_reads_check_specs(
    db_session: Session,
) -> None:
    author = create_user(db_session)
    language = create_language(db_session)
    task = create_task(db_session, author=author, language=language)

    repository = TaskRepository(db_session)
    repository.create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.LINT,
        name="ruff",
        weight=20,
        timeout_seconds=5,
        is_required=False,
        order=2,
        config_json={"select": ["E", "F"]},
    )
    tests_spec = repository.create_check_spec(
        task_id=task.id,
        check_type=SubmissionCheckType.TESTS,
        name="pytest",
        weight=80,
        timeout_seconds=30,
        is_required=True,
        order=1,
        config_json={"test_path": "tests/test_solution.py"},
    )
    db_session.commit()

    check_specs = repository.list_check_specs_by_task_id(task.id)

    assert [spec.name for spec in check_specs] == ["pytest", "ruff"]
    assert check_specs[0].id == tests_spec.id
    assert check_specs[0].check_type == SubmissionCheckType.TESTS
    assert check_specs[0].weight == 80
    assert check_specs[0].timeout_seconds == 30
    assert check_specs[0].is_required is True
    assert check_specs[0].order == 1
    assert check_specs[0].config_json == {"test_path": "tests/test_solution.py"}

    loaded_task = repository.get_task_by_id(task.id)

    assert loaded_task is not None
    assert [spec.name for spec in loaded_task.check_specs] == ["pytest", "ruff"]


def test_task_check_spec_and_result_contracts_serialize_report_json() -> None:
    check_spec = TaskCheckSpecContract(
        task_id=1,
        check_type=SubmissionCheckType.STATIC,
        name="static-analysis",
        weight=30,
        timeout_seconds=10,
        is_required=True,
        order=3,
        config_json={"rules": ["no-global-state"]},
    )
    result = InternalCheckResult(
        spec_id=check_spec.id,
        name=check_spec.name,
        check_type=check_spec.check_type,
        status=CheckStatus.FAILED,
        score=50,
        weight=check_spec.weight,
        is_required=check_spec.is_required,
        report=CheckReport(
            total=2,
            passed=1,
            failed=1,
            summary="1 architecture rule failed",
            details=[
                CheckReportDetail(
                    name="no-global-state",
                    status=CheckStatus.FAILED,
                    message="Global mutable state detected",
                    path="solution.py",
                    line=12,
                    column=5,
                    details={"symbol": "CACHE"},
                )
            ],
            metrics={"duration_ms": 42},
        ),
    )

    report_json = result.to_report_json()

    assert check_spec.config_json == {"rules": ["no-global-state"]}
    assert report_json["total"] == 2
    assert report_json["passed"] == 1
    assert report_json["failed"] == 1
    assert report_json["errors"] == 0
    assert report_json["details"][0]["status"] == "failed"
    assert report_json["details"][0]["path"] == "solution.py"
    assert report_json["metrics"] == {"duration_ms": 42}
