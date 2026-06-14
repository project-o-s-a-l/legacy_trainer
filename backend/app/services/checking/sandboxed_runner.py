from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.models.task_check_spec import TaskCheckSpec
from backend.app.schemas.check import CheckReport, CheckReportDetail
from backend.app.services.checking.sandbox import (
    DockerSandboxExecutor,
    SandboxExecutionRequest,
    SandboxExecutionResult,
    SandboxExecutor,
)
from backend.app.services.checking.types import CheckContext, CheckRunResult


OUTPUT_LIMIT = 8_000


def create_default_sandbox_executor() -> SandboxExecutor:
    return DockerSandboxExecutor()


class SandboxedCheckRunner:
    def __init__(
        self,
        check_type: SubmissionCheckType,
        *,
        executor: SandboxExecutor | None = None,
    ) -> None:
        self.check_type = check_type
        self.executor = executor

    def run(
        self,
        *,
        context: CheckContext,
        spec: TaskCheckSpec | None,
    ) -> CheckRunResult:
        if spec is None:
            return self._error_result(
                spec=spec,
                message=f"{self.check_type.value} checks require a task check spec",
                duration_ms=0,
                error_type="config_error",
                sandbox=None,
            )

        executor = self.executor or create_default_sandbox_executor()
        request = SandboxExecutionRequest(
            check_type=self.check_type,
            check_name=spec.name,
            submission_id=context.submission.id,
            spec_id=spec.id,
            timeout_seconds=self._timeout_seconds(spec),
            payload={
                "check_type": self.check_type.value,
                "check_name": spec.name,
                "timeout_seconds": self._timeout_seconds(spec),
                "program_language": context.program_language.name,
                "source_code": context.source_code,
                "config": spec.config_json,
            },
        )
        sandbox = executor.execute(request)
        return self._from_sandbox_result(spec=spec, sandbox=sandbox)

    def _from_sandbox_result(
        self,
        *,
        spec: TaskCheckSpec,
        sandbox: SandboxExecutionResult,
    ) -> CheckRunResult:
        if sandbox.error:
            return self._error_result(
                spec=spec,
                message=sandbox.error,
                duration_ms=sandbox.duration_ms,
                error_type="sandbox_error",
                sandbox=sandbox,
            )

        if sandbox.timed_out:
            return self._error_result(
                spec=spec,
                message=f"Sandbox timed out after {sandbox.duration_ms} ms",
                duration_ms=sandbox.duration_ms,
                error_type="sandbox_timeout",
                sandbox=sandbox,
            )

        if sandbox.exit_code != 0:
            return self._error_result(
                spec=spec,
                message=f"Sandbox container exited with code {sandbox.exit_code}",
                duration_ms=sandbox.duration_ms,
                error_type="sandbox_exit_code",
                sandbox=sandbox,
            )

        try:
            parsed = json.loads(sandbox.stdout)
        except json.JSONDecodeError:
            return self._error_result(
                spec=spec,
                message="Sandbox output could not be parsed as JSON",
                duration_ms=sandbox.duration_ms,
                error_type="invalid_sandbox_output",
                sandbox=sandbox,
            )

        if not isinstance(parsed, dict):
            return self._error_result(
                spec=spec,
                message="Sandbox output JSON must be an object",
                duration_ms=sandbox.duration_ms,
                error_type="invalid_sandbox_output",
                sandbox=sandbox,
            )

        try:
            status = CheckStatus(str(parsed.get("status", "error")))
        except ValueError:
            status = CheckStatus.ERROR

        score = self._bounded_score(parsed.get("score"))
        report, report_valid = self._validated_report(
            parsed.get("report"),
            spec,
            sandbox,
        )
        report = self._with_sandbox_metadata(
            report=report,
            spec=spec,
            sandbox=sandbox,
            parsed_timed_out=bool(parsed.get("timedOut", False)),
        )
        if not report_valid:
            return CheckRunResult(
                check_type=self.check_type,
                status=CheckStatus.ERROR,
                score=0,
                report=report,
                spec_id=spec.id,
                name=spec.name,
                weight=spec.weight,
                is_required=spec.is_required,
                execution_time_ms=sandbox.duration_ms,
                memory_used_kb=0,
            )

        execution_time_ms = self._non_negative_int(
            parsed.get("execution_time_ms"),
            fallback=sandbox.duration_ms,
        )
        memory_used_kb = self._non_negative_int(
            parsed.get("memory_used_kb"),
            fallback=0,
        )

        return CheckRunResult(
            check_type=self.check_type,
            status=status,
            score=score,
            report=report,
            spec_id=spec.id,
            name=spec.name,
            weight=spec.weight,
            is_required=spec.is_required,
            execution_time_ms=execution_time_ms,
            memory_used_kb=memory_used_kb,
        )

    def _validated_report(
        self,
        value: object,
        spec: TaskCheckSpec,
        sandbox: SandboxExecutionResult,
    ) -> tuple[CheckReport, bool]:
        if not isinstance(value, dict):
            return (
                self._error_report(
                    spec=spec,
                    message="Sandbox result report must be an object",
                    duration_ms=sandbox.duration_ms,
                    error_type="invalid_sandbox_report",
                    sandbox=sandbox,
                ),
                False,
            )
        try:
            return CheckReport.model_validate(value), True
        except ValidationError:
            return (
                self._error_report(
                    spec=spec,
                    message="Sandbox result report failed validation",
                    duration_ms=sandbox.duration_ms,
                    error_type="invalid_sandbox_report",
                    sandbox=sandbox,
                ),
                False,
            )

    def _with_sandbox_metadata(
        self,
        *,
        report: CheckReport,
        spec: TaskCheckSpec,
        sandbox: SandboxExecutionResult,
        parsed_timed_out: bool,
    ) -> CheckReport:
        report_json = report.model_dump(mode="python")
        metrics = dict(report_json.get("metrics") or {})
        artifacts = dict(report_json.get("artifacts") or {})
        timed_out = sandbox.timed_out or parsed_timed_out

        metrics.update(
            {
                "check_type": self.check_type.value,
                "check_name": spec.name,
                "sandbox": "docker",
                "container_image": sandbox.image,
                "container_name": sandbox.container_name,
                "container_exit_code": sandbox.exit_code,
                "container_timed_out": sandbox.timed_out,
                "container_duration_ms": sandbox.duration_ms,
                "containerDurationMs": sandbox.duration_ms,
                "timedOut": timed_out,
            }
        )

        artifacts.setdefault("stdout", "")
        artifacts.setdefault("stderr", sandbox.stderr)
        artifacts.setdefault("exit_code", sandbox.exit_code)
        artifacts.setdefault("duration_ms", sandbox.duration_ms)
        artifacts.setdefault("durationMs", sandbox.duration_ms)
        artifacts["timedOut"] = timed_out
        artifacts["container_image"] = sandbox.image
        artifacts["container_exit_code"] = sandbox.exit_code
        artifacts["container_timed_out"] = sandbox.timed_out
        artifacts["container_duration_ms"] = sandbox.duration_ms
        artifacts["containerDurationMs"] = sandbox.duration_ms
        if sandbox.stderr:
            artifacts["container_stderr"] = self._truncate(sandbox.stderr)[0]

        report_json["metrics"] = metrics
        report_json["artifacts"] = artifacts
        return CheckReport.model_validate(report_json)

    def _error_result(
        self,
        *,
        spec: TaskCheckSpec | None,
        message: str,
        duration_ms: int,
        error_type: str,
        sandbox: SandboxExecutionResult | None,
    ) -> CheckRunResult:
        return CheckRunResult(
            check_type=self.check_type,
            status=CheckStatus.ERROR,
            score=0,
            report=self._error_report(
                spec=spec,
                message=message,
                duration_ms=duration_ms,
                error_type=error_type,
                sandbox=sandbox,
            ),
            spec_id=spec.id if spec else None,
            name=spec.name if spec else self.check_type.value,
            weight=spec.weight if spec else 100,
            is_required=spec.is_required if spec else True,
            execution_time_ms=duration_ms,
            memory_used_kb=0,
        )

    def _error_report(
        self,
        *,
        spec: TaskCheckSpec | None,
        message: str,
        duration_ms: int,
        error_type: str,
        sandbox: SandboxExecutionResult | None,
    ) -> CheckReport:
        name = spec.name if spec else self.check_type.value
        stdout = self._truncate(sandbox.stdout if sandbox else "")[0]
        stderr = self._truncate(sandbox.stderr if sandbox else "")[0]
        image = sandbox.image if sandbox else None
        exit_code = sandbox.exit_code if sandbox else None
        timed_out = sandbox.timed_out if sandbox else False
        container_name = sandbox.container_name if sandbox else None
        container_duration_ms = sandbox.duration_ms if sandbox else duration_ms

        return CheckReport(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=message,
            details=[
                CheckReportDetail(
                    name=name,
                    status=CheckStatus.ERROR,
                    message=message,
                    details={
                        "runner": "sandboxed_check_runner",
                        "error_type": error_type,
                        "check_type": self.check_type.value,
                        "check_name": name,
                        "sandbox": "docker",
                        "container_image": image,
                        "container_exit_code": exit_code,
                        "timedOut": timed_out,
                    },
                )
            ],
            metrics={
                "runner": "sandboxed_check_runner",
                "check_type": self.check_type.value,
                "check_name": name,
                "sandbox": "docker",
                "container_image": image,
                "container_name": container_name,
                "container_exit_code": exit_code,
                "container_timed_out": timed_out,
                "container_duration_ms": container_duration_ms,
                "containerDurationMs": container_duration_ms,
                "duration_ms": duration_ms,
                "durationMs": duration_ms,
                "timedOut": timed_out,
            },
            artifacts={
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration_ms": duration_ms,
                "durationMs": duration_ms,
                "timedOut": timed_out,
                "container_image": image,
                "container_stdout": stdout,
                "container_stderr": stderr,
                "container_exit_code": exit_code,
                "container_duration_ms": container_duration_ms,
                "containerDurationMs": container_duration_ms,
            },
        )

    def _timeout_seconds(self, spec: TaskCheckSpec) -> int:
        if isinstance(spec.timeout_seconds, int) and spec.timeout_seconds > 0:
            return spec.timeout_seconds
        return 10

    def _bounded_score(self, value: object) -> int:
        if not isinstance(value, int):
            return 0
        return min(max(value, 0), 100)

    def _non_negative_int(self, value: object, *, fallback: int) -> int:
        if not isinstance(value, int) or value < 0:
            return fallback
        return value

    def _truncate(self, value: str) -> tuple[str, bool]:
        if len(value) <= OUTPUT_LIMIT:
            return value, False
        return value[:OUTPUT_LIMIT], True
