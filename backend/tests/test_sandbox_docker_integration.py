from __future__ import annotations

import json
import os

import pytest

from backend.app.db.enums import SubmissionCheckType
from backend.app.services.checking.sandbox import (
    DockerSandboxExecutor,
    SandboxExecutionRequest,
)


pytestmark = pytest.mark.skipif(
    os.getenv("LEGACY_TRAINER_RUN_DOCKER_SANDBOX_TESTS") != "1",
    reason=(
        "Optional Docker sandbox integration test. Build "
        "legacy-trainer-checker:local and set "
        "LEGACY_TRAINER_RUN_DOCKER_SANDBOX_TESTS=1 to run."
    ),
)


def test_docker_sandbox_runs_static_check_in_checker_container() -> None:
    executor = DockerSandboxExecutor()
    result = executor.execute(
        SandboxExecutionRequest(
            check_type=SubmissionCheckType.STATIC,
            check_name="static integration",
            submission_id=1,
            spec_id=1,
            timeout_seconds=5,
            payload={
                "check_type": "static",
                "check_name": "static integration",
                "timeout_seconds": 5,
                "program_language": "python",
                "source_code": "class Solution:\n    pass\n",
                "config": {"required_symbols": ["Solution"]},
            },
        )
    )

    assert result.error is None
    assert result.timed_out is False
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["status"] == "passed"
    assert parsed["report"]["metrics"]["runner"] == "python_static_ast"
