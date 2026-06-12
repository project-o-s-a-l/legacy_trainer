# Phase 01 - Contracts and Persistence

## Phase

- Number: 01
- Name: Contracts and Persistence
- Date: 2026-06-11
- Agent: Codex

## Summary

Added backend persistence for task check specs and formal Pydantic contracts for check results. Real pytest/lint/static/architecture execution is intentionally outside this phase.

For this port, the current branch keeps its existing `RefactorCheckPipeline` and legacy heuristic fallback. `TaskCheckSpec` is added as a foundation for later orchestration without replacing `TaskScenario` or `TaskCheckRule`.

## Files Changed

- `backend/app/models/task_check_spec.py` - SQLAlchemy model `TaskCheckSpec`.
- `backend/app/models/task.py` - `Task.check_specs` relationship.
- `backend/app/models/__init__.py` and `backend/models.py` - model registration for `Base.metadata.create_all`.
- `backend/app/repositories/task.py` - methods for creating and listing check specs; task loading preloads `check_specs`.
- `backend/app/schemas/check.py` - internal contracts `TaskCheckSpecContract`, `CheckReport`, `CheckReportDetail`, `InternalCheckResult`.
- `backend/app/services/submission.py` - legacy fallback report now uses the shared `CheckReport` shape.
- `backend/tests/test_task_check_specs.py` - persistence and contract serialization tests.

## Decisions

Final `TaskCheckSpec` format:

- `id`
- `task_id`
- `check_type`
- `name`
- `weight`
- `timeout_seconds`
- `is_required`
- `order`
- `config_json`

`SubmissionCheck.report_json` is expected to support:

```json
{
  "total": 0,
  "passed": 0,
  "failed": 0,
  "errors": 0,
  "summary": null,
  "details": [],
  "metrics": {},
  "artifacts": {}
}
```

Top-level `total`, `passed`, `failed` and `details` are preserved for compatibility with existing backend/frontend expectations.

## Tests

See `phase-01-port-from-codex-branch.md` for the test results from this port.

## Known Gaps

- Real pytest/lint/static/architecture runners are not added by this phase.
- The current branch's `RefactorCheckPipeline` is not replaced.
- No seed/default check specs are added.
- No Alembic migration workflow is added.
- Frontend is unchanged.

## Handoff to Next Phase

Entry points:

- `Task.check_specs`
- `TaskRepository.get_task_by_id(...)`
- `TaskRepository.list_check_specs_by_task_id(task_id)`
- `TaskRepository.create_check_spec(...)`
- `backend/app/schemas/check.py`

Future work should decide how `TaskCheckSpec` maps to or supersedes the existing `TaskScenario`/`TaskCheckRule` pipeline before introducing a second active orchestration path.
