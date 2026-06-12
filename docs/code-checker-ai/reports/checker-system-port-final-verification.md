# Checker System Port - Final Verification

## Summary

Completed the final progress/history/API compatibility window for the checker
system port on `feature/backend/checker`, using
`codex/phase-01-contracts-persistence` only as source context and without a
blind merge.

The port now has:

- `TaskCheckSpec` persistence and report contracts.
- A primary `TaskCheckSpec` checking orchestrator with weighted scoring.
- Real sandboxed Python runners for tests, lint, static, and architecture
  checks.
- Preserved legacy `RefactorCheckPipeline` support for existing
  `TaskScenario` / `TaskCheckRule` tasks, including C++ refactor checks.
- Progress tracking that records all attempts, keeps best submissions by
  score/status, and recalculates `User.total_score` from best submissions.
- Submission history through `GET /api/v1/submissions?taskId=...`.

## Final Architecture

`SubmissionService` chooses one checker path per submission:

1. If `task.check_specs` exists, run `CheckOrchestrator.with_default_runners()`.
2. Otherwise, try the existing `RefactorCheckPipeline`.
3. If neither check specs nor legacy refactor definitions exist, run the
   deterministic no-spec tests fallback.

For every path, the service records:

- `Submission.status`
- `Submission.score`
- `Submission.checked_at`
- `Submission.memory_used_kb`
- `Submission.execution_time_ms`
- one `SubmissionCheck` per check result

The progress update is now delegated to `UserProgressService.record_submission()`
instead of being embedded in `SubmissionService`.

The history endpoint is implemented as:

- `GET /api/v1/submissions`
- optional query parameter `taskId`
- response model: `list[SubmissionResponse]`
- results filtered to the authenticated user and sorted by
  `submitted_at desc, id desc`

## Scoring Behavior

Weighted score for `TaskCheckSpec` checks is:

```text
int(sum(check.score * check.weight) / sum(check.weight))
```

Only checks with `weight > 0` participate in the score.

Status aggregation is requirement-aware:

- required `error` makes the submission `error`
- required `failed` makes the submission `failed`
- optional failed checks can reduce score without failing the submission
- if no required checks fail/error, the submission is `passed`

Partial scores are preserved even when the aggregate status is `failed`.
This is the selected product behavior for this port because progress and total
score now intentionally support partial credit.

Acceptance coverage now verifies:

- full pass gives `100` when `task.max_score=100`
- partial required test pass can give `33` or `50`
- optional failed check can produce `75` while status remains `passed`
- required failed check changes status to `failed`
- equal-score best submissions prefer better status
- total score is recalculated from best submissions

## Progress Behavior

`UserProgressService.record_submission()` now:

- creates progress on the first attempt, including failed/partial submissions
- increments `attempts_count` for every submission
- updates `last_submission_at` on every submission
- keeps `first_submission_at` from the first attempt
- chooses best submission by higher score, then better status on ties
- marks `is_solved` when `submission.score >= solved_threshold`
- keeps `is_solved` monotonic once true
- recalculates `User.total_score` as the sum of best submission scores

Solved threshold is:

```text
task.max_score when 0 < task.max_score <= 100, otherwise 100
```

The user progress stats endpoint still counts completed tasks from
`UserTaskProgress.is_solved`, but average grade now uses best submission scores
even for unsolved partial progress.

## API Compatibility

Existing frontend-facing response shapes were not changed:

- `SubmissionCreateResponse`
- `SubmissionResponse`
- `SubmissionCheckResponse`
- current submit/result/checks path params
- current check report shape

Added endpoint:

- `GET /api/v1/submissions?taskId=<id>`

The current frontend does not call the new history endpoint, so no frontend
source patch was required. Frontend tests, lint, and build were still run for
final compatibility verification.

## Files Changed Across Port

Phase 01 / contracts:

- `backend/app/models/task_check_spec.py`
- `backend/app/models/task.py`
- `backend/app/models/__init__.py`
- `backend/models.py`
- `backend/app/repositories/task.py`
- `backend/app/schemas/check.py`
- `backend/tests/test_task_check_specs.py`

Core orchestrator/scoring:

- `backend/app/services/checking/types.py`
- `backend/app/services/checking/orchestrator.py`
- `backend/app/services/checking/fake_runner.py`
- `backend/app/services/checking/__init__.py`
- `backend/app/services/submission.py`
- `backend/tests/test_submissions_api.py`

