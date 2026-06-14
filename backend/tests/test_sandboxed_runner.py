from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.enums import (
    CheckStatus,
    SubmissionCheckType,
    SubmissionStatus,
    TaskDifficulty,
    TaskStatus,
)
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.submission import Submission
from backend.app.models.task import Task
from backend.app.models.task_check_spec import TaskCheckSpec
from backend.app.services.checking import CheckContext, CheckOrchestrator
from backend.app.services.checking.sandbox import (
    SandboxExecutionRequest,
    SandboxExecutionResult,
)
from backend.app.services.checking.sandboxed_runner import SandboxedCheckRunner
from backend.tests.sandbox_fakes import InProcessSandboxExecutor, sandbox_result
from backend.tests.test_submissions_api import (
    authenticate_client,
    create_language,
    create_static_check_spec,
    create_task,
    create_user,
)


def make_context() -> CheckContext:
    task = Task(
        id=1,
        title="Task",
        description="Task",
        requirements="Task",
        difficulty=TaskDifficulty.EASY,
        author_id=1,
        status=TaskStatus.PUBLISHED,
        max_score=100,
    )
    submission = Submission(
        id=10,
        task_id=1,
        user_id=1,
        language_id=1,
        source_code="def solve():\n    return 1\n",
    )
    language = ProgramLanguage(
        id=1,
        name="python",
        display_name="Python",
        version="3.12",
    )
    return CheckContext(
        task=task,
        submission=submission,
        program_language=language,
        source_code=submission.source_code,
    )


def make_spec(check_type: SubmissionCheckType) -> TaskCheckSpec:
    return TaskCheckSpec(
        id=20 + len(check_type.value),
        task_id=1,
        check_type=check_type,
        name=f"{check_type.value} check",
        weight=100,
        timeout_seconds=5,
        is_required=True,
        order=1,
        config_json={},
    )


def test_sandboxed_runner_uses_fake_executor_for_successful_check() -> None:
    executor = InProcessSandboxExecutor(
        [sandbox_result(status="passed", check_type="static")]
    )
    runner = SandboxedCheckRunner(SubmissionCheckType.STATIC, executor=executor)

    result = runner.run(context=make_context(), spec=make_spec(SubmissionCheckType.STATIC))

    assert result.status == CheckStatus.PASSED
    assert result.score == 100
    assert result.report.metrics["sandbox"] == "docker"
    assert result.report.metrics["container_image"] == "legacy-trainer-checker:test"
    assert result.report.artifacts["stdout"] == "fake stdout"
    assert len(executor.requests) == 1


def test_sandboxed_runner_uses_fake_executor_for_failed_check() -> None:
    executor = InProcessSandboxExecutor(
        [
            sandbox_result(
                status="failed",
                score=0,
                check_type="lint",
                summary="fake lint failed",
                exit_code=0,
            )
        ]
    )
    runner = SandboxedCheckRunner(SubmissionCheckType.LINT, executor=executor)

    result = runner.run(context=make_context(), spec=make_spec(SubmissionCheckType.LINT))

    assert result.status == CheckStatus.FAILED
    assert result.score == 0
    assert result.report.failed == 1
    assert result.report.summary == "fake lint failed"
    assert result.report.metrics["container_exit_code"] == 0


def test_sandboxed_runner_reports_fake_executor_timeout() -> None:
    executor = InProcessSandboxExecutor(
        [
            sandbox_result(
                status="error",
                score=0,
                check_type="tests",
                timed_out=True,
                exit_code=None,
            )
        ]
    )
    runner = SandboxedCheckRunner(SubmissionCheckType.TESTS, executor=executor)

    result = runner.run(context=make_context(), spec=make_spec(SubmissionCheckType.TESTS))

    assert result.status == CheckStatus.ERROR
    assert result.score == 0
    assert result.report.errors == 1
    assert result.report.metrics["timedOut"] is True
    assert result.report.details[0].details["error_type"] == "sandbox_timeout"


def test_sandboxed_runner_reports_missing_spec_config_error() -> None:
    runner = SandboxedCheckRunner(SubmissionCheckType.TESTS)

    result = runner.run(context=make_context(), spec=None)

    assert result.status == CheckStatus.ERROR
    assert result.score == 0
    assert result.report.summary == "tests checks require a task check spec"
    assert result.report.details[0].details["error_type"] == "config_error"


