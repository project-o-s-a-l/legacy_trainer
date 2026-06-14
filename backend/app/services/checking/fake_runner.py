from __future__ import annotations

from typing import Any

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.models.task_check_spec import TaskCheckSpec
from backend.app.schemas.check import CheckReport, CheckReportDetail
from backend.app.services.checking.types import CheckContext, CheckRunResult


class DeterministicFakeRunner:
    def __init__(self, check_type: SubmissionCheckType) -> None:
        self.check_type = check_type

    def run(
        self,
        *,
        context: CheckContext,
        spec: TaskCheckSpec | None,
    ) -> CheckRunResult:
        if self.check_type == SubmissionCheckType.TESTS:
            return self._run_fake_tests(context=context, spec=spec)

        if spec is None:
            raise ValueError("Non-tests fake checks require a task check spec")

        return self._run_placeholder(spec=spec)

    def _run_fake_tests(
        self,
        *,
        context: CheckContext,
        spec: TaskCheckSpec | None,
    ) -> CheckRunResult:
        total_tests = self._get_total_tests(spec)
        lines = [line for line in context.source_code.splitlines() if line.strip()]
        passed_tests = min(total_tests, len(lines))

        failed_markers = (
            "TODO",
            "pass",
            "stub",
            "raise NotImplementedError",
            "throw new Error",
        )
        if any(marker in context.source_code for marker in failed_markers):
            passed_tests = min(passed_tests, 1)

        failed_tests = total_tests - passed_tests
        score = int((passed_tests / total_tests) * 100)
        status = CheckStatus.PASSED if failed_tests == 0 else CheckStatus.FAILED
        status = self._configured_status(spec) or status
        score = self._configured_score(spec, score)

        if status == CheckStatus.ERROR:
            passed_tests = 0
            failed_tests = 0
            errors = 1
        else:
            errors = 0

        summary = self._configured_summary(spec)
        if summary is None:
            summary = (
                "All tests passed"
                if status == CheckStatus.PASSED
                else f"{passed_tests} of {total_tests} tests passed"
            )

        report = CheckReport(
            total=total_tests,
            passed=passed_tests,
            failed=failed_tests,
            errors=errors,
            summary=summary,
            details=[
                CheckReportDetail(
                    name=f"test_{index + 1}",
                    status=(
                        CheckStatus.PASSED
                        if index < passed_tests
                        else CheckStatus.FAILED
                    ),
                    details={"runner": "deterministic_fake"},
                )
                for index in range(total_tests)
            ],
            metrics={
                "runner": "deterministic_fake",
                "source": "legacy_heuristic",
            },
        )

        return CheckRunResult(
            check_type=SubmissionCheckType.TESTS,
            status=status,
            score=score,
            report=report,
            spec_id=spec.id if spec else None,
            name=spec.name if spec else "fake-tests",
            weight=spec.weight if spec else 100,
            is_required=spec.is_required if spec else True,
            execution_time_ms=10 + len(context.source_code.splitlines()) * 5,
            memory_used_kb=256 + len(context.source_code.splitlines()) * 64,
        )

    def _run_placeholder(self, *, spec: TaskCheckSpec) -> CheckRunResult:
        status = self._configured_status(spec) or CheckStatus.PASSED
        default_score = 100 if status == CheckStatus.PASSED else 0
        score = self._configured_score(spec, default_score)
        failed = 1 if status == CheckStatus.FAILED else 0
        errors = 1 if status == CheckStatus.ERROR else 0
        passed = 1 if status == CheckStatus.PASSED else 0
        summary = self._configured_summary(spec)
        if summary is None:
            summary = f"{spec.name} skipped by deterministic fake runner"

        report = CheckReport(
            total=1,
            passed=passed,
            failed=failed,
            errors=errors,
            summary=summary,
            details=[
                CheckReportDetail(
                    name=spec.name,
                    status=status,
                    message=(
                        "Skipped until a real runner is implemented for this "
                        "check type."
                    ),
                    details={
                        "runner": "deterministic_fake",
                        "skipped": True,
                    },
                )
            ],
            metrics={
                "runner": "deterministic_fake",
                "skipped": True,
            },
        )

        return CheckRunResult(
            check_type=spec.check_type,
            status=status,
            score=score,
            report=report,
            spec_id=spec.id,
            name=spec.name,
            weight=spec.weight,
            is_required=spec.is_required,
            execution_time_ms=0,
            memory_used_kb=0,
        )

    def _get_total_tests(self, spec: TaskCheckSpec | None) -> int:
        if spec is None:
            return 3

        configured_total = spec.config_json.get("total_tests")
        if isinstance(configured_total, int) and configured_total > 0:
            return configured_total

        return 3

    def _configured_status(self, spec: TaskCheckSpec | None) -> CheckStatus | None:
        value = self._config_value(spec, "fake_status")
        if value is None:
            return None
        try:
            return CheckStatus(str(value).strip().lower())
        except ValueError:
            return None

    def _configured_score(self, spec: TaskCheckSpec | None, default: int) -> int:
        value = self._config_value(spec, "fake_score")
        if not isinstance(value, int):
            return default
        return max(0, min(100, value))

    def _configured_summary(self, spec: TaskCheckSpec | None) -> str | None:
        value = self._config_value(spec, "fake_summary")
        if isinstance(value, str) and value.strip():
            return value
        return None

    def _config_value(self, spec: TaskCheckSpec | None, key: str) -> Any:
        if spec is None:
            return None
        return spec.config_json.get(key)
