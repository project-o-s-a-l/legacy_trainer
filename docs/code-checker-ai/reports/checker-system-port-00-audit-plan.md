# Checker System Port 00 - Audit and Integration Plan

## Source Branch

- Current branch: `feature/backend/checker` at `84033c5d41bbabca96295dc1cbd00896bdbde18a`.
- Source branch: `codex/phase-01-contracts-persistence` at `fd4c51f8b433fb15f57749ef2dcdc5f686b1b283`.
- Merge base: `3e568e30fd425e020d40bb8d867254ac80bdec63` (`develop`).
- The source branch must not be merged blindly. `git diff --name-status HEAD..codex/phase-01-contracts-persistence` shows backend checker changes mixed with deletions of the current refactor-check architecture, Docker/compose rewrites, frontend result UI changes, docs, seed data, and generated `legacy_checker/__pycache__` files.
- The working tree already contains uncommitted phase-01 port changes: `TaskCheckSpec`, `backend/app/schemas/check.py`, `backend/tests/test_task_check_specs.py`, `docs/code-checker-ai/`, and updates to `Task`, `TaskRepository`, `SubmissionService`, `backend/models.py`, and `backend/app/models/__init__.py`. These were treated as current branch context and were not reverted.

Mandatory audit commands were run:

- `git status --short --branch`
- `git branch -a --verbose --no-abbrev`
- `git diff --name-status HEAD..codex/phase-01-contracts-persistence`
- `git ls-tree -r --name-only codex/phase-01-contracts-persistence`

## Current Branch Summary

The current branch already has a working refactoring checker stack:

- `backend/app/services/refactor_checks/` contains `RefactorCheckPipeline`, behavior/contract/structure/quality checkers, workspace management, and local/docker execution support.
- Runtime configuration currently uses `CHECK_EXECUTION_BACKEND`, `CHECK_DOCKER_*`, `CHECK_WORKSPACE_ROOT`, and language-specific runner images (`legacy-trainer-python-runner:latest`, `legacy-trainer-cpp-runner:latest`).
- `TaskScenario` stores behavior scenarios; `TaskCheckRule` stores rule definitions keyed by `rule_type`. `TaskDefinitionService` combines both into an in-memory task definition for the pipeline.
- `RefactorCheckPipeline.evaluate()` returns multiple `CheckOutcome` values and calculates a scaled score from rule weights.
- `SubmissionService` first tries `RefactorCheckPipeline`; if no scenarios/rules exist, it falls back to `_evaluate_code`.
- `SubmissionService` already persists multiple `SubmissionCheck` rows for pipeline checks, and one `tests` check for the heuristic fallback.
- The current bug is in score assignment: both pipeline and fallback paths set `submission.score = raw_score if status == PASSED else 0`, so partial scores from failed checks are lost.
- Progress update is currently embedded in `SubmissionService`; it only counts solved/passed submissions in `User.total_score`, and `is_solved` is tied to `SubmissionStatus.PASSED`.
- Public backend API currently includes:
  - `POST /api/v1/tasks/{task_id}/submit`
  - `GET /api/v1/submissions/{submission_id}`
  - `GET /api/v1/submissions/{submission_id}/checks`
- The source branch history endpoint `GET /api/v1/submissions?taskId=...` is not present yet.
- After the local phase-01 port, `TaskCheckSpec` exists beside `TaskScenario` and `TaskCheckRule`; `TaskRepository` preloads and creates/list check specs, but no orchestrator consumes them yet.

## Source Branch Summary

The source branch implements a separate `TaskCheckSpec`-based checker architecture:

- `backend/app/services/checking/types.py` defines `CheckContext`, `CheckRunResult`, `CheckRunner`, and `CheckOrchestrationResult`.
- `backend/app/services/checking/orchestrator.py` sorts `Task.check_specs` by `(order, id)`, runs one runner per spec, falls back to a no-spec tests runner, aggregates status, weighted score, message, execution time, and memory.
- Status aggregation only treats required checks as submission-failing: required `error` -> `SubmissionStatus.ERROR`; required `failed` -> `SubmissionStatus.FAILED`; otherwise `PASSED`.
- Score aggregation is a weighted average: `int(sum(check.score * check.weight) / sum(check.weight))` for checks with `weight > 0`.
- `DeterministicFakeRunner` preserves the old heuristic tests behavior and returns placeholder passed results for non-tests specs.
- Real runner classes are thin wrappers over `SandboxedCheckRunner`:
  - `PythonPytestRunner`
  - `PythonRuffLintRunner`
  - `PythonStaticRunner`
  - `PythonArchitectureRunner`