Sandbox and real runners:

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
- `.env.example`
- `.gitignore`
- `backend/app/core/config.py`
- `backend/requirements-dev.txt`
- `compose.yaml`

Progress/history/final verification:

- `backend/app/api/v1/submissions.py`
- `backend/app/repositories/submission.py`
- `backend/app/repositories/user_progress.py`
- `backend/app/services/submission.py`
- `backend/app/services/user_progress.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_user_progress_api.py`
- `docs/code-checker-ai/reports/checker-system-port-final-verification.md`

Docs and reports:

- `docs/code-checker-ai/README.md`
- `docs/code-checker-ai/REPORT_TEMPLATE.md`
- `docs/code-checker-ai/prompts/phase-01-contracts-and-persistence.md`
- `docs/code-checker-ai/reports/phase-01-contracts-and-persistence.md`
- `docs/code-checker-ai/reports/phase-01-port-from-codex-branch.md`
- `docs/code-checker-ai/port-checker-system/README.md`
- `docs/code-checker-ai/port-checker-system/prompts/00-audit-and-integration-plan.md`
- `docs/code-checker-ai/port-checker-system/prompts/01-core-orchestrator-and-scoring.md`
- `docs/code-checker-ai/port-checker-system/prompts/02-sandbox-and-real-runners.md`
- `docs/code-checker-ai/port-checker-system/prompts/03-progress-history-and-final-verification.md`
- `docs/code-checker-ai/reports/checker-system-port-00-audit-plan.md`
- `docs/code-checker-ai/reports/checker-system-port-01-core-orchestrator-scoring.md`
- `docs/code-checker-ai/reports/checker-system-port-02-sandbox-real-runners.md`

## Tests

Before this final report, the required initial audit commands were run:

```powershell
git status --short --branch
git branch -a --verbose --no-abbrev
```

Targeted backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_submissions_api.py backend\tests\test_user_progress_api.py
```

Result: `30 passed, 84 warnings`.

Full backend suite:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Result: `85 passed, 1 skipped, 98 warnings`.

Frontend compatibility checks:

```powershell
npm run test:run
npm run lint
npm run build
```

Results:

- `test:run`: `120 passed`
- `lint`: passed
- `build`: passed

Whitespace check:

```powershell
git diff --check
```

Result: exit code `0`; only Windows line-ending warnings were reported.

Warnings in backend tests are the existing JWT `InsecureKeyLengthWarning`
warnings from the short test secret. The skipped backend test is the opt-in
Docker sandbox integration test when the opt-in environment flag is not set.

## Known Gaps

- No Alembic migration was added; the branch still follows the current
  `Base.metadata.create_all` test/init workflow.
- Real `TaskCheckSpec` runners are Python-only. C++ remains supported through
  the preserved legacy `RefactorCheckPipeline`.
- Hidden pytest test code can still appear indirectly through runner artifacts;
  report filtering should be reviewed before broad production exposure.
- The checker Docker image must be built/published for deployments that do not
  run the compose `sandbox-prep` flow.
- Existing legacy `TaskScenario` / `TaskCheckRule` task data still needs a
  future migration plan if `TaskCheckSpec` becomes the only long-term format.

## Operational Notes

- Do not delete `TaskScenario`, `TaskCheckRule`, `refactor_checks`, or C++
  runner support until legacy tasks have been migrated.
- `CHECKER_*` settings exist beside the existing `CHECK_DOCKER_*` settings.
- `legacy-trainer-checker:local` is built by `sandbox-prep` in the adapted
  Docker-in-Docker compose flow.
- `User.total_score` now includes partial best submissions. This is a visible
  product behavior change from solved-only totals.
- `GET /api/v1/submissions?taskId=...` returns only the authenticated user's
  history and does not expose other users' submissions.

## Recommended Next Steps

- Add database migrations for `TaskCheckSpec` and any new production columns if
  the project moves beyond metadata-based schema creation.
- Decide and implement hidden-test report filtering policy.
- Add seed/demo tasks that use `TaskCheckSpec` checks directly.
- Plan migration from legacy refactor task definitions to check specs.
- Publish a versioned checker image for non-local deployments.
