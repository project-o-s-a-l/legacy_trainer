from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterable

from backend.app.services.checking.sandbox import (
    SandboxExecutionRequest,
    SandboxExecutionResult,
)
from legacy_checker.checks import run_check


class InProcessSandboxExecutor:
    def __init__(
        self,
        scripted_results: Iterable[SandboxExecutionResult] | None = None,
    ) -> None:
        self.scripted_results = list(scripted_results or [])
        self.requests: list[SandboxExecutionRequest] = []

    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        self.requests.append(request)
        if self.scripted_results:
            return self.scripted_results.pop(0)

        current_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="legacy-trainer-fake-sandbox-") as temp_dir:
            os.chdir(temp_dir)
            try:
                result = run_check(request.payload)
            finally:
                os.chdir(current_dir)
        return SandboxExecutionResult(
            image="legacy-trainer-checker:test",
            container_name=f"fake-container-{len(self.requests)}",
            exit_code=0,
            timed_out=False,
            duration_ms=int(result.get("execution_time_ms", 0)),
            stdout=json.dumps(result, ensure_ascii=False),
            stderr="",
        )


def sandbox_result(
    *,
    status: str = "passed",
    score: int = 100,
    check_type: str = "tests",
    summary: str = "fake check passed",
    exit_code: int | None = 0,
    timed_out: bool = False,
    error: str | None = None,
) -> SandboxExecutionResult:
    payload = {
        "check_type": check_type,
        "status": status,
        "score": score,
        "execution_time_ms": 7,
        "memory_used_kb": 0,
        "timedOut": timed_out,
        "report": {
            "total": 1,
            "passed": 1 if status == "passed" else 0,
            "failed": 1 if status == "failed" else 0,
            "errors": 1 if status == "error" else 0,
            "summary": summary,
            "details": [
                {
                    "name": "fake",
                    "status": status,
                    "message": summary,
                    "path": None,
                    "line": None,
                    "column": None,
                    "details": {"runner": "fake_sandbox"},
                }
            ],
            "metrics": {
                "runner": "fake_sandbox",
                "duration_ms": 7,
                "durationMs": 7,
                "timedOut": timed_out,
            },
            "artifacts": {
                "stdout": "fake stdout",
                "stderr": "fake stderr" if status == "error" else "",
                "exit_code": exit_code,
                "duration_ms": 7,
                "durationMs": 7,
                "timedOut": timed_out,
            },
        },
    }
    return SandboxExecutionResult(
        image="legacy-trainer-checker:test",
        container_name="fake-container",
        exit_code=exit_code,
        timed_out=timed_out,
        duration_ms=9,
        stdout=json.dumps(payload, ensure_ascii=False),
        stderr="",
        error=error,
    )
