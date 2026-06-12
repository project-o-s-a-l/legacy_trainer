from __future__ import annotations

import json
import subprocess
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from backend.app.core.config import settings
from backend.app.db.enums import SubmissionCheckType


@dataclass(frozen=True)
class DockerSandboxConfig:
    image: str = "legacy-trainer-checker:local"
    docker_bin: str = "docker"
    cpus: str = "0.5"
    memory: str = "256m"
    pids_limit: int = 128
    user: str = "10001:10001"
    tmpfs_size: str = "64m"
    workspace_tmpfs_size: str = "64m"
    timeout_overhead_seconds: int = 3
    cleanup_timeout_seconds: int = 5


@dataclass(frozen=True)
class SandboxExecutionRequest:
    check_type: SubmissionCheckType
    check_name: str
    submission_id: int | None
    spec_id: int | None
    timeout_seconds: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class SandboxExecutionResult:
    image: str
    container_name: str
    exit_code: int | None
    timed_out: bool
    duration_ms: int
    stdout: str
    stderr: str
    error: str | None = None


class SandboxExecutor(Protocol):
    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        ...


class DockerSandboxExecutor:
    def __init__(self, config: DockerSandboxConfig | None = None) -> None:
        self.config = config or docker_sandbox_config_from_settings()

    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        container_name = self.container_name(request)
        command = self.build_run_command(request, container_name)
        timeout_seconds = request.timeout_seconds + self.config.timeout_overhead_seconds
        payload_json = json.dumps(request.payload, ensure_ascii=False)
        started_at = time.perf_counter()

        try:
            completed = subprocess.run(
                command,
                input=payload_json,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            self.remove_container(container_name)
            return SandboxExecutionResult(
                image=self.config.image,
                container_name=container_name,
                exit_code=None,
                timed_out=True,
                duration_ms=self.duration_ms(started_at),
                stdout=self.normalize_output(exc.stdout),
                stderr=self.normalize_output(exc.stderr),
                error=f"Sandbox container timed out after {timeout_seconds} seconds",
            )
        except FileNotFoundError as exc:
            return SandboxExecutionResult(
                image=self.config.image,
                container_name=container_name,
                exit_code=None,
                timed_out=False,
                duration_ms=self.duration_ms(started_at),
                stdout="",
                stderr="",
                error=f"Docker executable not found: {exc.filename or self.config.docker_bin}",
            )
        except Exception as exc:
            self.remove_container(container_name)
            return SandboxExecutionResult(
                image=self.config.image,
                container_name=container_name,
                exit_code=None,
                timed_out=False,
                duration_ms=self.duration_ms(started_at),
                stdout="",
                stderr="",
                error=f"Sandbox executor failed: {exc}",
            )

        return SandboxExecutionResult(
            image=self.config.image,
            container_name=container_name,
            exit_code=completed.returncode,
            timed_out=False,
            duration_ms=self.duration_ms(started_at),
            stdout=self.normalize_output(completed.stdout),
            stderr=self.normalize_output(completed.stderr),
        )

    def build_run_command(
        self,
        request: SandboxExecutionRequest,
        container_name: str,
    ) -> list[str]:
        return [
            self.config.docker_bin,
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--cpus",
            self.config.cpus,
            "--memory",
            self.config.memory,
            "--pids-limit",
            str(self.config.pids_limit),
            "--read-only",
            "--tmpfs",
            f"/tmp:rw,nosuid,nodev,noexec,size={self.config.tmpfs_size}",
            "--tmpfs",
            (
                "/workspace:rw,nosuid,nodev,"
                f"size={self.config.workspace_tmpfs_size},uid=10001,gid=10001"
            ),
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--user",
            self.config.user,
            "--workdir",
            "/workspace",
            "--env",
            "HOME=/tmp",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            "PYTHONUNBUFFERED=1",
            "--label",
            "legacy-trainer.checker=true",
            "--label",
            f"legacy-trainer.check-type={request.check_type.value}",
            "-i",
            self.config.image,
        ]

    def remove_container(self, container_name: str) -> None:
        try:
            subprocess.run(
                [self.config.docker_bin, "rm", "-f", container_name],
                capture_output=True,
                text=True,
                timeout=self.config.cleanup_timeout_seconds,
                check=False,
                shell=False,
            )
        except Exception:
            return

    def container_name(self, request: SandboxExecutionRequest) -> str:
        parts = [
            "legacy-trainer-check",
            request.check_type.value,
            str(request.submission_id or "new"),
            str(request.spec_id or "legacy"),
            uuid.uuid4().hex[:12],
        ]
        return "-".join(self.safe_name_part(part) for part in parts)

    def safe_name_part(self, value: str) -> str:
        result = "".join(
            char.lower() if char.isalnum() else "-"
            for char in value
        ).strip("-")
        return result or "x"

    def duration_ms(self, started_at: float) -> int:
        return max(int((time.perf_counter() - started_at) * 1000), 0)

    def normalize_output(self, value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value


def docker_sandbox_config_from_settings() -> DockerSandboxConfig:
    return DockerSandboxConfig(
        image=settings.checker_sandbox_image,
        docker_bin=settings.checker_docker_bin,
        cpus=settings.checker_sandbox_cpus,
        memory=settings.checker_sandbox_memory,
        pids_limit=settings.checker_sandbox_pids_limit,
        user=settings.checker_sandbox_user,
        tmpfs_size=settings.checker_sandbox_tmpfs_size,
        workspace_tmpfs_size=settings.checker_sandbox_workspace_tmpfs_size,
        timeout_overhead_seconds=settings.checker_sandbox_timeout_overhead_seconds,
        cleanup_timeout_seconds=settings.checker_sandbox_cleanup_timeout_seconds,
    )
