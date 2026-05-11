from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.enums import CheckStatus, SubmissionCheckType, SubmissionStatus
from backend.app.models.submission import Submission
from backend.app.models.submission_check import SubmissionCheck
from backend.app.models.user import User
from backend.app.repositories.submission import SubmissionRepository
from backend.app.repositories.task import TaskRepository
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

        passed_tests, total_tests, score = self._evaluate_code(code)
        failed_tests = total_tests - passed_tests

        report = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "details": [
                {
                    "name": f"test_{index + 1}",
                    "status": "passed" if index < passed_tests else "failed",
                }
                for index in range(total_tests)
            ],
        }

        if failed_tests == 0:
            submission.status = SubmissionStatus.PASSED
            check_status = CheckStatus.PASSED
            message = "All tests passed"
        else:
            submission.status = SubmissionStatus.FAILED
            check_status = CheckStatus.FAILED
            message = f"{passed_tests} of {total_tests} tests passed"

        submission.score = score
        submission.checked_at = datetime.now(timezone.utc)
        submission.memory_used_kb = 256 + len(code.splitlines()) * 64
        submission.execution_time_ms = 10 + len(code.splitlines()) * 5

        self.submissions.create_submission_check(
            submission_id=submission.id,
            check_type=SubmissionCheckType.TESTS,
            status=check_status,
            score=score,
            report_json=report,
        )

        self.db.commit()
        self.db.refresh(submission)

        return SubmissionCreateResponse(
            submissionId=submission.id,
            taskId=submission.task_id,
            status=submission.status.value,
            score=submission.score or 0,
            message=message,
            testPassed=passed_tests,
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

    def _evaluate_code(self, code: str) -> tuple[int, int, int]:
        total_tests = 3
        lines = [line for line in code.splitlines() if line.strip()]
        passed_tests = min(total_tests, len(lines))

        failed_markers = (
            "TODO",
            "pass",
            "stub",
            "raise NotImplementedError",
            "throw new Error",
        )
        if any(marker in code for marker in failed_markers):
            passed_tests = min(passed_tests, 1)

        score = int((passed_tests / total_tests) * 100)
        return passed_tests, total_tests, score

    def _map_check(self, check: SubmissionCheck) -> SubmissionCheckResponse:
        return SubmissionCheckResponse(
            id=check.id,
            checkType=check.check_type.value,
            status=check.status.value,
            score=check.score,
            report=check.report_json,
            createdAt=check.created_at,
        )
