from __future__ import annotations

from backend.app.db.enums import SubmissionCheckType
from backend.app.services.checking.sandbox import SandboxExecutor
from backend.app.services.checking.sandboxed_runner import SandboxedCheckRunner


class PythonPytestRunner(SandboxedCheckRunner):
    check_type = SubmissionCheckType.TESTS

    def __init__(self, executor: SandboxExecutor | None = None) -> None:
        super().__init__(SubmissionCheckType.TESTS, executor=executor)
