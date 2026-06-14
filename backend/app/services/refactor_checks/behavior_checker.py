from __future__ import annotations

import json
from typing import Any

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.services.refactor_checks.execution import RefactorModuleExecutor
from backend.app.services.refactor_checks.models import (
    CheckOutcome,
    ModuleWorkspace,
    RuleDefinition,
    ScenarioDefinition,
)


class BehaviorChecker:
    def __init__(self, executor: RefactorModuleExecutor | None = None) -> None:
        self.executor = executor or RefactorModuleExecutor()

    def run(
        self,
        *,
        workspace: ModuleWorkspace,
        rule: RuleDefinition,
        scenarios: list[ScenarioDefinition],
        legacy_code_available: bool,
    ) -> CheckOutcome:
        mode = str(rule.config.get("mode", "stdin")).strip().lower()
        entrypoint = str(rule.config.get("entrypoint", "")).strip()

        if not scenarios:
            return CheckOutcome(
                check_type=SubmissionCheckType.TESTS,
                status=CheckStatus.ERROR,
                score=0,
                max_score=rule.weight,
                report={"message": "No behaviour scenarios configured"},
            )

        details: list[dict[str, Any]] = []
        passed_count = 0
        platform_error = False
        total_duration_ms = 0

        compile_report: dict[str, Any] | None = None
        legacy_compile_report: dict[str, Any] | None = None

        if workspace.language_name == "cpp":
            if workspace.legacy_binary_path is None or workspace.candidate_binary_path is None:
                return self._error(rule.weight, "C++ workspace is incomplete")

            if legacy_code_available:
                legacy_compile = self.executor.compile_cpp(
                    source_path=workspace.legacy_path,
                    binary_path=workspace.legacy_binary_path,
                    workspace=workspace,
                )
                total_duration_ms += legacy_compile.duration_ms
                legacy_compile_report = self._execution_report(legacy_compile)
                if not legacy_compile.succeeded():
                    return CheckOutcome(
                        check_type=SubmissionCheckType.TESTS,
                        status=CheckStatus.ERROR,
                        score=0,
                        max_score=rule.weight,
                        report={
                            "message": "Legacy baseline compilation failed",
                            "compile": legacy_compile_report,
                        },
                    )

            candidate_compile = self.executor.compile_cpp(
                source_path=workspace.candidate_path,
                binary_path=workspace.candidate_binary_path,
                workspace=workspace,
            )
            total_duration_ms += candidate_compile.duration_ms
            compile_report = self._execution_report(candidate_compile)
            if not candidate_compile.succeeded():
                return CheckOutcome(
                    check_type=SubmissionCheckType.TESTS,
                    status=CheckStatus.FAILED,
                    score=0,
                    max_score=rule.weight,
                    report={
                        "message": "Candidate compilation failed",
                        "compile": compile_report,
                    },
                )

        for scenario in scenarios:
            if mode == "python_function":
                if workspace.language_name != "python":
                    return self._error(rule.weight, "python_function mode is only supported for Python")
                if not entrypoint:
                    return self._error(rule.weight, "Behaviour rule must define entrypoint")

                candidate_result = self.executor.run_python_function(
                    module_path=workspace.candidate_path,
                    workspace=workspace,
                    function_name=entrypoint,
                    payload=scenario.input_payload,
                )
                legacy_result = None
                if scenario.expected_output is None:
                    if not legacy_code_available:
                        return self._error(
                            rule.weight,
                            "Legacy code is required when expected output is not provided",
                        )
                    legacy_result = self.executor.run_python_function(
                        module_path=workspace.legacy_path,
                        workspace=workspace,
                        function_name=entrypoint,
                        payload=scenario.input_payload,
                    )
                actual_value = self._parse_json_result(candidate_result)
                expected_value = (
                    self._normalize_expected_python(scenario.expected_output)
                    if scenario.expected_output is not None
                    else self._parse_json_result(legacy_result)
                )
                total_duration_ms += candidate_result.duration_ms
                if legacy_result is not None:
                    total_duration_ms += legacy_result.duration_ms
                result_error = candidate_result.exit_code is None or (
                    legacy_result is not None and legacy_result.exit_code is None
                )
                passed = candidate_result.succeeded() and actual_value == expected_value
            else:
                stdin_text = str(scenario.input_payload.get("stdin", ""))
                if workspace.language_name == "python":
                    candidate_result = self.executor.run_python_stdin(
                        module_path=workspace.candidate_path,
                        workspace=workspace,
                        stdin_text=stdin_text,
                    )
                    legacy_result = None
                    if scenario.expected_output is None:
                        if not legacy_code_available:
                            return self._error(
                                rule.weight,
                                "Legacy code is required when expected output is not provided",
                            )
                        legacy_result = self.executor.run_python_stdin(
                            module_path=workspace.legacy_path,
                            workspace=workspace,
                            stdin_text=stdin_text,
                        )
                else:
                    if workspace.candidate_binary_path is None:
                        return self._error(rule.weight, "C++ binary path is not prepared")
                    candidate_result = self.executor.run_binary(
                        binary_path=workspace.candidate_binary_path,
                        workspace=workspace,
                        stdin_text=stdin_text,
                    )
                    legacy_result = None
                    if scenario.expected_output is None:
                        if workspace.legacy_binary_path is None:
                            return self._error(rule.weight, "Legacy binary path is not prepared")
                        if not legacy_code_available:
                            return self._error(
                                rule.weight,
                                "Legacy code is required when expected output is not provided",
                            )
                        legacy_result = self.executor.run_binary(
                            binary_path=workspace.legacy_binary_path,
                            workspace=workspace,
                            stdin_text=stdin_text,
                        )

                actual_value = candidate_result.stdout.strip()
                expected_value = (
                    str(scenario.expected_output).strip()
                    if scenario.expected_output is not None
                    else legacy_result.stdout.strip()
                )
                total_duration_ms += candidate_result.duration_ms
                if legacy_result is not None:
                    total_duration_ms += legacy_result.duration_ms
                result_error = candidate_result.exit_code is None or (
                    legacy_result is not None and legacy_result.exit_code is None
                )
                passed = candidate_result.succeeded() and actual_value == expected_value

            if result_error:
                platform_error = True

            if passed:
                passed_count += 1

            details.append(
                {
                    "scenarioId": scenario.id,
                    "name": scenario.name,
                    "status": "passed" if passed else "failed",
                    "input": scenario.input_payload,
                    "expected": expected_value,
                    "actual": actual_value,
                    "candidate": self._execution_report(candidate_result),
                    "legacy": self._execution_report(legacy_result) if legacy_result else None,
                }
            )

        total = len(scenarios)
        failed = total - passed_count
        if platform_error:
            status = CheckStatus.ERROR
        elif failed == 0:
            status = CheckStatus.PASSED
        else:
            status = CheckStatus.FAILED

        score = round((passed_count / total) * rule.weight) if total > 0 else 0
        return CheckOutcome(
            check_type=SubmissionCheckType.TESTS,
            status=status,
            score=score,
            max_score=rule.weight,
            report={
                "mode": mode,
                "total": total,
                "passed": passed_count,
                "failed": failed,
                "details": details,
                "compile": compile_report,
                "legacyCompile": legacy_compile_report,
                "durationMs": total_duration_ms,
            },
        )

    def _error(self, max_score: int, message: str) -> CheckOutcome:
        return CheckOutcome(
            check_type=SubmissionCheckType.TESTS,
            status=CheckStatus.ERROR,
            score=0,
            max_score=max_score,
            report={"message": message},
        )

    def _execution_report(self, result) -> dict[str, Any] | None:
        if result is None:
            return None
        return {
            "command": result.command,
            "exitCode": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "durationMs": result.duration_ms,
            "timedOut": result.timed_out,
        }

    def _parse_json_result(self, result) -> dict[str, Any]:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "errorType": "InvalidJSON",
                "errorMessage": result.stdout.strip() or result.stderr.strip(),
            }

    def _normalize_expected_python(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict) and "ok" in value:
            return value
        return {"ok": True, "result": value}