def test_sandboxed_runner_reports_non_json_output() -> None:
    executor = InProcessSandboxExecutor(
        [
            SandboxExecutionResult(
                image="legacy-trainer-checker:test",
                container_name="fake-container",
                exit_code=0,
                timed_out=False,
                duration_ms=5,
                stdout="not json",
                stderr="",
            )
        ]
    )
    runner = SandboxedCheckRunner(SubmissionCheckType.TESTS, executor=executor)

    result = runner.run(context=make_context(), spec=make_spec(SubmissionCheckType.TESTS))

    assert result.status == CheckStatus.ERROR
    assert result.score == 0
    assert result.report.summary == "Sandbox output could not be parsed as JSON"
    assert result.report.details[0].details["error_type"] == "invalid_sandbox_output"


def test_sandboxed_runner_reports_invalid_report() -> None:
    payload = {
        "check_type": "tests",
        "status": "passed",
        "score": 100,
        "execution_time_ms": 3,
        "memory_used_kb": 0,
        "report": {
            "total": -1,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "summary": "invalid",
        },
    }
    executor = InProcessSandboxExecutor(
        [
            SandboxExecutionResult(
                image="legacy-trainer-checker:test",
                container_name="fake-container",
                exit_code=0,
                timed_out=False,
                duration_ms=5,
                stdout=json.dumps(payload),
                stderr="",
            )
        ]
    )
    runner = SandboxedCheckRunner(SubmissionCheckType.TESTS, executor=executor)

    result = runner.run(context=make_context(), spec=make_spec(SubmissionCheckType.TESTS))

    assert result.status == CheckStatus.ERROR
    assert result.score == 0
    assert result.report.summary == "Sandbox result report failed validation"
    assert result.report.details[0].details["error_type"] == "invalid_sandbox_report"


def test_orchestrator_runs_each_check_in_separate_sandbox_execution(
    db_session: Session,
) -> None:
    user = create_user(db_session)
    python = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python,
        title="Separate sandbox task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    for order, check_type in enumerate(SubmissionCheckType, start=1):
        task.check_specs.append(
            TaskCheckSpec(
                check_type=check_type,
                name=f"{check_type.value} check",
                weight=25,
                timeout_seconds=5,
                is_required=True,
                order=order,
                config_json={},
            )
        )
    submission = Submission(
        task_id=task.id,
        user_id=user.id,
        language_id=python.id,
        source_code="class Solution:\n    pass\n",
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(task)
    db_session.refresh(submission)

    executor = RecordingPassingExecutor()
    orchestrator = CheckOrchestrator(
        {
            check_type: SandboxedCheckRunner(check_type, executor=executor)
            for check_type in SubmissionCheckType
        }
    )

    result = orchestrator.run(
        CheckContext(
            task=task,
            submission=submission,
            program_language=python,
            source_code=submission.source_code,
        )
    )

    assert result.status == SubmissionStatus.PASSED
    assert [request.check_type for request in executor.requests] == list(
        SubmissionCheckType
    )
    assert len({request.spec_id for request in executor.requests}) == 4


def test_submit_returns_check_error_when_sandbox_fails(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    user = create_user(db_session)
    python = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python,
        title="Sandbox failure task",
        difficulty=TaskDifficulty.EASY,
        status=TaskStatus.PUBLISHED,
    )
    create_static_check_spec(
        db_session,
        task,
        config_json={"required_symbols": ["Solution"]},
    )
    db_session.commit()
    authenticate_client(client, user)

    monkeypatch.setattr(
        "backend.app.services.checking.sandboxed_runner."
        "create_default_sandbox_executor",
        lambda: FailingSandboxExecutor(),
    )

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={"code": "class Solution:\n    pass\n", "language": "python"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "error"
    assert body["score"] == 0
    assert "Docker executable not found" in body["message"]

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    check = checks_response.json()[0]
    assert check["status"] == "error"
    assert check["report"]["metrics"]["sandbox"] == "docker"
    assert check["report"]["details"][0]["details"]["error_type"] == "sandbox_error"


class RecordingPassingExecutor:
    def __init__(self) -> None:
        self.requests: list[SandboxExecutionRequest] = []

    def execute(self, request: SandboxExecutionRequest):
        self.requests.append(request)
        return sandbox_result(
            status="passed",
            score=100,
            check_type=request.check_type.value,
            summary=f"{request.check_type.value} passed",
        )


class FailingSandboxExecutor:
    def execute(self, request: SandboxExecutionRequest):
        return sandbox_result(
            status="error",
            score=0,
            check_type=request.check_type.value,
            summary="Docker executable not found: docker",
            exit_code=None,
            error="Docker executable not found: docker",
        )
