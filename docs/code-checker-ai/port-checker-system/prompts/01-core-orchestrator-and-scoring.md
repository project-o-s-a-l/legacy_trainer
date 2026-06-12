# Prompt 01 - Core Orchestrator and Weighted Scoring

Ты работаешь в репозитории `D:\Projects\legacy_trainer`.

Текущая ветка должна быть `feature/backend/checker`. Source branch: `codex/phase-01-contracts-persistence`.

Твоя задача - перенести core checking orchestration и weighted scoring из source branch в текущую ветку, адаптировав под уже существующую архитектуру. Не переноси Docker sandbox и real runners в этом окне, если для этого требуется большой отдельный пласт изменений.

## Перед началом

Выполни:

```powershell
git status --short --branch
git branch -a --verbose --no-abbrev
```

Прочитай отчет окна 00, если он существует:

- `docs/code-checker-ai/reports/checker-system-port-00-audit-plan.md`

Если отчета нет, сначала прочитай:

- `docs/code-checker-ai/port-checker-system/README.md`
- `docs/code-checker-ai/reports/phase-01-port-from-codex-branch.md`

## Обязательный контекст текущей ветки

Прочитай:

- `backend/app/services/submission.py`
- `backend/app/services/refactor_checks/pipeline.py`
- `backend/app/services/refactor_checks/models.py`
- `backend/app/services/refactor_checks/task_definition.py`
- `backend/app/models/task.py`
- `backend/app/models/task_check_spec.py`
- `backend/app/models/task_check_rule.py`
- `backend/app/models/task_scenario.py`
- `backend/app/repositories/task.py`
- `backend/app/repositories/submission.py`
- `backend/app/schemas/check.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_refactor_submission_api.py`
- `backend/tests/test_task_check_specs.py`

## Обязательный контекст source branch

Изучи через `git show`:

- `backend/app/services/submission.py`
- `backend/app/services/checking/__init__.py`
- `backend/app/services/checking/types.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/fake_runner.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_task_check_specs.py`

## Цель переноса

Нужно добавить или адаптировать:

- `backend/app/services/checking/types.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/fake_runner.py`
- `backend/app/services/checking/__init__.py`
- подключение orchestrator в `SubmissionService`;
- weighted scoring по `TaskCheckSpec.weight`;
- `is_required` для статуса submission;
- сохранение нескольких `SubmissionCheck`;
- частичные итоговые баллы, если часть checks провалилась, когда это соответствует rules.

## Важная адаптация под текущую ветку

В текущей ветке уже есть `RefactorCheckPipeline`. Не удаляй его.

Выбери один из безопасных вариантов и объясни в отчете:

1. `TaskCheckSpec` orchestrator становится основным, а `RefactorCheckPipeline` остается fallback, если у задачи нет `check_specs`.
2. `RefactorCheckPipeline` оборачивается в runner/adapter внутри нового orchestrator.
3. На этом шаге подключается только fake runner для `TaskCheckSpec`, а refactor pipeline остается текущим путем до окна 02/03.

Не оставляй две конкурирующие активные системы, которые одновременно создают дублирующие checks для одной submission без ясного правила выбора.

## Scoring behavior

Source branch считает:

```text
sum(check.score * check.weight) / sum(check.weight)
```

Текущая ветка считает raw pipeline score, но потом делает:

```python
submission.score = raw_score if submission.status == SubmissionStatus.PASSED else 0
```

Это мешает частичным баллам. Нужно заменить на осознанное правило:

- если продуктово нужны частичные баллы, сохранять aggregated score даже при `FAILED`;
- если `ERROR`, обычно score должен быть `0` или score только по успешно выполненным optional checks - решение зафиксировать в отчете.

## Тесты

Адаптируй или добавь backend tests, которые проверяют:

- задача без `TaskCheckSpec` не ломает текущий fallback/refactor flow;
- задача с несколькими `TaskCheckSpec` создает несколько `SubmissionCheck`;
- weighted score может быть 75 при optional failed check;
- required failed check дает статус `failed`;
- optional failed check не обязательно валит submission;
- старые tests `test_submissions_api.py`, `test_refactor_submission_api.py`, `test_task_check_specs.py` проходят.

Можно временно использовать fake runner, если real runners переносятся в следующем окне.

## Проверки

Минимум:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_task_check_specs.py backend\tests\test_submissions_api.py backend\tests\test_refactor_submission_api.py
.\.venv\Scripts\python.exe -m pytest backend\tests
```

## Отчет

Создай:

`docs/code-checker-ai/reports/checker-system-port-01-core-orchestrator-scoring.md`

Структура:

```markdown
# Checker System Port 01 - Core Orchestrator and Scoring

## Summary

## Files Compared

## Files Changed

## Architecture Decision

## Scoring Rules

## Compatibility With Refactor Pipeline

## Tests

## Skipped Source Changes

## Risks / Follow-up
```
