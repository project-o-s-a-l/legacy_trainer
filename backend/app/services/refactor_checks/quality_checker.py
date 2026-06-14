from __future__ import annotations

import ast

from backend.app.db.enums import CheckStatus, SubmissionCheckType
from backend.app.services.refactor_checks.models import CheckOutcome, RuleDefinition


class QualityChecker:
    def run(
        self,
        *,
        language_name: str,
        source_code: str,
        rule: RuleDefinition,
    ) -> CheckOutcome:
        issues: list[str] = []

        forbidden_markers = rule.config.get(
            "forbidden_markers",
            ["TODO", "pass", "NotImplementedError", "stub"],
        )
        for marker in forbidden_markers:
            if marker in source_code:
                issues.append(f"Forbidden marker found: {marker}")

        max_lines = rule.config.get("max_lines")
        if isinstance(max_lines, int):
            line_count = len(source_code.splitlines())
            if line_count > max_lines:
                issues.append(f"Too many lines: {line_count} > {max_lines}")

        if language_name == "python":
            try:
                ast.parse(source_code)
            except SyntaxError as exc:
                return self._failed(
                    rule=rule,
                    status=CheckStatus.ERROR,
                    report={"message": f"Syntax error: {exc.msg}"},
                )

        if issues:
            return self._failed(rule=rule, report={"issues": issues})

        return CheckOutcome(
            check_type=SubmissionCheckType.LINT,
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
            check_type=SubmissionCheckType.LINT,
            status=status,
            score=0,
            max_score=rule.weight,
            report=report,
        )
