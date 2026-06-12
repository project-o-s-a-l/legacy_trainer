# Code Checker Implementation Plan

This directory keeps shared context for staged implementation of the Legacy Trainer code checking system.

Agents should:

1. Read this file.
2. Read the reports in `docs/code-checker-ai/reports/`, especially the previous phase report.
3. Implement only the requested phase without rewriting unrelated areas.
4. Run relevant tests.
5. Record the result in `docs/code-checker-ai/reports/`.

## Goal

Replace the current heuristic solution check with an extensible checks system:

- tests;
- lint;
- static analysis;
- architecture rules;
- scoring;
- progress and history;
- frontend result breakdown.

## Current Entry Point

The current submit flow starts in `backend/app/services/submission.py`.

In this branch it already has a `RefactorCheckPipeline` based on `TaskScenario` and `TaskCheckRule`, with a legacy heuristic fallback. Phase 01 adds `TaskCheckSpec` contracts and persistence without replacing that existing pipeline.

## Phases

| Phase | Name | Main Result |
| --- | --- | --- |
| 01 | Contracts and persistence | Check specs, result contracts, DB/schema/repository layer. |
| 02 | Orchestrator with fake runner | Submission checks flow through orchestration. |
| 03 | Python pytest runner | Python test checks run in a controlled workspace. |
| 04 | Lint, static, architecture checks | Separate check runners and configurable rules. |
| 05 | Scoring, progress, history | Final score, best submission, progress and history. |
| 06 | Frontend check results | UI renders check breakdown and details. |
| 07 | Hardening, Docker, seed data | Docker/local run, sample checks, docs and stabilization. |

## Prompts

Phase prompts live in `docs/code-checker-ai/prompts/`.
