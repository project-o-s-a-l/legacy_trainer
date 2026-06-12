# Prompt 03 - Progress, History, API Compatibility and Final Verification

Ты работаешь в репозитории `D:\Projects\legacy_trainer`.

Текущая ветка должна быть `feature/backend/checker`. Source branch: `codex/phase-01-contracts-persistence`.

Твоя задача - довести перенос системы проверки и оценивания до стабильного состояния: progress/history, API compatibility, документация и финальная верификация. Окна 01 и 02 должны уже перенести core orchestrator/scoring и real runners. Если этого нет, сначала зафиксируй, что именно отсутствует, и адаптируй объем работы.

## Перед началом

Выполни:

```powershell
git status --short --branch
git branch -a --verbose --no-abbrev
```

Прочитай отчеты, если они существуют:

- `docs/code-checker-ai/reports/checker-system-port-00-audit-plan.md`
- `docs/code-checker-ai/reports/checker-system-port-01-core-orchestrator-scoring.md`
- `docs/code-checker-ai/reports/checker-system-port-02-sandbox-real-runners.md`
- `docs/code-checker-ai/reports/phase-01-port-from-codex-branch.md`

## Обязательный контекст текущей ветки

Прочитай:

- `backend/app/services/submission.py`
- `backend/app/services/user_progress.py`
- `backend/app/repositories/user_progress.py`
- `backend/app/repositories/submission.py`
- `backend/app/api/v1/submissions.py`
- `backend/app/schemas/submission.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_user_progress_api.py`
- `backend/tests/test_refactor_submission_api.py`
- frontend API call sites if response shape changes:
  - `frontend/src/features/CheckSolution/CheckSolution.ts`
  - `frontend/src/features/getScoreForSolution/getScoreForSolution.ts`
  - `frontend/src/pages/SolutionResultPage/SolutionResult.tsx`

## Обязательный контекст source branch

Изучи через `git show`:

- `backend/app/services/user_progress.py`
- `backend/app/repositories/user_progress.py`
- `backend/app/repositories/submission.py`
- `backend/app/api/v1/submissions.py`
- `backend/app/schemas/submission.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_user_progress_api.py`
- frontend changes only if backend API response shape changed.

## Цель

Нужно убедиться, что новая система проверки:

- корректно записывает `Submission.status`, `Submission.score`, `checked_at`, memory/time;
- сохраняет все `SubmissionCheck`;
- корректно пересчитывает `UserTaskProgress`;
- выбирает best submission по score/status осознанно;
- обновляет `User.total_score` из best submissions;
- поддерживает submission history endpoint, если он есть в source branch и нужен текущей ветке;
- не ломает текущий frontend API contract без отдельного frontend patch;
- имеет понятную документацию по scoring.

## Scoring acceptance criteria

Зафиксируй и проверь тестами:

- full pass может дать 100 при `task.max_score=100`;
- partial pass может дать не 0 и не 100, например 50 или 75;
- required failed check влияет на `status`;
- optional failed check влияет на `score`, но может не валить `status`;
- progress сохраняет best submission не только при `PASSED`, если продуктово нужны частичные баллы;
- total score пересчитывается из best submissions.

Если текущий продуктовый контракт требует, чтобы failed submission всегда давал 0, явно зафиксируй это как решение и объясни, почему weighted scoring ограничен.

## Frontend

Если backend response shape не меняется, frontend tests можно не запускать.

Если меняешь:

- `SubmissionCreateResponse`;
- `SubmissionCheckResponse`;
- path/query params;
- формат `report`;
- history endpoint;

то обнови frontend mocks/types/tests и запусти:

```powershell
npm run test:run
npm run lint
npm run build
```

## Проверки

Минимум:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Если frontend/API изменены:

```powershell
npm run test:run
npm run lint
npm run build
```

Также проверь:

```powershell
git diff --check
```

## Финальный отчет

Создай:

`docs/code-checker-ai/reports/checker-system-port-final-verification.md`

Структура:

```markdown
# Checker System Port - Final Verification

## Summary

## Final Architecture

## Scoring Behavior

## Progress Behavior

## API Compatibility

## Files Changed Across Port

## Tests

## Known Gaps

## Operational Notes

## Recommended Next Steps
```
