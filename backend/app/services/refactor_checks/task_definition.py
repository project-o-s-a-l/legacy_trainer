from __future__ import annotations

from backend.app.models.task import Task
from backend.app.repositories.task_check_rule import TaskCheckRuleRepository
from backend.app.repositories.task_scenario import TaskScenarioRepository
from backend.app.services.refactor_checks.models import (
    RuleDefinition,
    ScenarioDefinition,
    TaskDefinition,
)


class TaskDefinitionService:
    def __init__(
        self,
        *,
        scenarios: TaskScenarioRepository,
        rules: TaskCheckRuleRepository,
    ) -> None:
        self.scenarios = scenarios
        self.rules = rules

    def build(self, *, task: Task, language_name: str) -> TaskDefinition:
        scenario_rows = self.scenarios.list_for_task(
            task_id=task.id,
            language_name=language_name,
        )
        rule_rows = self.rules.list_for_task(
            task_id=task.id,
            language_name=language_name,
        )

        return TaskDefinition(
            task_id=task.id,
            language_name=language_name,
            legacy_code=task.legacy_code,
            scenarios=[
                ScenarioDefinition(
                    id=item.id,
                    name=item.name,
                    weight=item.weight,
                    input_payload=item.input_payload,
                    expected_output=item.expected_output,
                )
                for item in scenario_rows
            ],
            rules={
                item.rule_type: RuleDefinition(
                    rule_type=item.rule_type,
                    weight=item.weight,
                    config=item.config_json,
                )
                for item in rule_rows
            },
        )
