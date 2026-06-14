from __future__ import annotations

import ast
import re

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.services.refactor_checks.models import CheckOutcome, RuleDefinition


class ContractChecker:
    def run(
        self,
        *,
        language_name: str,
        source_code: str,
        rule: RuleDefinition,
    ) -> CheckOutcome:
        if language_name == "python":
            return self._run_python(source_code=source_code, rule=rule)
        return self._run_text(source_code=source_code, rule=rule)

    def _run_python(self, *, source_code: str, rule: RuleDefinition) -> CheckOutcome:
        try:
            module = ast.parse(source_code)
        except SyntaxError as exc:
            return self._failed(
                rule=rule,
                report={"message": f"Syntax error: {exc.msg}"},
                status=CheckStatus.ERROR,
            )

        top_level_functions = {
            node.name for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        classes = {
            node.name: node
            for node in module.body
            if isinstance(node, ast.ClassDef)
        }

        missing_functions = [
            name
            for name in rule.config.get("required_functions", [])
            if name not in top_level_functions
        ]
        missing_classes = [
            name
            for name in rule.config.get("required_classes", [])
            if name not in classes
        ]

        required_methods = rule.config.get("required_methods", {})
        missing_methods: list[str] = []
        for class_name, methods in required_methods.items():
            class_node = classes.get(class_name)
            if class_node is None:
                missing_methods.extend(f"{class_name}.{method}" for method in methods)
                continue
            class_methods = {
                item.name
                for item in class_node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            for method in methods:
                if method not in class_methods:
                    missing_methods.append(f"{class_name}.{method}")

        if missing_functions or missing_classes or missing_methods:
            return self._failed(
                rule=rule,
                report={
                    "missingFunctions": missing_functions,
                    "missingClasses": missing_classes,
                    "missingMethods": missing_methods,
                },
            )

        return CheckOutcome(
            check_type=SubmissionCheckType.STATIC,
            status=CheckStatus.PASSED,
            score=rule.weight,
            max_score=rule.weight,
            report={
                "missingFunctions": [],
                "missingClasses": [],
                "missingMethods": [],
            },
        )

    def _run_text(self, *, source_code: str, rule: RuleDefinition) -> CheckOutcome:
        missing_tokens = [
            token
            for token in rule.config.get("required_tokens", [])
            if token not in source_code
        ]
        missing_patterns = [
            pattern
            for pattern in rule.config.get("required_regexes", [])
            if re.search(pattern, source_code, re.MULTILINE) is None
        ]

        if missing_tokens or missing_patterns:
            return self._failed(
                rule=rule,
                report={
                    "missingTokens": missing_tokens,
                    "missingPatterns": missing_patterns,
                },
            )

        return CheckOutcome(
            check_type=SubmissionCheckType.STATIC,
            status=CheckStatus.PASSED,
            score=rule.weight,
            max_score=rule.weight,
            report={
                "missingTokens": [],
                "missingPatterns": [],
            },
        )

    def _failed(
        self,
        *,
        rule: RuleDefinition,
        report: dict,
        status: CheckStatus = CheckStatus.FAILED,
    ) -> CheckOutcome:
        return CheckOutcome(
            check_type=SubmissionCheckType.STATIC,
            status=status,
            score=0,
            max_score=rule.weight,
            report=report,
        )
