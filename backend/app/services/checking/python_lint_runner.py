from __future__ import annotations

from backend.app.db.enums import SubmissionCheckType
from backend.app.services.checking.sandbox import SandboxExecutor
from backend.app.services.checking.sandboxed_runner import SandboxedCheckRunner


class PythonRuffLintRunner(SandboxedCheckRunner):
    check_type = SubmissionCheckType.LINT

    def __init__(self, executor: SandboxExecutor | None = None) -> None:
        super().__init__(SubmissionCheckType.LINT, executor=executor)
