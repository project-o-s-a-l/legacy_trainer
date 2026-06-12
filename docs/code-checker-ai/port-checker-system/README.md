# Porting Checker System From `codex/phase-01-contracts-persistence`

Эта папка содержит материалы и промпты для последовательного переноса системы проверки и оценивания кода из ветки `codex/phase-01-contracts-persistence` в текущую ветку `feature/backend/checker`.

Перенос нужно делать в несколько независимых контекстных окон. Не делайте слепой `merge` всей ветки: source branch содержит не только backend checker, но и docker/frontend/docs/infra изменения, часть которых может конфликтовать с текущей архитектурой.

## Текущее состояние ветки

В текущей ветке уже есть:

- `backend/app/services/refactor_checks/` - рабочий pipeline для refactoring checks.
- `TaskScenario` и `TaskCheckRule` - текущие модели конфигурации refactor checks.
- `SubmissionService` вызывает `RefactorCheckPipeline`, а если правил нет, использует legacy fallback `_evaluate_code`.
- `SubmissionCheckType` уже содержит `tests`, `lint`, `static`, `architecture`.
- После phase-01 port уже добавлены `TaskCheckSpec`, `Task.check_specs`, `backend/app/schemas/check.py` и тесты persistence/contracts.

Главная проблема текущего оценивания: если pipeline вернул статус не `PASSED`, `SubmissionService` обнуляет общий `submission.score`, даже если часть checks дала частичные баллы.

## Что лучше в source branch

В `codex/phase-01-contracts-persistence` реализованы:

- `backend/app/services/checking/CheckOrchestrator`;
- `TaskCheckSpec`-based checks;
- runner contracts `CheckContext`, `CheckRunResult`, `CheckOrchestrationResult`;
- default runners для `tests`, `lint`, `static`, `architecture`;
- sandboxed execution;
- weighted scoring по `TaskCheckSpec.weight`;
- `is_required`, позволяющий optional checks падать без failed submission;
- tests для pytest/lint/static/architecture, weighted score и progress.

## Рекомендуемая последовательность окон

1. `prompts/00-audit-and-integration-plan.md`
   - Ничего не переносит или делает только docs/report.
   - Сравнивает обе ветки и пишет детальный integration plan.

2. `prompts/01-core-orchestrator-and-scoring.md`
   - Переносит contracts/orchestrator/fake runner и подключает weighted scoring.
   - Не переносит Docker sandbox и real runners, если это выходит за рамку окна.

3. `prompts/02-sandbox-and-real-runners.md`
   - Переносит sandbox, Docker runner и реальные Python checks.
   - Адаптирует tests под текущую ветку.

4. `prompts/03-progress-history-and-final-verification.md`
   - Доводит progress/history/scoring API, проверяет совместимость frontend/API.
   - Делает финальную верификацию и отчет.

Если после окна 00 окажется, что перенос можно безопасно сделать в меньшее число окон, агент может объединить окна 01-02 только при явном понимании конфликтов и после фиксации плана.

## Общие правила для всех окон

- Перед работой выполнить:
  - `git status --short --branch`
  - `git branch -a --verbose --no-abbrev`
- Убедиться, что текущая ветка - `feature/backend/checker`.
- Убедиться, что source branch `codex/phase-01-contracts-persistence` есть локально или как remote branch.
- Не переключаться на source branch без необходимости; использовать `git show`, `git diff`, `git ls-tree`, либо временный worktree.
- Не откатывать чужие незакоммиченные изменения.
- Не удалять текущие `refactor_checks`, `TaskScenario`, `TaskCheckRule` без отдельного решения и объяснения в отчете.
- После каждого окна создать отчет в `docs/code-checker-ai/reports/`.
- Минимальная backend-проверка после кодовых изменений:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Если меняются frontend контракты:

```powershell
npm run test:run
npm run lint
npm run build
```
