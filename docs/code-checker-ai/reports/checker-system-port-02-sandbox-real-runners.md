# Checker System Port 02 - Sandbox and Real Runners

## Summary

Ported sandboxed real Python runners for `TaskCheckSpec` checks without merging
`codex/phase-01-contracts-persistence` wholesale.

The default `TaskCheckSpec` orchestrator now runs:

- pytest checks through `PythonPytestRunner`
- Ruff lint checks through `PythonRuffLintRunner`
- Python AST static checks through `PythonStaticRunner`
- Python AST architecture checks through `PythonArchitectureRunner`

The no-spec fallback remains the deterministic fake tests runner, and the
current `RefactorCheckPipeline` path for `TaskScenario` / `TaskCheckRule`
tasks remains intact.

## Files Compared

Current branch context read before and during the port:

- `backend/app/core/config.py`
- `backend/app/services/submission.py`
- `backend/app/services/checking/`
- `backend/app/services/refactor_checks/`
- `backend/tests/conftest.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_refactor_submission_api.py`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`
- `compose.yaml`
- `docker/`

Source branch context read via `git show codex/phase-01-contracts-persistence:<path>`:

- `backend/app/services/checking/sandbox.py`
- `backend/app/services/checking/sandboxed_runner.py`
- `backend/app/services/checking/python_pytest_runner.py`
- `backend/app/services/checking/python_lint_runner.py`
- `backend/app/services/checking/python_static_runner.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/types.py`
- `backend/app/services/checking/__init__.py`
- `backend/tests/sandbox_fakes.py`
- `backend/tests/test_sandbox_executor.py`
- `backend/tests/test_sandboxed_runner.py`
- `backend/tests/test_sandbox_docker_integration.py`
- `backend/tests/test_submissions_api.py`
- `backend/app/core/config.py`
- `backend/requirements.txt`
- `docker/checker.Dockerfile`
- `docker/docker-compose.yml`
- `docker/.dockerignore`
- `legacy_checker/__init__.py`
- `legacy_checker/checks.py`
- `legacy_checker/run.py`

## Files Changed

Added:

- `backend/app/services/checking/sandbox.py`
- `backend/app/services/checking/sandboxed_runner.py`
- `backend/app/services/checking/python_pytest_runner.py`
- `backend/app/services/checking/python_lint_runner.py`
- `backend/app/services/checking/python_static_runner.py`
- `backend/tests/sandbox_fakes.py`
- `backend/tests/test_sandbox_executor.py`
- `backend/tests/test_sandboxed_runner.py`
- `backend/tests/test_sandbox_docker_integration.py`
- `docker/checker.Dockerfile`
- `legacy_checker/__init__.py`
- `legacy_checker/checks.py`
- `legacy_checker/run.py`

Updated:

- `.gitignore`
- `.env.example`
- `backend/app/core/config.py`
- `backend/app/services/checking/__init__.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/sandboxed_runner.py`
- `backend/app/services/submission.py`
- `backend/requirements-dev.txt`
- `backend/tests/test_submissions_api.py`
- `compose.yaml`

Pre-existing uncommitted phase-01 files remain in the working tree and were not
reverted: `TaskCheckSpec`, `backend/app/schemas/check.py`, repository/model
wiring, `backend/tests/test_task_check_specs.py`, and earlier docs/reports.

## Runner Contracts

`SandboxedCheckRunner` sends a `SandboxExecutionRequest` to a `SandboxExecutor`.
The request payload is JSON on stdin and contains:

- `check_type`
- `check_name`
- `timeout_seconds`
- `program_language`
- `source_code`
- `config`

The checker process returns JSON with:

- `status`
- `score`
- `execution_time_ms`
- `memory_used_kb`
- `timedOut`
- `report`

`report` is validated as the existing `CheckReport` schema and then enriched
with sandbox metadata such as container image, container name, exit code,
duration, and timeout flags.

Adapted from source: invalid sandbox reports now force `CheckStatus.ERROR` and
`score = 0`. The source code created an error-shaped report but could preserve a
successful status from malformed sandbox JSON.

Supported `TaskCheckSpec.config_json` contracts:

- `tests`: `entry_file`, `test_file`, `test_code`, `visible`
- `lint`: `entry_file`, `select`, `ignore`, `line_length`
- `static`: `forbidden_imports`, `forbidden_calls`, `required_symbols`
- `architecture`: `required_classes`, `required_methods`,
  `forbidden_functions`, `max_function_length`

## Sandbox Notes

`DockerSandboxExecutor` runs the checker image with:

- no network
- read-only root filesystem
- tmpfs `/tmp`
- tmpfs `/workspace`
- no bind mounts
- no Docker socket mount
- dropped capabilities
- `no-new-privileges`
- non-root user `10001:10001` by default

User code is sent through stdin JSON and written only inside the checker
container workspace. Unit tests use `InProcessSandboxExecutor`, which switches
into a temporary directory before invoking `legacy_checker.checks.run_check()`.

The standalone `legacy_checker` package handles pytest, Ruff lint, AST static
rules, and AST architecture rules. Generated `legacy_checker/__pycache__` files
were not ported; a test-created cache directory was removed, and root
`.gitignore` now ignores nested `__pycache__/` and `*.pyc`.

## Docker Notes

Added `docker/checker.Dockerfile` for `legacy-trainer-checker:local`. The image
installs `pytest` and `ruff`, copies `legacy_checker` to `/opt/legacy_checker`,
sets `PYTHONPATH=/opt`, and runs `python -m legacy_checker.run`.

Adapted current `compose.yaml` instead of copying source
`docker/docker-compose.yml`:

- `sandbox-prep` still builds the legacy Python and C++ refactor runner images.
- `sandbox-prep` now also builds `legacy-trainer-checker:local`.
- `sandbox-prep` mounts only `./docker` and `./legacy_checker` read-only.
- backend keeps the current DinD `DOCKER_HOST=tcp://docker-daemon:2375` model.
- backend receives `CHECKER_*` settings beside existing `CHECK_DOCKER_*`
  settings.

