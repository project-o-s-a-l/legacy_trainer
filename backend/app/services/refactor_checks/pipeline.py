from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.db.enums import CheckStatus, SubmissionStatus
from backend.app.models.task import Task
from backend.app.repositories.task_check_rule import TaskCheckRuleRepository
from backend.app.repositories.task_scenario import TaskScenarioRepository
from backend.app.services.refactor_checks.behavior_checker import BehaviorChecker
from backend.app.services.refactor_checks.contract_checker import ContractChecker
from backend.app.services.refactor_checks.models import CheckOutcome, PipelineResult
from backend.app.services.refactor_checks.quality_checker import QualityChecker
from backend.app.services.refactor_checks.structure_checker import StructureChecker
from backend.app.services.refactor_checks.task_definition import TaskDefinitionService
from backend.app.services.refactor_checks.workspace import ModuleWorkspaceBuilder


class RefactorCheckPipeline:
    def __init__(self, db: Session) -> None:
        self.definition_service = TaskDefinitionService(
            scenarios=TaskScenarioRepository(db),
            rules=TaskCheckRuleRepository(db),
        )
        self.workspace_builder = ModuleWorkspaceBuilder()
        self.behavior_checker = BehaviorChecker()
        self.contract_checker = ContractChecker()
        self.structure_checker = StructureChecker()
        self.quality_checker = QualityChecker()

    def evaluate(
        self,
        *,
        task: Task,
        language_name: str,
        candidate_code: str,
    ) -> PipelineResult | None:
        definition = self.definition_service.build(task=task, language_name=language_name)
        if not definition.scenarios and not definition.rules:
            return None

        checks: list[CheckOutcome] = []
        total_duration_ms = 0

        workspace = self.workspace_builder.build(
            language_name=language_name,
            legacy_code=definition.legacy_code or "",
            candidate_code=candidate_code,
        )
        try:
            behavior_rule = definition.rules.get("behavior")
            if behavior_rule is not None:
                behavior_outcome = self.behavior_checker.run(
                    workspace=workspace,
                    rule=behavior_rule,
                    scenarios=definition.scenarios,
                    legacy_code_available=bool(definition.legacy_code),
                )
                checks.append(behavior_outcome)
                duration = behavior_outcome.report.get("durationMs")
                if isinstance(duration, int):
                    total_duration_ms += duration

            contract_rule = definition.rules.get("contract")
            if contract_rule is not None:
                checks.append(
                    self.contract_checker.run(
                        language_name=language_name,
                        source_code=candidate_code,
                        rule=contract_rule,
                    )
                )

            structure_rule = definition.rules.get("structure")
            if structure_rule is not None:
                checks.append(
                    self.structure_checker.run(
                        language_name=language_name,
                        source_code=candidate_code,
                        rule=structure_rule,
                    )
                )

            quality_rule = definition.rules.get("quality")
            if quality_rule is not None:
                checks.append(
                    self.quality_checker.run(
                        language_name=language_name,
                        source_code=candidate_code,
                        rule=quality_rule,
                    )
                )
        finally:
            self.workspace_builder.cleanup(workspace)

        if not checks:
            return None

        score = self._calculate_score(checks=checks, max_score=task.max_score)
        status = self._resolve_status(checks)
        message = self._build_message(checks, status)
        tests_outcome = next(
            (item for item in checks if item.check_type.value == "tests"),
            None,
        )

        return PipelineResult(
            status=status,
            score=score,
            message=message,
            test_passed=int(tests_outcome.report.get("passed", 0)) if tests_outcome else 0,
            total_tests=int(tests_outcome.report.get("total", 0)) if tests_outcome else 0,
            checks=checks,
            execution_time_ms=total_duration_ms or None,
            memory_used_kb=None,
        )

    def _calculate_score(self, *, checks: list[CheckOutcome], max_score: int) -> int:
        configured = sum(item.max_score for item in checks)
        if configured <= 0:
            return 0

        earned = sum(item.score for item in checks)
        scaled = round((earned / configured) * max_score)
        return max(0, min(max_score, scaled))

    def _resolve_status(self, checks: list[CheckOutcome]) -> SubmissionStatus:
        if any(item.status == CheckStatus.ERROR for item in checks):
            return SubmissionStatus.ERROR
        if checks and all(item.status == CheckStatus.PASSED for item in checks):
            return SubmissionStatus.PASSED
        return SubmissionStatus.FAILED

    def _build_message(
        self,
        checks: list[CheckOutcome],
        status: SubmissionStatus,
    ) -> str:
        tests_outcome = next(
            (item for item in checks if item.check_type.value == "tests"),
            None,
        )
        if tests_outcome is not None:
            passed = tests_outcome.report.get("passed", 0)
            total = tests_outcome.report.get("total", 0)
            if status == SubmissionStatus.PASSED:
                return f"Behaviour preserved for {passed} of {total} scenarios"
            return f"Behaviour matched in {passed} of {total} scenarios"

        if status == SubmissionStatus.PASSED:
            return "All configured refactoring checks passed"
        if status == SubmissionStatus.ERROR:
            return "Some refactoring checks could not be executed"
        return "Some refactoring checks failed"