- `SandboxedCheckRunner` sends JSON payloads to `DockerSandboxExecutor`, parses sandbox JSON, validates `CheckReport`, and adds sandbox metadata to `metrics`/`artifacts`.
- `legacy_checker/checks.py` is the checker program inside the sandbox image. It supports pytest, Ruff lint, Python AST static checks, and Python AST architecture checks.
- `docker/checker.Dockerfile` builds a non-root Python image with `pytest`, `ruff`, and `legacy_checker`.
- Source `SubmissionService` always calls `CheckOrchestrator.with_default_runners()`, saves every `SubmissionCheck`, keeps the orchestration score even when status is failed/error, and delegates progress to `UserProgressService.record_submission()`.
- Source progress/history changes add `GET /api/v1/submissions?taskId=...`, best-submission-by-score logic, solved threshold based on `task.max_score`, and total score as a sum of best submission scores.
- Source frontend changes expect richer check result types, per-check details, artifacts/metrics, requirements text, and submission history.

Important non-core source changes:

- Source deletes `TaskScenario`, `TaskCheckRule`, `refactor_checks/`, `seed_refactor_tasks.py`, and old sandbox runner Dockerfiles. These deletions are not safe for the current branch.
- Source rewrites Docker/compose from the current Docker-in-Docker layout to a `docker/docker-compose.yml` that mounts `/var/run/docker.sock`. That should be adapted, not copied.
- Source adds `legacy_checker/__pycache__`; generated pyc files should not be ported.
- Source docs/prompts include later phase reports and frontend/docker hardening notes; useful as reference but not all needed in this branch.

## Architecture Decision

Use the source branch's `TaskCheckSpec` orchestrator as the new primary checker path, but preserve the current `RefactorCheckPipeline` as a legacy adapter/fallback until existing refactor tasks are migrated.

Recommended runtime decision order in `SubmissionService`:

1. Validate task, code, language, and task-language availability exactly as today.
2. Create the `Submission`.
3. If `task.check_specs` is non-empty, run the new `CheckOrchestrator`.
4. Else, try the current `RefactorCheckPipeline` for `TaskScenario`/`TaskCheckRule` tasks.
5. Else, use the deterministic no-spec fake tests runner or a tiny adapter around the existing `_evaluate_code` behavior.
6. Assign `submission.status`, `submission.score`, `checked_at`, `execution_time_ms`, and `memory_used_kb` from the chosen result without zeroing partial score solely because the status is `failed` or `error`.
7. Persist one `SubmissionCheck` per check result with a normalized `CheckReport` shape.
8. Update progress/history in the same transaction.

`TaskCheckSpec` should become the canonical format for new tasks. `TaskScenario`/`TaskCheckRule` should remain read-compatible for current seeded/refactor tasks and tests. Do not delete the legacy models, repositories, tests, or `refactor_checks` directory in the port windows unless a later migration explicitly replaces their data and behavior.

The legacy pipeline should be wrapped, not merged into the new orchestrator internals. A small adapter can convert each current `CheckOutcome` into the same public shape as `CheckRunResult`/`CheckReport`:

- `check_type`, `status`, `score` from `CheckOutcome`.
- `weight` from `max_score`.
- `report` normalized to include `total`, `passed`, `failed`, `errors`, `summary`, `details`, `metrics`, and `artifacts`.
- `metrics.runner = "refactor_pipeline"` plus `rule_type` or checker name where available.

This keeps `SubmissionService` and frontend-facing API consistent while avoiding an early rewrite of the working Python/C++ refactor checks.

## Files Compared

Current branch context read from the working tree:

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
- `backend/app/repositories/submission.py`
- `backend/app/repositories/user_progress.py`
- `backend/app/services/user_progress.py`
- `backend/app/schemas/check.py`
- `backend/app/schemas/submission.py`
- `backend/app/models/submission.py`
- `backend/app/models/submission_check.py`
- `backend/app/db/enums.py`
- `backend/app/api/v1/submissions.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_refactor_submission_api.py`
- `backend/tests/test_task_check_specs.py`
- `compose.yaml`
- `docker/backend.Dockerfile`
- `docker/frontend.Dockerfile`
- `docker/start-backend.sh`
- `docker/sandbox/python-runner.Dockerfile`
- `docker/sandbox/cpp-runner.Dockerfile`
- `.env.example`