Source `docker/docker-compose.yml` and `docker/.dockerignore` were not copied.
The current root `.dockerignore` applies when building
`docker/checker.Dockerfile` from the repository root.

## Tests

Ran:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_sandbox_executor.py backend\tests\test_sandboxed_runner.py backend\tests\test_sandbox_docker_integration.py
```

Result: `12 passed, 1 skipped, 3 warnings`.

Ran the prompt-required targeted check:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_sandboxed_runner.py backend\tests\test_submissions_api.py
```

Result: `31 passed, 64 warnings`.

Ran the full backend suite:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Result: `81 passed, 1 skipped, 79 warnings`.

Docker was available, so the checker image and opt-in Docker integration test
were also run:

```powershell
docker build -f docker/checker.Dockerfile -t legacy-trainer-checker:local .
$env:LEGACY_TRAINER_RUN_DOCKER_SANDBOX_TESTS='1'; .\.venv\Scripts\python.exe -m pytest backend\tests\test_sandbox_docker_integration.py
```

Result: image build succeeded; Docker integration test result: `1 passed`.

Compose and whitespace checks:

```powershell
docker compose -f compose.yaml config
git diff --check
```

Result: compose config succeeded; `git diff --check` reported no whitespace
errors, only Windows line-ending warnings.

Warnings are existing JWT `InsecureKeyLengthWarning` warnings from the test
secret unless noted otherwise.

## Skipped Source Changes

Not ported in this window:

- source `docker/docker-compose.yml` host-socket Docker setup
- source `docker/.dockerignore` as a separate compose-context file
- source `backend/requirements.txt` addition of runtime `pytest` and `ruff`;
  this port keeps them in the checker image and adds `ruff` to
  `backend/requirements-dev.txt` for in-process unit tests
- source progress/history endpoint and scoring changes from later windows
- source frontend changes
- generated `legacy_checker/__pycache__` files

## Risks / Follow-up

- Real `TaskCheckSpec` runners are Python-only. C++ remains supported through
  the preserved legacy `RefactorCheckPipeline`.
- Pytest `test_code` can represent hidden tests. Current reports include
  stdout/stderr artifacts, so frontend/API filtering should be reviewed before
  exposing hidden-test output broadly.
- The production default sandbox executor is Docker-only. Local non-Docker
  execution exists only as a test fake.
- The checker image is built by `sandbox-prep`; deployments that do not run
  compose prep need to build/publish `legacy-trainer-checker:local` or point
  `CHECKER_SANDBOX_IMAGE` at a published image.
- Progress/history semantics are intentionally still from the current branch
  and should be handled in the next port window.
