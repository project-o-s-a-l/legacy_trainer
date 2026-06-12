from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from backend.app.db.enums import CheckStatus, SubmissionCheckType, SubmissionStatus
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.submission import Submission
from backend.app.models.task import Task
from backend.app.models.task_check_spec import TaskCheckSpec
from backend.app.schemas.check import CheckReport


@dataclass(frozen=True)
class CheckContext:
    task: Task
    submission: Submission
    program_language: ProgramLanguage
    source_code: str


@dataclass(frozen=True)
class CheckRunResult:
    check_type: SubmissionCheckType
    status: CheckStatus
    score: int
    report: CheckReport
    spec_id: int | None = None
    name: str | None = None
    weight: int = 100
    is_required: bool = True
    execution_time_ms: int | None = None
    memory_used_kb: int | None = None

    def to_report_json(self) -> dict[str, Any]:
        return self.report.model_dump(mode="json")


class CheckRunner(Protocol):
    check_type: SubmissionCheckType

    def run(
        self,
        *,
        context: CheckContext,
        spec: TaskCheckSpec | None,
    ) -> CheckRunResult:
        ...


@dataclass(frozen=True)
class CheckOrchestrationResult:
    checks: list[CheckRunResult]
    status: SubmissionStatus
    score: int
    checked_at: datetime
    message: str
    test_passed: int
    execution_time_ms: int
    memory_used_kb: int
