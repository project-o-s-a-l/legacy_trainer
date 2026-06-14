from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from backend.app.core.config import settings
from backend.app.services.refactor_checks.models import ModuleWorkspace

_PYTHON_HARNESS = """\
import importlib.util
import json
import sys


def main() -> int:
    module_path = sys.argv[1]
    function_name = sys.argv[2]
    payload = json.loads(sys.stdin.read() or "{}")

    try:
        spec = importlib.util.spec_from_file_location("submission_module", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to load module spec")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        target = getattr(module, function_name)
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        result = target(*args, **kwargs)
        output = {"ok": True, "result": result}
        print(json.dumps(output, ensure_ascii=False, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        output = {
            "ok": False,
            "errorType": exc.__class__.__name__,
            "errorMessage": str(exc),
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
"""


class ModuleWorkspaceBuilder:
    def build(
        self,
        *,
        language_name: str,
        legacy_code: str,
        candidate_code: str,
    ) -> ModuleWorkspace:
        workspace_root = settings.check_workspace_root.strip()
        if workspace_root:
            root_base = Path(workspace_root)
            root_base.mkdir(parents=True, exist_ok=True)
            root_dir = Path(
                tempfile.mkdtemp(
                    prefix=f"legacy_refactor_{language_name}_",
                    dir=str(root_base),
                )
            )
        else:
            root_dir = Path(tempfile.mkdtemp(prefix=f"legacy_refactor_{language_name}_"))

        self._prepare_root_dir(root_dir)
        suffix = ".py" if language_name == "python" else ".cpp"

        legacy_path = root_dir / f"legacy_module{suffix}"
        candidate_path = root_dir / f"candidate_module{suffix}"
        legacy_path.write_text(legacy_code, encoding="utf-8")
        candidate_path.write_text(candidate_code, encoding="utf-8")

        python_harness_path: Path | None = None
        if language_name == "python":
            python_harness_path = root_dir / "_invoke_python_function.py"
            python_harness_path.write_text(_PYTHON_HARNESS, encoding="utf-8")

        return ModuleWorkspace(
            root_dir=root_dir,
            language_name=language_name,
            legacy_path=legacy_path,
            candidate_path=candidate_path,
            python_harness_path=python_harness_path,
            legacy_binary_path=(root_dir / "legacy_module.exe")
            if language_name == "cpp"
            else None,
            candidate_binary_path=(root_dir / "candidate_module.exe")
            if language_name == "cpp"
            else None,
        )

    def cleanup(self, workspace: ModuleWorkspace) -> None:
        shutil.rmtree(workspace.root_dir, ignore_errors=True)

    def _prepare_root_dir(self, root_dir: Path) -> None:
        if settings.check_execution_backend.strip().lower() == "docker":
            root_dir.chmod(0o777)
