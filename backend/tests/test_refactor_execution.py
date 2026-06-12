import json
from pathlib import Path

from backend.app.core.config import settings
from backend.app.services.refactor_checks.execution import RefactorModuleExecutor
from backend.app.services.refactor_checks.models import CommandExecutionResult
from backend.app.services.refactor_checks.workspace import ModuleWorkspaceBuilder


def test_run_python_function_uses_local_executor_by_default() -> None:
    builder = ModuleWorkspaceBuilder()
    workspace = builder.build(
        language_name="python",
        legacy_code="def format_order(total, vip=False):\n    return total\n",
        candidate_code="def format_order(total, vip=False):\n    return total * 2\n",
    )

    try:
        executor = RefactorModuleExecutor(backend="local")
        result = executor.run_python_function(
            module_path=workspace.candidate_path,
            workspace=workspace,
            function_name="format_order",
            payload={"args": [5], "kwargs": {}},
        )
    finally:
        builder.cleanup(workspace)

    assert result.succeeded()
    assert json.loads(result.stdout) == {"ok": True, "result": 10}


def test_run_python_function_wraps_execution_in_docker(
    monkeypatch,
) -> None:
    builder = ModuleWorkspaceBuilder()
    workspace = builder.build(
        language_name="python",
        legacy_code="def format_order(total, vip=False):\n    return total\n",
        candidate_code="def format_order(total, vip=False):\n    return total\n",
    )
    captured: dict[str, object] = {}

    def fake_execute_command(
        self,
        *,
        command,
        cwd,
        stdin_text=None,
        timeout_seconds=None,
    ):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["stdin_text"] = stdin_text
        captured["timeout_seconds"] = timeout_seconds
        return CommandExecutionResult(
            command=command,
            exit_code=0,
            stdout='{"ok": true, "result": {"final_total": 90.0, "vip": true}}',
            stderr="",
            duration_ms=1,
        )

    monkeypatch.setattr(
        "backend.app.services.refactor_checks.execution.shutil.which",
        lambda name: None,
    )
    monkeypatch.setattr(RefactorModuleExecutor, "execute_command", fake_execute_command)
    monkeypatch.setattr(settings, "check_docker_python_image", "python-sandbox:test")
    monkeypatch.setattr(settings, "check_docker_workspace_dir", "/sandbox")
    monkeypatch.setattr(settings, "check_docker_tmp_dir", "/sandbox-tmp")

    try:
        executor = RefactorModuleExecutor(backend="docker")
        executor.run_python_function(
            module_path=workspace.candidate_path,
            workspace=workspace,
            function_name="format_order",
            payload={"args": [100, True], "kwargs": {}},
        )
    finally:
        builder.cleanup(workspace)

    command = captured["command"]
    assert isinstance(command, list)
    assert command[0] == "docker"
    assert command[1] == "run"
    assert "-i" in command
    assert "--network" in command
    assert "none" in command
    assert "--read-only" in command
    assert "--cap-drop" in command
    assert "--security-opt" in command
    assert "python-sandbox:test" in command
    assert any(
        isinstance(item, str)
        and item.startswith("type=bind,src=")
        and item.endswith(",dst=/sandbox")
        for item in command
    )
    assert command[-5:] == [
        "python",
        "-I",
        "/sandbox/_invoke_python_function.py",
        "/sandbox/candidate_module.py",
        "format_order",
    ]
    assert captured["cwd"] == workspace.root_dir
    assert json.loads(str(captured["stdin_text"])) == {
        "args": [100, True],
        "kwargs": {},
    }


def test_compile_cpp_wraps_execution_in_docker(monkeypatch) -> None:
    builder = ModuleWorkspaceBuilder()
    workspace = builder.build(
        language_name="cpp",
        legacy_code="#include <iostream>\nint main() { return 0; }\n",
        candidate_code="#include <iostream>\nint main() { return 0; }\n",
    )
    captured: dict[str, object] = {}

    def fake_execute_command(
        self,
        *,
        command,
        cwd,
        stdin_text=None,
        timeout_seconds=None,
    ):
        captured["command"] = command
        captured["cwd"] = cwd
        return CommandExecutionResult(
            command=command,
            exit_code=0,
            stdout="",
            stderr="",
            duration_ms=1,
        )

    monkeypatch.setattr(
        "backend.app.services.refactor_checks.execution.shutil.which",
        lambda name: None,
    )
    monkeypatch.setattr(RefactorModuleExecutor, "execute_command", fake_execute_command)
    monkeypatch.setattr(settings, "check_docker_cpp_image", "cpp-sandbox:test")
    monkeypatch.setattr(settings, "check_docker_workspace_dir", "/sandbox")

    try:
        executor = RefactorModuleExecutor(backend="docker")
        executor.compile_cpp(
            source_path=workspace.candidate_path,
            binary_path=workspace.candidate_binary_path,
            workspace=workspace,
        )
    finally:
        builder.cleanup(workspace)

    command = captured["command"]
    assert isinstance(command, list)
    assert command[0] == "docker"
    assert "cpp-sandbox:test" in command
    assert command[-6:] == [
        "g++",
        "-std=c++17",
        "/sandbox/candidate_module.cpp",
        "-O2",
        "-o",
        "/sandbox/candidate_module.exe",
    ]
    assert captured["cwd"] == workspace.root_dir


def test_workspace_builder_uses_configured_root(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "check_workspace_root", str(tmp_path))
    builder = ModuleWorkspaceBuilder()

    workspace = builder.build(
        language_name="python",
        legacy_code="def format_order(total, vip=False):\n    return total\n",
        candidate_code="def format_order(total, vip=False):\n    return total\n",
    )

    try:
        assert workspace.root_dir.parent == Path(tmp_path)
        assert workspace.legacy_path.exists()
        assert workspace.candidate_path.exists()
    finally:
        builder.cleanup(workspace)


def test_workspace_builder_relaxes_permissions_for_docker(
    tmp_path,
    monkeypatch,
) -> None:
    chmod_calls: list[tuple[Path, int]] = []
    original_chmod = Path.chmod

    def tracking_chmod(self: Path, mode: int) -> None:
        chmod_calls.append((self, mode))
        original_chmod(self, mode)

    monkeypatch.setattr(settings, "check_workspace_root", str(tmp_path))
    monkeypatch.setattr(settings, "check_execution_backend", "docker")
    monkeypatch.setattr(Path, "chmod", tracking_chmod)

    builder = ModuleWorkspaceBuilder()
    workspace = builder.build(
        language_name="python",
        legacy_code="def format_order(total, vip=False):\n    return total\n",
        candidate_code="def format_order(total, vip=False):\n    return total\n",
    )

    try:
        assert (workspace.root_dir, 0o777) in chmod_calls
    finally:
        builder.cleanup(workspace)
