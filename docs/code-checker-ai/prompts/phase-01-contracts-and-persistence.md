# Prompt - Phase 01: Contracts and Persistence

Work only on phase 01 of the code checking implementation: formalize check contracts and persistence for task check specs.

## Required Context

Before editing, read:

- `README.md`
- `docs/code-checker-ai/README.md`
- all files in `docs/code-checker-ai/reports/`
- `backend/app/services/submission.py`
- `backend/app/db/enums.py`
- `backend/app/models/task.py`
- `backend/app/models/submission_check.py`
- `backend/app/schemas/submission.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_tasks_api.py`

## Phase Goal

Prepare backend contracts for multiple check types without implementing real code execution.

Add or refine:

- a table/model for task check specs, for example `TaskCheckSpec`;
- `Task -> check_specs`;
- repository methods for task check specs;
- Pydantic/dataclass contracts for internal check results;
- a clear `report_json` format compatible with future tests/lint/static/architecture checks;
- tests for creating and reading check specs.

## Recommended TaskCheckSpec Contract

Use these fields unless there is a good local reason to adapt them:

- `id`
- `task_id`
- `check_type` from `SubmissionCheckType`
- `name`
- `weight`
- `timeout_seconds`
- `is_required`
- `order`
- `config_json`

## Constraints

- Do not implement real pytest/lint runners in this phase.
- Do not break `/api/v1/tasks/{task_id}/submit`.
- Do not change frontend.
- Do not add Alembic unless the migration workflow is fully introduced. The project currently relies on `Base.metadata.create_all`.
- Keep existing backend tests compatible.

## Checks

Run at minimum:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

## Report

Create:

`docs/code-checker-ai/reports/phase-01-contracts-and-persistence.md`
