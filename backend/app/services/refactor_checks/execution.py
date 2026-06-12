from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from time import perf_counter
from typing import Any

from backend.app.core.config import settings
from backend.app.services.refactor_checks.models import (
    CommandExecutionResult,
    ModuleWorkspace,
)


class RefactorModuleExecutor:
    _SUPPORTED_BACKENDS = {"local", "docker"}

    def __init__(self, backend: str | None = None) -> None:
        configured_backend = (backend or settings.check_execution_backend).strip().lower()
        if configured_backend not in self._SUPPORTED_BACKENDS:
            raise RuntimeError(
                f"Unsupported execution backend: {configured_backend}"
            )
        self.backend = configured_backend

    def execute_command(
        self,
        *,
        command: list[str],
        cwd: Path,
        stdin_text: str | None = None,
        timeout_seconds: int | None = None,
    ) -> CommandExecutionResult:
        start = perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                input=stdin_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds or settings.check_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((perf_counter() - start) * 1000)
            return CommandExecutionResult(
                command=command,
                exit_code=None,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                duration_ms=duration_ms,
                timed_out=True,
            )
        except OSError as exc:
            duration_ms = int((perf_counter() - start) * 1000)
            return CommandExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr=str(exc),
                duration_ms=duration_ms,
                timed_out=False,
            )

        duration_ms = int((perf_counter() - start) * 1000)
        return CommandExecutionResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=duration_ms,
            timed_out=False,
        )

    def run_python_stdin(
        self,
        *,
        module_path: Path,
        workspace: ModuleWorkspace,
        stdin_text: str,
    ) -> CommandExecutionResult:
        if self.backend == "docker":
            container_module_path = self._to_container_path(
                workspace=workspace,
                host_path=module_path,
            )
            return self._execute_docker_command(
                workspace=workspace,
                language_name="python",
                command=["python", "-I", str(container_module_path)],
                stdin_text=stdin_text,
            )

        return self.execute_command(
            command=[sys.executable, str(module_path)],
            cwd=workspace.root_dir,
            stdin_text=stdin_text,
        )

    def run_python_function(
        self,
        *,
        module_path: Path,
        workspace: ModuleWorkspace,
        function_name: str,
        payload: dict[str, Any],
    ) -> CommandExecutionResult:
        if workspace.python_harness_path is None:
            raise RuntimeError("Python function harness is not available")

        if self.backend == "docker":
            container_harness_path = self._to_container_path(
                workspace=workspace,
                host_path=workspace.python_harness_path,
            )
            container_module_path = self._to_container_path(
                workspace=workspace,
                host_path=module_path,
            )
            return self._execute_docker_command(
                workspace=workspace,
                language_name="python",
                command=[
                    "python",
                    "-I",
                    str(container_harness_path),
                    str(container_module_path),
                    function_name,
                ],
                stdin_text=json.dumps(payload, ensure_ascii=False),
            )

        return self.execute_command(
            command=[
                sys.executable,
                str(workspace.python_harness_path),
                str(module_path),
                function_name,
            ],
            cwd=workspace.root_dir,
            stdin_text=json.dumps(payload, ensure_ascii=False),
        )

    def compile_cpp(
        self,
        *,
        source_path: Path,
        binary_path: Path,
        workspace: ModuleWorkspace,
    ) -> CommandExecutionResult:
        if self.backend == "docker":
            container_source_path = self._to_container_path(
                workspace=workspace,
                host_path=source_path,
            )
            container_binary_path = self._to_container_path(
                workspace=workspace,
                host_path=binary_path,
            )
            return self._execute_docker_command(
                workspace=workspace,
                language_name="cpp",
                command=[
                    "g++",
                    "-std=c++17",
                    str(container_source_path),
                    "-O2",
                    "-o",
                    str(container_binary_path),
                ],
            )

        compiler = shutil.which("g++") or "g++"
        return self.execute_command(
            command=[
                compiler,
                "-std=c++17",
                str(source_path),
                "-O2",
                "-o",
                str(binary_path),
            ],
            cwd=workspace.root_dir,
        )

    def run_binary(
        self,
        *,
        binary_path: Path,
        workspace: ModuleWorkspace,
        stdin_text: str,
    ) -> CommandExecutionResult:
        if self.backend == "docker":
            container_binary_path = self._to_container_path(
                workspace=workspace,
                host_path=binary_path,
            )
            return self._execute_docker_command(
                workspace=workspace,
                language_name="cpp",
                command=[str(container_binary_path)],
                stdin_text=stdin_text,
            )

        return self.execute_command(
            command=[str(binary_path)],
            cwd=workspace.root_dir,
            stdin_text=stdin_text,
        )

    def _execute_docker_command(
        self,
        *,
        workspace: ModuleWorkspace,
        language_name: str,
        command: list[str],
        stdin_text: str | None = None,
        timeout_seconds: int | None = None,
    ) -> CommandExecutionResult:
        docker_binary = shutil.which("docker") or "docker"
        docker_command = self._build_docker_command(
            workspace=workspace,
            language_name=language_name,
            command=command,
            attach_stdin=stdin_text is not None,
        )
        return self.execute_command(
            command=[docker_binary, *docker_command],
            cwd=workspace.root_dir,
            stdin_text=stdin_text,
            timeout_seconds=timeout_seconds,
        )

    def _build_docker_command(
        self,
        *,
        workspace: ModuleWorkspace,
        language_name: str,
        command: list[str],
        attach_stdin: bool = False,
    ) -> list[str]:
        workspace_dir = settings.check_docker_workspace_dir.rstrip("/") or "/workspace"
        tmp_dir = settings.check_docker_tmp_dir.rstrip("/") or "/tmp"
        image = self._get_docker_image(language_name=language_name)
        mount_argument = (
            f"type=bind,src={workspace.root_dir.resolve()},dst={workspace_dir}"
        )

        docker_command = [
            "run",
            "--rm",
            "--workdir",
            workspace_dir,
            "--mount",
            mount_argument,
            "--user",
            settings.check_docker_container_user,
            "--memory",
            settings.check_docker_memory_limit,
            "--cpus",
            settings.check_docker_cpus,
            "--pids-limit",
            str(settings.check_docker_pids_limit),
            "--tmpfs",
            f"{tmp_dir}:rw,noexec,nosuid,size={settings.check_docker_tmpfs_size}",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
        ]

        if attach_stdin:
            docker_command.append("-i")

        if settings.check_docker_disable_network:
            docker_command.extend(["--network", "none"])
        if settings.check_docker_read_only_rootfs:
            docker_command.append("--read-only")
        if settings.check_docker_drop_capabilities:
            docker_command.extend(["--cap-drop", "ALL"])
        if settings.check_docker_no_new_privileges:
            docker_command.extend(["--security-opt", "no-new-privileges:true"])

        docker_command.extend([image, *command])
        return docker_command

    def _get_docker_image(self, *, language_name: str) -> str:
        normalized_language = language_name.strip().lower()
        if normalized_language == "python":
            return settings.check_docker_python_image
        if normalized_language == "cpp":
            return settings.check_docker_cpp_image
        raise RuntimeError(f"Unsupported Docker execution language: {language_name}")

    def _to_container_path(
        self,
        *,
        workspace: ModuleWorkspace,
        host_path: Path,
    ) -> PurePosixPath:
        workspace_dir = settings.check_docker_workspace_dir.rstrip("/") or "/workspace"
        relative_path = host_path.resolve().relative_to(workspace.root_dir.resolve())
        return PurePosixPath(workspace_dir, *relative_path.parts)
