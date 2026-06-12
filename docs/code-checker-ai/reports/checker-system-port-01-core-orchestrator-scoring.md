# Checker System Port 01 - Core Orchestrator and Scoring

## Summary

Ported the core `TaskCheckSpec` checking orchestration layer into the current
`feature/backend/checker` branch without merging
`codex/phase-01-contracts-persistence` wholesale.

This window adds shared checking contracts, a deterministic fake runner, a
weighted-score orchestrator, and `SubmissionService` integration. The service
now persists every check result from the selected path and preserves partial
submission scores instead of zeroing failed submissions.

## Files Compared

Current branch context:

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

Source branch context via `git show codex/phase-01-contracts-persistence:<path>`:

- `backend/app/services/submission.py`
- `backend/app/services/checking/__init__.py`
- `backend/app/services/checking/types.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/fake_runner.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_task_check_specs.py`

## Files Changed

- Added `backend/app/services/checking/types.py`
- Added `backend/app/services/checking/orchestrator.py`
- Added `backend/app/services/checking/fake_runner.py`
- Added `backend/app/services/checking/__init__.py`
- Updated `backend/app/services/submission.py`
- Updated `backend/tests/test_submissions_api.py`
- Added this report

Pre-existing uncommitted phase-01 files from the prior window were left intact:
`TaskCheckSpec`, `backend/app/schemas/check.py`, repository/model wiring, and
`backend/tests/test_task_check_specs.py`.

## Architecture Decision

Selected option 1 from the prompt:

`TaskCheckSpec` orchestration is the primary path when `task.check_specs` is
present. If a task has no `check_specs`, `SubmissionService` falls back to the
existing `RefactorCheckPipeline`. If the refactor pipeline has no scenarios or
rules, the service uses the deterministic no-spec tests fallback.

This keeps one active checker path per submission:

1. `TaskCheckSpec` orchestrator
2. Legacy `RefactorCheckPipeline`
3. No-spec deterministic tests fallback

The source branch's `with_default_runners()` imported real Python runners and
sandbox code. In this window it intentionally resolves to fake runners only, so
Docker sandbox and real runner work remains isolated for a later window.

## Scoring Rules

For `TaskCheckSpec` checks, orchestration score is:

```text
int(sum(check.score * check.weight) / sum(check.weight))
```

Only checks with `weight > 0` participate. Status aggregation follows the
source behavior: only required checks can fail or error the submission.
Optional failed checks can reduce score without making the submission failed.

Partial scores are now preserved on `FAILED` submissions. The previous
`submission.score = raw_score if status == PASSED else 0` rule was removed.

For `ERROR`, this window keeps the same aggregate-score rule as the source
orchestrator: error checks normally score `0`, while any successful weighted
optional checks can still contribute. This should be revisited when real
sandbox errors are ported and product-visible error scoring is finalized.

Progress totals were not fully migrated in this window. Current progress
behavior still counts solved/passed best submissions for `User.total_score`,
while best-submission selection already uses the stored score.

## Compatibility With Refactor Pipeline

`RefactorCheckPipeline`, `TaskScenario`, `TaskCheckRule`, and C++ refactor
coverage were preserved.

When the legacy pipeline runs, its `PipelineResult` is adapted into the same
internal `CheckOrchestrationResult` shape used by the new orchestrator. Each
legacy `CheckOutcome` is normalized into a `CheckReport` shape with:

- `total`, `passed`, `failed`, `errors`
- `summary`
- `details`
- `metrics.runner = "refactor_pipeline"`
- `artifacts.legacy_report` preserving the original report payload

The legacy pipeline remains required-only for status purposes because its
current rule model has no `is_required` field.

## Tests

Ran the prompt's required checks:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_task_check_specs.py backend\tests\test_submissions_api.py backend\tests\test_refactor_submission_api.py
```

Result: `17 passed, 37 warnings`.

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Result: `59 passed, 46 warnings`.

Warnings are existing JWT `InsecureKeyLengthWarning` warnings from the test
secret.

Added or updated coverage for:

- no-spec fallback preserving partial failed score
- multiple `TaskCheckSpec` rows creating multiple `SubmissionCheck` rows
- weighted score of `75` with an optional failed check
- required failed check setting submission status to `failed`
- optional failed check not failing the submission
- existing refactor pipeline API tests

## Skipped Source Changes

Not ported in this window:

- Docker sandbox executor
- `SandboxedCheckRunner`
- real Python pytest, Ruff lint, static, and architecture runners
- `legacy_checker`
- Docker image and compose rewrites
- frontend result/history UI changes
- `GET /api/v1/submissions?taskId=...`
- source `UserProgressService.record_submission()` and full progress/history
  semantics
- generated `legacy_checker/__pycache__`

## Risks / Follow-up

- Fake runner behavior is intentionally temporary for `TaskCheckSpec` checks.
  Real runners must replace it in the sandbox/runner window.
- Error scoring should be revisited once sandbox errors are real and product
  semantics are decided.
- `User.total_score` still follows current solved/passed-only semantics. A
  later progress/history window should decide whether partial best scores count
  globally.
- Hidden pytest test code and runner artifacts need report filtering before
  frontend-facing real runner output is exposed.
- The current working tree remains dirty with pre-existing phase-01 changes;
  those were not reverted or merged blindly.
