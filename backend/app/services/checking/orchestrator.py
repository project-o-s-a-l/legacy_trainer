from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone

from backend.app.db.enums import CheckStatus, SubmissionCheckType, SubmissionStatus
from backend.app.models.task_check_spec import TaskCheckSpec
from backend.app.schemas.check import CheckReport, CheckReportDetail
from backend.app.services.checking.fake_runner import DeterministicFakeRunner
from backend.app.services.checking.python_lint_runner import PythonRuffLintRunner
from backend.app.services.checking.python_pytest_runner import PythonPytestRunner
from backend.app.services.checking.python_static_runner import (
    PythonArchitectureRunner,
    PythonStaticRunner,
)
from backend.app.services.checking.types import (
    CheckContext,
    CheckOrchestrationResult,
    CheckRunResult,
    CheckRunner,
)


class CheckOrchestrator:
    def __init__(
        self,
        runners: Mapping[SubmissionCheckType, CheckRunner],
        *,
        no_spec_tests_runner: CheckRunner | None = None,
    ) -> None:
        self.runners = dict(runners)
        self.no_spec_tests_runner = no_spec_tests_runner

    @classmethod
    def with_fake_runners(cls) -> "CheckOrchestrator":
        return cls(
            {
                check_type: DeterministicFakeRunner(check_type)
                for check_type in SubmissionCheckType
            },
            no_spec_tests_runner=DeterministicFakeRunner(SubmissionCheckType.TESTS),
        )

    @classmethod
    def with_default_runners(cls) -> "CheckOrchestrator":
        return cls(
            {
                SubmissionCheckType.TESTS: PythonPytestRunner(),
                SubmissionCheckType.LINT: PythonRuffLintRunner(),
                SubmissionCheckType.STATIC: PythonStaticRunner(),
                SubmissionCheckType.ARCHITECTURE: PythonArchitectureRunner(),
            },
            no_spec_tests_runner=DeterministicFakeRunner(SubmissionCheckType.TESTS),
        )

    def run(self, context: CheckContext) -> CheckOrchestrationResult:
        check_specs = self._get_ordered_specs(context)
        checks = [
            self._run_spec(context=context, spec=spec)
            for spec in check_specs
        ]

        if not checks:
            checks = [
                self._run_spec(context=context, spec=None),
            ]

        checked_at = datetime.now(timezone.utc)
        return CheckOrchestrationResult(
            checks=checks,
            status=self._aggregate_status(checks),
            score=self._aggregate_score(checks),
            checked_at=checked_at,
            message=self._response_message(checks),
            test_passed=self._test_passed(checks),
            execution_time_ms=self._aggregate_execution_time_ms(checks, context),
            memory_used_kb=self._aggregate_memory_used_kb(checks, context),
        )

    def _run_spec(
        self,
        *,
        context: CheckContext,
        spec: TaskCheckSpec | None,
    ) -> CheckRunResult:
        check_type = spec.check_type if spec else SubmissionCheckType.TESTS
        if spec is None and self.no_spec_tests_runner is not None:
            return self.no_spec_tests_runner.run(context=context, spec=spec)

        runner = self.runners.get(check_type)
        if runner is None:
            return self._missing_runner_result(spec)

        return runner.run(context=context, spec=spec)

    def _get_ordered_specs(self, context: CheckContext) -> list[TaskCheckSpec]:
        return sorted(
            context.task.check_specs,
            key=lambda spec: (spec.order, spec.id),
        )

    def _missing_runner_result(self, spec: TaskCheckSpec | None) -> CheckRunResult:
        check_type = spec.check_type if spec else SubmissionCheckType.TESTS
        name = spec.name if spec else "tests"
        report = CheckReport(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=f"No runner registered for {check_type.value}",
            details=[
                CheckReportDetail(
                    name=name,
                    status=CheckStatus.ERROR,
                    message=f"No runner registered for {check_type.value}",
                )
            ],
            metrics={"runner_missing": True},
        )

        return CheckRunResult(
            check_type=check_type,
            status=CheckStatus.ERROR,
            score=0,
            report=report,
            spec_id=spec.id if spec else None,
            name=name,
            weight=spec.weight if spec else 100,
            is_required=spec.is_required if spec else True,
        )

    def _aggregate_status(
        self,
        checks: Iterable[CheckRunResult],
    ) -> SubmissionStatus:
        required_checks = [check for check in checks if check.is_required]
        if any(check.status == CheckStatus.ERROR for check in required_checks):
            return SubmissionStatus.ERROR
        if any(check.status == CheckStatus.FAILED for check in required_checks):
            return SubmissionStatus.FAILED
        return SubmissionStatus.PASSED

    def _aggregate_score(self, checks: Iterable[CheckRunResult]) -> int:
        weighted_checks = [check for check in checks if check.weight > 0]
        if not weighted_checks:
            return 0

        total_weight = sum(check.weight for check in weighted_checks)
        weighted_score = sum(
            check.score * check.weight
            for check in weighted_checks
        )
        return int(weighted_score / total_weight)

    def _response_message(self, checks: Iterable[CheckRunResult]) -> str:
        checks = list(checks)
        tests_result = next(
            (
                check
                for check in checks
                if check.check_type == SubmissionCheckType.TESTS
            ),
            None,
        )
        if tests_result and tests_result.report.summary:
            return tests_result.report.summary

        if len(checks) == 1 and checks[0].status == CheckStatus.ERROR:
            return checks[0].report.summary or "Check could not be completed"

        if any(check.status == CheckStatus.ERROR for check in checks):
            return "Some checks could not be completed"
        if any(
            check.status == CheckStatus.FAILED and check.is_required
            for check in checks
        ):
            return "Some required checks failed"
        return "All checks passed"

    def _test_passed(self, checks: Iterable[CheckRunResult]) -> int:
        tests_result = next(
            (
                check
                for check in checks
                if check.check_type == SubmissionCheckType.TESTS
            ),
            None,
        )
        if tests_result is None:
            return 0
        return tests_result.report.passed

    def _aggregate_execution_time_ms(
        self,
        checks: Iterable[CheckRunResult],
        context: CheckContext,
    ) -> int:
        values = [
            check.execution_time_ms
            for check in checks
            if check.execution_time_ms is not None
        ]
        if values:
            return sum(values)
        return 10 + len(context.source_code.splitlines()) * 5

    def _aggregate_memory_used_kb(
        self,
        checks: Iterable[CheckRunResult],
        context: CheckContext,
    ) -> int:
        values = [
            check.memory_used_kb
            for check in checks
            if check.memory_used_kb is not None
        ]
        if values:
            return max(values)
        return 256 + len(context.source_code.splitlines()) * 64
