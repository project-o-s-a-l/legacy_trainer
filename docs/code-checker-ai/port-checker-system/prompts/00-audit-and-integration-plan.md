# Prompt 00 - Audit and Integration Plan

Ты работаешь в репозитории `D:\Projects\legacy_trainer`.

Текущая ветка должна быть `feature/backend/checker`. Source branch: `codex/phase-01-contracts-persistence`.

Твоя задача в этом окне - подготовить детальный план переноса системы проверки и оценивания кода из source branch в текущую ветку. Не делай слепой merge всей ветки. Кодовые изменения в этом окне допустимы только для отчета/документации; основная цель - сравнение и план.

## Перед началом

Выполни:

```powershell
git status --short --branch
git branch -a --verbose --no-abbrev
git diff --name-status HEAD..codex/phase-01-contracts-persistence
git ls-tree -r --name-only codex/phase-01-contracts-persistence
```

Если есть незакоммиченные изменения, не затирай и не откатывай их.

## Обязательный контекст текущей ветки

Прочитай:

- `docs/code-checker-ai/port-checker-system/README.md`
- `docs/code-checker-ai/reports/phase-01-port-from-codex-branch.md`
- `backend/app/services/submission.py`
- `backend/app/services/refactor_checks/`
- `backend/app/models/task.py`
- `backend/app/models/task_check_spec.py`
- `backend/app/models/task_check_rule.py`
- `backend/app/models/task_scenario.py`
- `backend/app/repositories/task.py`
- `backend/app/repositories/task_check_rule.py`
- `backend/app/repositories/task_scenario.py`
- `backend/app/schemas/check.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_refactor_submission_api.py`
- `backend/tests/test_task_check_specs.py`

## Обязательный контекст source branch

Используй `git show`/`git diff`, не переключайся на ветку.

Особенно изучи:

- `backend/app/services/submission.py`
- `backend/app/services/checking/__init__.py`
- `backend/app/services/checking/types.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/fake_runner.py`
- `backend/app/services/checking/sandbox.py`
- `backend/app/services/checking/sandboxed_runner.py`
- `backend/app/services/checking/python_pytest_runner.py`
- `backend/app/services/checking/python_lint_runner.py`
- `backend/app/services/checking/python_static_runner.py`
- `backend/app/repositories/task.py`
- `backend/app/repositories/submission.py`
- `backend/app/services/user_progress.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_sandbox*.py`
- `backend/tests/sandbox_fakes.py`
- `docker/checker.Dockerfile`
- `docker/docker-compose.yml`
- `docs/code-checker-ai/reports/phase-02-orchestrator-fake-runner.md`
- `docs/code-checker-ai/reports/phase-03-python-pytest-runner.md`
- `docs/code-checker-ai/reports/phase-04-lint-static-architecture.md`
- `docs/code-checker-ai/reports/phase-05-scoring-progress-history.md`

## Что нужно выяснить

1. Какие части source branch относятся к core checking/scoring, а какие к docker/frontend/docs/infra.
2. Как лучше состыковать `TaskCheckSpec`-based orchestrator с текущими `TaskScenario`/`TaskCheckRule`.
3. Нужно ли сохранить `RefactorCheckPipeline` как fallback/adapter/legacy path.
4. Какие тесты из source branch можно перенести напрямую, а какие нужно адаптировать.
5. Какие изменения потребуются в `SubmissionService`, чтобы:
   - запускать checks через orchestrator;
   - сохранять несколько `SubmissionCheck`;
   - считать weighted score;
   - не обнулять частичные баллы без продуктовой причины;
   - сохранить текущий публичный API.
6. Какие Docker/sandbox изменения нужны для реальных runner-ов.
7. Какие риски есть для frontend и progress.

## Выходной результат

Создай отчет:

`docs/code-checker-ai/reports/checker-system-port-00-audit-plan.md`

Структура:

```markdown
# Checker System Port 00 - Audit and Integration Plan

## Source Branch

## Current Branch Summary

## Source Branch Summary

## Architecture Decision

## Files Compared

## Proposed Port Plan

## Window Breakdown

## Tests To Reuse / Adapt

## Risks

## Explicit Non-Goals
```

## Проверки

Если менял только docs, тесты можно не запускать. Если менял код, минимум:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```