Source branch context read via `git show`/`git diff` without checkout:

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
- `backend/app/repositories/user_progress.py`
- `backend/app/services/user_progress.py`
- `backend/app/core/config.py`
- `backend/requirements.txt`
- `backend/init_db.py`
- `backend/tests/test_submissions_api.py`
- `backend/tests/test_sandbox_executor.py`
- `backend/tests/test_sandboxed_runner.py`
- `backend/tests/test_sandbox_docker_integration.py`
- `backend/tests/sandbox_fakes.py`
- `docker/checker.Dockerfile`
- `docker/docker-compose.yml`
- `legacy_checker/checks.py`
- `legacy_checker/run.py`
- `docs/code-checker-ai/reports/phase-02-orchestrator-fake-runner.md`
- `docs/code-checker-ai/reports/phase-03-python-pytest-runner.md`
- `docs/code-checker-ai/reports/phase-04-lint-static-architecture.md`
- `docs/code-checker-ai/reports/phase-05-scoring-progress-history.md`
- Frontend diffs in `CheckSolution`, `getScoreForSolution`, `SolutionResultPage`, `CodeBlockPage`, tests, and `mockApi`.

## Proposed Port Plan

1. Core contracts and fake orchestrator.
   - Port `backend/app/services/checking/types.py`, `fake_runner.py`, `orchestrator.py`, and `__init__.py`.
   - Keep source contracts close to original names so later runner code ports cleanly.
   - In the first code window, use fake/default fake runners only; do not introduce Docker sandbox yet.
   - Add a legacy adapter that turns current `RefactorCheckPipeline` output into the same shape used by the orchestrator.
   - Change `SubmissionService` to choose between `TaskCheckSpec` orchestrator, legacy refactor pipeline, and no-spec fake tests.
   - Persist all checks and set `submission.score = result.score` without status-based zeroing.
   - Keep response fields `submissionId`, `taskId`, `status`, `score`, `message`, and `testPassed`.

2. Score/progress/history semantics.
   - Move progress update rules toward source `UserProgressService.record_submission()` or extract equivalent logic from current `SubmissionService`.
   - Record every submission attempt, including failed/error checks.
   - Select `best_submission_id` by highest score, not only by passed status.
   - Keep `is_solved` monotonic: once true, do not reset to false.
   - Use a solved threshold based on `task.max_score` when it is in `1..100`, otherwise `100`.
   - Decide product semantics for `User.total_score`: recommended source behavior is sum of best scores, including partial best submissions. If the product wants solved-only totals, document that explicitly and add tests.
   - Add source history endpoint `GET /api/v1/submissions?taskId=...` only after backend tests cover ownership and sorting.

3. Real runners and sandbox.
   - Port `sandbox.py`, `sandboxed_runner.py`, real Python runner wrappers, and `legacy_checker/checks.py`/`run.py`.
   - Do not port `legacy_checker/__pycache__`.
   - Add `pytest` and `ruff` where needed. Prefer keeping them in the checker Docker image; only add them to backend runtime if local non-Docker runners remain supported.
   - Adapt `DockerSandboxExecutor` to current Docker-in-Docker compose (`DOCKER_HOST=tcp://docker-daemon:2375`) instead of copying source `/var/run/docker.sock` compose wholesale.
   - Build a single `legacy-trainer-checker:local` image in the current `sandbox-prep` flow or add a sibling prep service.
   - Keep existing Python/C++ refactor runner images until `RefactorCheckPipeline` is retired.
   - Add `CHECKER_*` env vars beside existing `CHECK_DOCKER_*` vars to avoid breaking legacy pipeline settings.

4. Check config and seed migration.
   - For new Python tasks, use source `TaskCheckSpec.config_json` contracts:
     - `tests`: `entry_file`, `test_file`, `test_code`, `visible`
     - `lint`: `entry_file`, `select`, `ignore`, `line_length`
     - `static`: `forbidden_imports`, `forbidden_calls`, `required_symbols`
     - `architecture`: `required_classes`, `required_methods`, `forbidden_functions`, `max_function_length`
   - Do not remove `seed_refactor_tasks.py` in the same step. Either migrate its data to check specs or keep it as legacy seed data.
   - If porting source `init_db.py` demo seed logic, adapt it to current auth/env requirements and current Docker startup script.

5. Frontend/API compatibility.
   - Keep current submit response contract.
   - Keep existing `GET /submissions/{id}` and `GET /submissions/{id}/checks`.
   - Add history endpoint before porting source frontend code that depends on it.
   - Ensure every `report_json` has the richer source shape so frontend can render all check types consistently.
   - Do not expose hidden pytest secrets in user-visible reports without a filtering decision.

## Window Breakdown

Window 01 - core orchestrator and scoring:

- Port checking contracts, fake runner, orchestrator.
- Add adapter/normalizer for `RefactorCheckPipeline`.
- Update `SubmissionService` selection and remove partial-score zeroing.
- Add or adapt tests for multi-spec fake checks, optional failed checks, weighted score, no-spec fallback, and legacy refactor fallback.
- Expected verification: `.\.venv\Scripts\python.exe -m pytest backend\tests\test_task_check_specs.py backend\tests\test_submissions_api.py backend\tests\test_refactor_submission_api.py`.

