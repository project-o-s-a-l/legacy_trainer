from __future__ import annotations

import ast
import re

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.services.refactor_checks.models import CheckOutcome, RuleDefinition


class StructureChecker:
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
                status=CheckStatus.ERROR,
                report={"message": f"Syntax error: {exc.msg}"},
            )

        issues: list[str] = []
        max_top_level_statements = rule.config.get("max_top_level_statements")
        if isinstance(max_top_level_statements, int):
            top_level_statements = sum(
                1
                for node in module.body
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            )
            if top_level_statements > max_top_level_statements:
                issues.append(
                    f"Too many top-level statements: {top_level_statements} > {max_top_level_statements}"
                )

        if rule.config.get("forbid_global_assignments"):
            for node in module.body:
                if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    issues.append("Global assignments are forbidden")
                    break

        max_function_length = rule.config.get("max_function_length")
        if isinstance(max_function_length, int):
            for node in ast.walk(module):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    function_length = end_lineno - node.lineno + 1
                    if function_length > max_function_length:
                        issues.append(
                            f"Function {node.name} is too long: {function_length} > {max_function_length}"
                        )

        required_tokens = rule.config.get("required_tokens", [])
        for token in required_tokens:
            if token not in source_code:
                issues.append(f"Required token is missing: {token}")

        forbidden_tokens = rule.config.get("forbidden_tokens", [])
        for token in forbidden_tokens:
            if token in source_code:
                issues.append(f"Forbidden token found: {token}")

        if issues:
            return self._failed(rule=rule, report={"issues": issues})

        return CheckOutcome(
            check_type=SubmissionCheckType.ARCHITECTURE,
            status=CheckStatus.PASSED,
            score=rule.weight,
            max_score=rule.weight,
            report={"issues": []},
        )

    def _run_text(self, *, source_code: str, rule: RuleDefinition) -> CheckOutcome:
        issues: list[str] = []

        required_tokens = rule.config.get("required_tokens", [])
        for token in required_tokens:
            if token not in source_code:
                issues.append(f"Required token is missing: {token}")

        forbidden_tokens = rule.config.get("forbidden_tokens", [])
        for token in forbidden_tokens:
            if token in source_code:
                issues.append(f"Forbidden token found: {token}")

        minimum_class_count = rule.config.get("minimum_class_count")
        if isinstance(minimum_class_count, int):
            class_count = len(re.findall(r"\b(class|struct)\b", source_code))
            if class_count < minimum_class_count:
                issues.append(
                    f"Class/struct count is too low: {class_count} < {minimum_class_count}"
                )

        if issues:
            return self._failed(rule=rule, report={"issues": issues})

        return CheckOutcome(
            check_type=SubmissionCheckType.ARCHITECTURE,
            status=CheckStatus.PASSED,
            score=rule.weight,
            max_score=rule.weight,
            report={"issues": []},
        )

    def _failed(
        self,
        *,
        rule: RuleDefinition,
        report: dict,
        status: CheckStatus = CheckStatus.FAILED,
    ) -> CheckOutcome:
        return CheckOutcome(
            check_type=SubmissionCheckType.ARCHITECTURE,
            status=status,
            score=0,
            max_score=rule.weight,
            report=report,
        )
