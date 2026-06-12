from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.db.enums import CheckStatus, SubmissionCheckType, SubmissionStatus


@dataclass(slots=True)
class ScenarioDefinition:
    id: int
    name: str
    weight: int
    input_payload: dict[str, Any]
    expected_output: Any = None


@dataclass(slots=True)
class RuleDefinition:
    rule_type: str
    weight: int
    config: dict[str, Any]


@dataclass(slots=True)
class TaskDefinition:
    task_id: int
    language_name: str
    legacy_code: str | None
    scenarios: list[ScenarioDefinition] = field(default_factory=list)
    rules: dict[str, RuleDefinition] = field(default_factory=dict)


@dataclass(slots=True)
class ModuleWorkspace:
    root_dir: Path
    language_name: str
    legacy_path: Path
    candidate_path: Path
    python_harness_path: Path | None = None
    legacy_binary_path: Path | None = None
    candidate_binary_path: Path | None = None


@dataclass(slots=True)
class CommandExecutionResult:
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False

    def succeeded(self) -> bool:
        return not self.timed_out and self.exit_code == 0


@dataclass(slots=True)
class CheckOutcome:
    check_type: SubmissionCheckType
    status: CheckStatus
    score: int
    max_score: int
    report: dict[str, Any]


@dataclass(slots=True)
class PipelineResult:
    status: SubmissionStatus
    score: int
    message: str
    test_passed: int
    total_tests: int
    checks: list[CheckOutcome]
    execution_time_ms: int | None = None
    memory_used_kb: int | None = None