Window 02 - sandbox and real runners:

- Port Docker sandbox executor, sandboxed runner, Python pytest/lint/static/architecture runner wrappers, `legacy_checker`, and sandbox fakes.
- Adapt Docker image build to current Docker-in-Docker compose.
- Add `CHECKER_*` settings without deleting existing `CHECK_DOCKER_*`.
- Add sandbox unit tests and real-runner tests with in-process/fake executor first; keep Docker integration test opt-in/skipped when Docker is unavailable.
- Expected verification: targeted sandbox tests plus full `backend\tests` if settings/imports change.

Window 03 - progress, history, final verification:

- Move/align progress update logic.
- Add submission history repository/service/API endpoint.
- Adapt current progress tests and source history/scoring tests.
- Decide and document total-score semantics.
- Port frontend result/history/check-breakdown changes only after backend endpoints are present.
- Run full backend tests and frontend tests/build if frontend changes are included.

## Tests To Reuse / Adapt

Already ported or directly reusable:

- `backend/tests/test_task_check_specs.py` is already present in the working tree and matches source phase-01 contracts.
- Source `backend/tests/test_sandbox_executor.py` can be ported mostly directly with the sandbox code.
- Source `backend/tests/test_sandboxed_runner.py` can be ported after checking package exists, but API-level cases need injection/adaptation so current legacy fallback remains testable.
- Source `backend/tests/sandbox_fakes.py` is useful for sandboxed runner tests and avoids Docker dependency.

Adapt from source `backend/tests/test_submissions_api.py`:

- `test_submit_solution_runs_all_task_check_specs`
- `test_submit_solution_uses_weighted_score_and_required_status_rules`
- pytest success/failure/timeout/invalid config tests
- lint/static/architecture success/failure tests
- progress attempts/best/solved tests
- total score recalculation tests
- history endpoint ownership/sorting tests

Keep and update current tests:

- Current basic submit/auth/language/ownership tests should remain.
- `backend/tests/test_refactor_submission_api.py` should stay as the regression suite for the legacy `TaskScenario`/`TaskCheckRule` path.
- Current score/progress expectations that assert failed submissions have `score == 0` should be changed when partial scores become product behavior.
- Current C++ refactor tests should not be deleted because source real runners only cover Python `TaskCheckSpec` checks.

Do not port directly:

- Source deletions of `test_refactor_execution.py` and `test_refactor_submission_api.py`.
- Source Docker integration test as an always-on test; keep it skipped/opt-in because it requires Docker image availability.
- Source frontend tests before adding backend history endpoint and stable report filtering.

## Risks

- Blind merge would delete the current `refactor_checks` system, `TaskScenario`, `TaskCheckRule`, C++ refactor coverage, and existing seed flow.
- Score semantics will change visible behavior: failed submissions can keep partial scores. This requires backend test updates and product/frontend agreement about `User.total_score`.
- Current `RefactorCheckPipeline` reports are not all shaped like `CheckReport`; without normalization, frontend rendering of check breakdown will be inconsistent.
- Source real runners are Python-only. Current branch supports C++ through the refactor pipeline; that must remain until equivalent `TaskCheckSpec` C++ runners exist.
- Docker infrastructure differs. Source compose mounts the host Docker socket; current branch uses a Docker-in-Docker service. Copying source compose would regress current local setup and alter the security model.
- Hidden pytest tests live in `TaskCheckSpec.config_json.test_code`; source reports currently retain stdout/stderr/artifacts. Frontend/API filtering is needed before using sensitive hidden tests.
- `backend/requirements.txt` in source adds `pytest` and `ruff`; if real checks move fully into checker containers, backend runtime may not need both.
- Source `init_db.py` demo seed logic may conflict with current `seed_refactor_tasks.py` and required environment settings.
- The working tree is already dirty. Future windows must avoid overwriting the uncommitted phase-01 files and docs.
- Frontend source changes depend on `GET /api/v1/submissions?taskId=...`; porting UI first would create broken requests.

## Explicit Non-Goals

- Do not merge `codex/phase-01-contracts-persistence` wholesale.
- Do not delete `TaskScenario`, `TaskCheckRule`, `refactor_checks/`, `seed_refactor_tasks.py`, or current C++ refactor support in the core orchestrator window.
- Do not port source frontend changes before backend history/check-report contracts are ready.
- Do not replace the current Docker-in-Docker compose with the source host-socket compose without a separate infra decision.
- Do not port generated `legacy_checker/__pycache__` files.
- Do not add Alembic/migration work in this audit window.
- Do not run code tests for this window because only documentation/report files were changed.
