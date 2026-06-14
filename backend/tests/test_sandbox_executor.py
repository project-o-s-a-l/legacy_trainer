from __future__ import annotations

import json
import subprocess

from backend.app.db.enums import SubmissionCheckType
from backend.app.services.checking.sandbox import (
    DockerSandboxConfig,
    DockerSandboxExecutor,
    SandboxExecutionRequest,
)


def make_request() -> SandboxExecutionRequest:
    return SandboxExecutionRequest(
        check_type=SubmissionCheckType.TESTS,
        check_name="pytest",
        submission_id=42,
        spec_id=7,
        timeout_seconds=5,
        payload={"check_type": "tests"},
    )


def test_docker_sandbox_command_builder_uses_isolation_flags() -> None:
    executor = DockerSandboxExecutor(
        DockerSandboxConfig(
            image="checker:test",
            docker_bin="docker",
            cpus="0.25",
            memory="128m",
            pids_limit=64,
        )
    )

    command = executor.build_run_command(make_request(), "check-container")

    assert command[:2] == ["docker", "run"]
    assert "--rm" in command
    assert command[command.index("--name") + 1] == "check-container"
    assert command[command.index("--network") + 1] == "none"
    assert command[command.index("--cpus") + 1] == "0.25"
    assert command[command.index("--memory") + 1] == "128m"
    assert command[command.index("--pids-limit") + 1] == "64"
    assert "--read-only" in command
    assert "--cap-drop" in command
    assert command[command.index("--cap-drop") + 1] == "ALL"
    assert "--security-opt" in command
    assert command[command.index("--security-opt") + 1] == "no-new-privileges"
    assert "--user" in command
    assert command[command.index("--user") + 1] == "10001:10001"
    assert "--tmpfs" in command
    assert "-i" in command
    assert command[-1] == "checker:test"
    assert "-v" not in command
    assert "--volume" not in command
    assert "/var/run/docker.sock" not in command


def test_docker_sandbox_executor_serializes_payload_to_stdin(monkeypatch) -> None:
    payload = {
        "check_type": "tests",
        "source_code": "def solve():\n    return 1\n",
        "config": {"entry_file": "solution.py"},
    }
    request = SandboxExecutionRequest(
        check_type=SubmissionCheckType.TESTS,
        check_name="pytest",
        submission_id=42,
        spec_id=7,
        timeout_seconds=5,
        payload=payload,
    )

    def fake_run(command, **kwargs):
        assert command[:2] == ["docker", "run"]
        assert kwargs["shell"] is False
        assert kwargs["encoding"] == "utf-8"
        assert json.loads(kwargs["input"]) == payload
        return subprocess.CompletedProcess(command, 0, '{"ok": true}', "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    executor = DockerSandboxExecutor(DockerSandboxConfig(image="checker:test"))

    result = executor.execute(request)

    assert result.exit_code == 0
    assert result.stdout == '{"ok": true}'


def test_docker_sandbox_executor_removes_container_on_timeout(monkeypatch) -> None:
    calls: list[tuple[list[str], dict]] = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        assert kwargs["shell"] is False
        if command[1] == "run":
            raise subprocess.TimeoutExpired(
                cmd=command,
                timeout=8,
                output="partial stdout",
                stderr="partial stderr",
            )
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    executor = DockerSandboxExecutor(DockerSandboxConfig(image="checker:test"))

    result = executor.execute(make_request())

    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "partial stdout"
    assert result.stderr == "partial stderr"
    assert result.error == "Sandbox container timed out after 8 seconds"
    assert any(call[0][1:3] == ["rm", "-f"] for call in calls)


def test_docker_sandbox_executor_reports_missing_docker(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        raise FileNotFoundError("docker missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    executor = DockerSandboxExecutor(DockerSandboxConfig(image="checker:test"))

    result = executor.execute(make_request())

    assert result.timed_out is False
    assert result.exit_code is None
    assert result.error is not None
    assert "Docker executable not found" in result.error
