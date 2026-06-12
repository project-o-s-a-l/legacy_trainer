# Phase 01 Port Report

## Source Branch

`codex/phase-01-contracts-persistence`

## Summary

Ported the phase-01 foundation for code checking into the current `feature/backend/checker` branch without merging the whole source branch.

The current branch already has a `RefactorCheckPipeline` based on `TaskScenario` and `TaskCheckRule`, so the port keeps that implementation intact and adds the missing `TaskCheckSpec` persistence/contracts beside it. This gives later phases a stable check-spec table and report contract without replacing the existing checking flow.

## Files Compared

- `README.md`
- `docs/code-checker-ai/README.md` from source branch; missing in current branch before this port.
- `docs/code-checker-ai/reports/phase-01-contracts-and-persistence.md` from source branch.
- `docs/code-checker-ai/prompts/phase-01-contracts-and-persistence.md` from source branch.
- `backend/app/services/submission.py`
- `backend/app/db/enums.py`
- `backend/app/models/task.py`
- `backend/app/models/submission_check.py`
- `backend/app/models/task_check_spec.py` from source branch.
- `backend/app/models/__init__.py`
- `backend/app/repositories/task.py`
- `backend/app/repositories/task_check_spec.py` lookup: not present in source branch.
- `backend/app/schemas/check.py` from source branch.
- `backend/app/schemas/submission.py`
- `backend/app/services/checking/` from source branch.
- `backend/app/services/refactor_checks/` from current branch.
- `backend/tests/test_task_check_specs.py` from source branch.
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_tasks_api.py`

## Files Changed

- `backend/app/models/task_check_spec.py` - added `TaskCheckSpec`.
- `backend/app/models/task.py` - added `Task.check_specs` while keeping `scenarios` and `check_rules`.
- `backend/app/models/__init__.py` - registered `TaskCheckSpec`.
- `backend/models.py` - exported `TaskCheckSpec` so `Base.metadata.create_all` sees it in tests/init.
- `backend/app/repositories/task.py` - preloads `check_specs`; added `create_check_spec` and `list_check_specs_by_task_id`.
- `backend/app/schemas/check.py` - added phase-01 check spec and result/report contracts.
- `backend/app/services/submission.py` - legacy fallback report now serializes through `CheckReport`.
- `backend/tests/test_task_check_specs.py` - added adapted persistence/contracts tests.
- `docs/code-checker-ai/README.md` - added minimal code-checker context for this branch.
- `docs/code-checker-ai/REPORT_TEMPLATE.md` - added report template.
- `docs/code-checker-ai/prompts/phase-01-contracts-and-persistence.md` - added phase-01 prompt.
- `docs/code-checker-ai/reports/phase-01-contracts-and-persistence.md` - added phase-01 report.
- `docs/code-checker-ai/reports/phase-01-port-from-codex-branch.md` - this port report.

## Adaptation Notes

- Current `SubmissionCheckType` already had `TESTS`, `LINT`, `STATIC`, and `ARCHITECTURE`; no enum values were changed.
- Current branch already had `TaskScenario` and `TaskCheckRule`; they were preserved and no parallel replacement of `RefactorCheckPipeline` was introduced.
- Source branch's phase-01 repository methods lived in `TaskRepository`; there was no separate `task_check_spec.py` repository file to port.
- The fallback heuristic submit path now stores `errors`, `summary`, `metrics`, and JSON-safe detail statuses while preserving existing `total`, `passed`, `failed`, and `details` fields.
- Source docs were reduced to phase-01-relevant files instead of copying all later phase reports/prompts.

## Skipped Changes

- `backend/app/services/checking/` runner/orchestrator/sandbox code from source branch was not ported because it belongs to later phases and would conflict with the current branch's `refactor_checks` pipeline.
- Source branch deletions of `TaskScenario`, `TaskCheckRule`, and `refactor_checks` were not ported because those are active current-branch architecture.
- Frontend changes from source branch were not ported because phase-01 did not require frontend/API contract changes.
- Docker, sandbox image, cert, and compose changes from source branch were not ported because they are outside phase-01 persistence/contracts.
- Later source tests for pytest/lint/static/architecture runners were not ported because the current branch does not use that orchestrator.

## Tests

- `.\.venv\Scripts\python.exe -m pytest backend\tests\test_task_check_specs.py` -> 2 passed.
- `.\.venv\Scripts\python.exe -m pytest backend\tests\test_submissions_api.py backend\tests\test_tasks_api.py` -> 16 passed, 23 warnings.
- `.\.venv\Scripts\python.exe -m pytest backend\tests` -> 56 passed, 38 warnings.

Warnings are the existing short test JWT secret `InsecureKeyLengthWarning`.

## Risks / Follow-up

- The branch now has both `TaskCheckSpec` and the older `TaskScenario`/`TaskCheckRule` model family. A later phase should define the migration/mapping path before enabling a second live orchestrator.
- No Alembic migration was added; this follows the current `Base.metadata.create_all` workflow.
- Existing production data will need seed/migration planning before `TaskCheckSpec` is used outside tests.
