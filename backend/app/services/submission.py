from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.enums import CheckStatus
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.submission import Submission
from backend.app.models.submission_check import SubmissionCheck
from backend.app.models.task import Task
from backend.app.models.user import User
from backend.app.repositories.submission import SubmissionRepository
from backend.app.repositories.task import TaskRepository
from backend.app.schemas.check import CheckReport, CheckReportDetail
from backend.app.services.checking import (
    CheckContext,
    CheckOrchestrationResult,
    CheckOrchestrator,
    CheckRunResult,
)
from backend.app.services.refactor_checks.models import CheckOutcome, PipelineResult
from backend.app.services.refactor_checks.pipeline import RefactorCheckPipeline
from backend.app.services.user_progress import UserProgressService
from backend.app.schemas.submission import (
    SubmissionCheckResponse,
    SubmissionCreateRequest,
    SubmissionCreateResponse,
    SubmissionResponse,
)


class SubmissionService:
    _LANGUAGE_ALIASES = {
        "python": ("python", "Python"),
        "cpp": ("cpp", "C++"),
        "c++": ("cpp", "C++"),
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.tasks = TaskRepository(db)
        self.submissions = SubmissionRepository(db)
        self.progress = UserProgressService(db)
        self.refactor_pipeline = RefactorCheckPipeline(db)
        self.check_orchestrator = CheckOrchestrator.with_default_runners()

    def submit(
        self,
        *,
        task_id: int,
        data: SubmissionCreateRequest,
        current_user: User,
    ) -> SubmissionCreateResponse:
        task = self.tasks.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        code = data.code.strip()
        if not code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Code must not be empty",
            )

        language_name, language_display_name = self._normalize_language(data.language)

        program_language = self.submissions.get_language_by_name_or_display_name(
            name=language_name,
            display_name=language_display_name,
        )
        if program_language is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported language",
            )

        task_language_ids = {language.id for language in task.languages}
        if program_language.id not in task_language_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language is not available for this task",
            )

        submission = self.submissions.create_submission(
            task_id=task.id,
            user_id=current_user.id,
            language_id=program_language.id,
            source_code=code,
        )

        orchestration = self._run_checks(
            task=task,
            submission=submission,
            program_language=program_language,
            source_code=code,
        )

        submission.status = orchestration.status
        submission.score = orchestration.score
        submission.checked_at = orchestration.checked_at
        submission.memory_used_kb = orchestration.memory_used_kb
        submission.execution_time_ms = orchestration.execution_time_ms

        for check in orchestration.checks:
            self.submissions.create_submission_check(
                submission_id=submission.id,
                check_type=check.check_type,
                status=check.status,
                score=check.score,
                report_json=check.to_report_json(),
            )

        self.progress.record_submission(
            user_id=current_user.id,
            task=task,
            submission=submission,
        )

        self.db.commit()
        self.db.refresh(submission)

        return SubmissionCreateResponse(
            submissionId=submission.id,
            taskId=submission.task_id,
            status=submission.status.value,
            score=submission.score or 0,
            message=orchestration.message,
            testPassed=orchestration.test_passed,
        )

    def get_submission(
        self,
        *,
        submission_id: int,
        current_user: User,
    ) -> SubmissionResponse:
        submission = self._get_owned_submission(
            submission_id=submission_id,
            current_user=current_user,
        )

        return self._map_submission(submission)

    def list_submissions(
        self,
        *,
        current_user: User,
        task_id: int | None = None,
    ) -> list[SubmissionResponse]:
        submissions = self.submissions.list_user_submissions(
            user_id=current_user.id,
            task_id=task_id,
        )
        return [self._map_submission(submission) for submission in submissions]

    def get_submission_checks(
        self,
        *,
        submission_id: int,
        current_user: User,
    ) -> list[SubmissionCheckResponse]:
        submission = self._get_owned_submission(
            submission_id=submission_id,
            current_user=current_user,
        )

        checks = sorted(submission.checks, key=lambda item: item.id)
        return [self._map_check(check) for check in checks]

    def _get_owned_submission(
        self,
        *,
        submission_id: int,
        current_user: User,
    ) -> Submission:
        submission = self.submissions.get_submission_by_id(submission_id)
        if submission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )

        if submission.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return submission

    def _normalize_language(self, language: str) -> tuple[str, str]:
        normalized = language.strip().lower()
        result = self._LANGUAGE_ALIASES.get(normalized)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported language",
            )
        return result

    def _run_checks(
        self,
        *,
        task: Task,
        submission: Submission,
        program_language: ProgramLanguage,
        source_code: str,
    ) -> CheckOrchestrationResult:
        context = CheckContext(
            task=task,
            submission=submission,
            program_language=program_language,
            source_code=source_code,
        )

        if task.check_specs:
            return self.check_orchestrator.run(context)

        pipeline_result = self.refactor_pipeline.evaluate(
            task=task,
            language_name=program_language.name,
            candidate_code=source_code,
        )
        if pipeline_result is not None:
            return self._orchestration_from_refactor_pipeline(
                pipeline_result=pipeline_result,
                source_code=source_code,
            )

        return self.check_orchestrator.run(context)

    def _orchestration_from_refactor_pipeline(
        self,
        *,
        pipeline_result: PipelineResult,
        source_code: str,
    ) -> CheckOrchestrationResult:
        checks = [
            self._check_result_from_refactor_outcome(check)
            for check in pipeline_result.checks
        ]
        return CheckOrchestrationResult(
            checks=checks,
            status=pipeline_result.status,
            score=pipeline_result.score,
            checked_at=datetime.now(timezone.utc),
            message=pipeline_result.message,
            test_passed=pipeline_result.test_passed,
            execution_time_ms=(
                pipeline_result.execution_time_ms
                if pipeline_result.execution_time_ms is not None
                else 10 + len(source_code.splitlines()) * 5
            ),
            memory_used_kb=(
                pipeline_result.memory_used_kb
                if pipeline_result.memory_used_kb is not None
                else 256 + len(source_code.splitlines()) * 64
            ),
        )

    def _check_result_from_refactor_outcome(
        self,
        check: CheckOutcome,
    ) -> CheckRunResult:
        return CheckRunResult(
            check_type=check.check_type,
            status=check.status,
            score=check.score,
            report=self._normalize_refactor_report(check),
            name=check.check_type.value,
            weight=check.max_score,
            is_required=True,
        )

    def _normalize_refactor_report(self, check: CheckOutcome) -> CheckReport:
        raw = check.report or {}
        passed = self._report_int(raw, "passed")
        failed = self._report_int(raw, "failed")
        errors = self._report_int(raw, "errors")
        total = self._report_int(raw, "total")

        if total == 0:
            total = passed + failed + errors
        if total == 0 and check.status != CheckStatus.PASSED:
            total = 1
            failed = 1 if check.status == CheckStatus.FAILED else failed
            errors = 1 if check.status == CheckStatus.ERROR else errors
        if total == 0 and check.status == CheckStatus.PASSED:
            total = 1
            passed = 1

        summary = self._report_summary(raw, check)
        details = self._refactor_report_details(raw, check)
        metrics: dict[str, Any] = {
            "runner": "refactor_pipeline",
            "max_score": check.max_score,
        }
        duration_ms = raw.get("durationMs")
        if isinstance(duration_ms, int):
            metrics["duration_ms"] = duration_ms

        return CheckReport(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            summary=summary,
            details=details,
            metrics=metrics,
            artifacts={"legacy_report": raw},
        )

    def _refactor_report_details(
        self,
        raw: dict[str, Any],
        check: CheckOutcome,
    ) -> list[CheckReportDetail]:
        raw_details = raw.get("details")
        if isinstance(raw_details, list):
            return [
                self._refactor_report_detail(item, index, check.status)
                for index, item in enumerate(raw_details)
            ]

        issues = raw.get("issues")
        if isinstance(issues, list):
            return [
                CheckReportDetail(
                    name=f"issue_{index + 1}",
                    status=check.status,
                    message=str(issue),
                )
                for index, issue in enumerate(issues)
            ]

        message = raw.get("message")
        if isinstance(message, str) and message:
            return [
                CheckReportDetail(
                    name=check.check_type.value,
                    status=check.status,
                    message=message,
                )
            ]

        return []

    def _refactor_report_detail(
        self,
        item: Any,
        index: int,
        fallback_status: CheckStatus,
    ) -> CheckReportDetail:
        if not isinstance(item, dict):
            return CheckReportDetail(
                name=f"detail_{index + 1}",
                status=fallback_status,
                message=str(item),
            )

        name = item.get("name") or item.get("scenarioId") or f"detail_{index + 1}"
        message = item.get("message")
        detail_status = self._coerce_check_status(item.get("status"), fallback_status)
        line = item.get("line")
        column = item.get("column")
        passthrough = {
            key: value
            for key, value in item.items()
            if key not in {"name", "status", "message", "path", "line", "column"}
        }

        return CheckReportDetail(
            name=str(name),
            status=detail_status,
            message=str(message) if message is not None else None,
            path=str(item["path"]) if item.get("path") is not None else None,
            line=line if isinstance(line, int) and line > 0 else None,
            column=column if isinstance(column, int) and column > 0 else None,
            details=passthrough,
        )

    def _report_int(self, raw: dict[str, Any], key: str) -> int:
        value = raw.get(key)
        if isinstance(value, int) and value >= 0:
            return value
        return 0

    def _report_summary(self, raw: dict[str, Any], check: CheckOutcome) -> str:
        summary = raw.get("summary") or raw.get("message")
        if isinstance(summary, str) and summary:
            return summary
        if check.status == CheckStatus.PASSED:
            return f"{check.check_type.value} check passed"
        if check.status == CheckStatus.ERROR:
            return f"{check.check_type.value} check could not be completed"
        return f"{check.check_type.value} check failed"

    def _coerce_check_status(
        self,
        value: Any,
        fallback: CheckStatus,
    ) -> CheckStatus:
        if isinstance(value, CheckStatus):
            return value
        try:
            return CheckStatus(str(value).strip().lower())
        except ValueError:
            return fallback

    def _map_submission(self, submission: Submission) -> SubmissionResponse:
        return SubmissionResponse(
            id=submission.id,
            taskId=submission.task_id,
            userId=submission.user_id,
            language=submission.program_language.name,
            status=submission.status.value,
            score=submission.score,
            submittedAt=submission.submitted_at,
            checkedAt=submission.checked_at,
            memoryUsedKb=submission.memory_used_kb,
            executionTimeMs=submission.execution_time_ms,
        )

    def _map_check(self, check: SubmissionCheck) -> SubmissionCheckResponse:
        return SubmissionCheckResponse(
            id=check.id,
            checkType=check.check_type.value,
            status=check.status.value,
            score=check.score,
            report=check.report_json,
            createdAt=check.created_at,
        )
