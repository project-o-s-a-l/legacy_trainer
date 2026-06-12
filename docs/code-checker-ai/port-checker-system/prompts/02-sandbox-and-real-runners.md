# Prompt 02 - Sandbox and Real Python Runners

Ты работаешь в репозитории `D:\Projects\legacy_trainer`.

Текущая ветка должна быть `feature/backend/checker`. Source branch: `codex/phase-01-contracts-persistence`.

Твоя задача - перенести и адаптировать sandboxed real runners для проверки кода: pytest, lint, static, architecture. Окно 01 должно уже перенести core orchestrator/scoring. Если этого нет, сначала оцени, можно ли сделать минимальную интеграцию без поломки текущего pipeline; если нельзя, остановись с отчетом о блокере.

## Перед началом

Выполни:

```powershell
git status --short --branch
git branch -a --verbose --no-abbrev
```

Прочитай:

- `docs/code-checker-ai/port-checker-system/README.md`
- `docs/code-checker-ai/reports/checker-system-port-00-audit-plan.md`, если есть
- `docs/code-checker-ai/reports/checker-system-port-01-core-orchestrator-scoring.md`, если есть

## Обязательный контекст текущей ветки

Прочитай:

- `backend/app/core/config.py`
- `backend/app/services/submission.py`
- `backend/app/services/checking/`, если уже появился после окна 01
- `backend/app/services/refactor_checks/`
- `backend/tests/conftest.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_refactor_submission_api.py`
- `docker/`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`, если есть

## Обязательный контекст source branch

Изучи через `git show`:

- `backend/app/services/checking/sandbox.py`
- `backend/app/services/checking/sandboxed_runner.py`
- `backend/app/services/checking/python_pytest_runner.py`
- `backend/app/services/checking/python_lint_runner.py`
- `backend/app/services/checking/python_static_runner.py`
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

## Цель переноса

Нужно перенести/adapt:

- `SandboxExecutionRequest` / `SandboxExecutionResult`;
- Docker/local sandbox executor;
- `SandboxedCheckRunner`;
- Python pytest runner;
- Python lint runner;
- Python static runner;
- Python architecture runner;
- test fakes for sandbox;
- relevant requirements/config;
- docker checker image if tests/runtime depend on it.

## Важные ограничения

- Не ломай текущие `refactor_checks` tests.
- Не требуй Docker для всего backend suite. Docker integration tests должны быть skip-able, если Docker недоступен.
- Если source branch использует Docker Compose структуру, адаптируй ее под текущую `docker/` структуру, не удаляя рабочие файлы без необходимости.
- Не переносить frontend изменения в этом окне.
- Не хранить небезопасный пользовательский код вне sandbox/temp workspace.

## Тесты

Адаптируй или добавь tests:

- sandbox request/result serialization;
- sandboxed runner handles config error, timeout, non-json output, invalid report;
- pytest success/failure/timeout/config error;
- lint success/failure;
- static success/failure;
- architecture success/failure;
- multi-check task with checks order;
- backend suite remains green.

Если Docker недоступен, unit tests через `sandbox_fakes.py` должны покрывать runner behavior.

## Проверки

Минимум:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_sandboxed_runner.py backend\tests\test_submissions_api.py
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Если Docker доступен и перенесен Docker executor:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_sandbox_docker_integration.py
```

Если изменены docker files, по возможности:

```powershell
docker compose -f docker\docker-compose.yml config
```

## Отчет

Создай:

`docs/code-checker-ai/reports/checker-system-port-02-sandbox-real-runners.md`

Структура:

```markdown
# Checker System Port 02 - Sandbox and Real Runners

## Summary

## Files Compared

## Files Changed

## Runner Contracts

## Sandbox Notes

## Docker Notes

## Tests

## Skipped Source Changes

## Risks / Follow-up
```
