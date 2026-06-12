from __future__ import annotations

from backend.app.db.enums import SubmissionCheckType
from backend.app.services.checking.sandbox import SandboxExecutor
from backend.app.services.checking.sandboxed_runner import SandboxedCheckRunner


class PythonStaticRunner(SandboxedCheckRunner):
    check_type = SubmissionCheckType.STATIC

    def __init__(self, executor: SandboxExecutor | None = None) -> None:
        super().__init__(SubmissionCheckType.STATIC, executor=executor)


class PythonArchitectureRunner(SandboxedCheckRunner):
    check_type = SubmissionCheckType.ARCHITECTURE

    def __init__(self, executor: SandboxExecutor | None = None) -> None:
        super().__init__(SubmissionCheckType.ARCHITECTURE, executor=executor)
