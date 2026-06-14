from __future__ import annotations

import ast
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


OUTPUT_LIMIT = 8_000
JUNIT_REPORT_NAME = "pytest-report.xml"
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
SYMBOL_NODES = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


class CheckerConfigError(ValueError):
    pass


@dataclass(frozen=True)
class PytestConfig:
    entry_file: str
    test_file: str
    test_code: str
    visible: bool


@dataclass(frozen=True)
class PytestCounts:
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    details: list[dict[str, Any]]


@dataclass(frozen=True)
class LintConfig:
    entry_file: str
    select: list[str]
    ignore: list[str]
    line_length: int | None


@dataclass(frozen=True)
class StaticConfig:
    forbidden_imports: list[str]
    forbidden_calls: list[str]
    required_symbols: list[str]


@dataclass(frozen=True)
class ArchitectureConfig:
    required_classes: list[str]
    required_methods: dict[str, list[str]]
    forbidden_functions: list[str]
    max_function_length: int | None


def run_check(payload: dict[str, Any]) -> dict[str, Any]:
    started_at = time.perf_counter()
    check_type = _string(payload.get("check_type"), "tests")
    check_name = _string(payload.get("check_name"), check_type)
    try:
        if check_type == "tests":
            return _run_pytest(payload, started_at)
        if check_type == "lint":
            return _run_ruff(payload, started_at)
        if check_type == "static":
            return _run_static(payload, started_at)
        if check_type == "architecture":
            return _run_architecture(payload, started_at)
        raise CheckerConfigError(f"Unsupported check type: {check_type}")
    except SyntaxError as exc:
        return _error_result(
            check_type=check_type,
            check_name=check_name,
            runner=_runner_name(check_type),
            message=f"Syntax error: {exc.msg}",
            duration_ms=_duration_ms(started_at),
            error_type="syntax_error",
            line=exc.lineno,
            column=exc.offset,
            detail_name="syntax_error",
        )
    except CheckerConfigError as exc:
        return _error_result(
            check_type=check_type,
            check_name=check_name,
            runner=_runner_name(check_type),
            message=str(exc),
            duration_ms=_duration_ms(started_at),
            error_type="config_error",
        )
    except Exception as exc:
        return _error_result(
            check_type=check_type,
            check_name=check_name,
            runner=_runner_name(check_type),
            message=f"{check_name} runner failed: {exc}",
            duration_ms=_duration_ms(started_at),
            error_type=exc.__class__.__name__,
        )


def _run_pytest(payload: dict[str, Any], started_at: float) -> dict[str, Any]:
    _validate_python(payload)
    check_name = _string(payload.get("check_name"), "pytest")
    timeout_seconds = _timeout_seconds(payload)
    config = _parse_pytest_config(_config(payload))

    workspace = Path.cwd()
    (workspace / config.entry_file).write_text(
        _string(payload.get("source_code"), ""),
        encoding="utf-8",
    )
    (workspace / config.test_file).write_text(config.test_code, encoding="utf-8")
    junit_path = workspace / JUNIT_REPORT_NAME

    command = [
        sys.executable,
        "-m",
        "pytest",
        config.test_file,
        f"--junitxml={JUNIT_REPORT_NAME}",
        "--tb=short",
        "-q",
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = _duration_ms(started_at)
        summary = f"Pytest timed out after {timeout_seconds} seconds"
        report = _process_report(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=summary,
            details=[
                _detail(
                    name=check_name,
                    status="error",
                    message=summary,
                    details={"runner": "python_pytest", "timeout": True},
                )
            ],
            metrics={
                "runner": "python_pytest",
                "entry_file": config.entry_file,
                "test_file": config.test_file,
                "visible": config.visible,
                "exit_code": None,
                "duration_ms": duration_ms,
                "durationMs": duration_ms,
                "timeout_seconds": timeout_seconds,
                "timedOut": True,
            },
            stdout=_normalize_output(exc.stdout),
            stderr=_normalize_output(exc.stderr),
            exit_code=None,
            duration_ms=duration_ms,
            timed_out=True,
        )
        return _check_result(
            check_type="tests",
            status="error",
            score=0,
            report=report,
            duration_ms=duration_ms,
            timed_out=True,
        )

    duration_ms = _duration_ms(started_at)
    stdout = _normalize_output(completed.stdout)
    stderr = _normalize_output(completed.stderr)
    counts = _parse_junit_report(junit_path)

    if counts is None:
        summary = "Pytest did not produce a JUnit report"
        report = _process_report(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=summary,
            details=[
                _detail(
                    name=check_name,
                    status="error",
                    message=summary,
                    details={"runner": "python_pytest"},
                )
            ],
            metrics={
                "runner": "python_pytest",
                "entry_file": config.entry_file,
                "test_file": config.test_file,
                "visible": config.visible,
                "exit_code": completed.returncode,
                "duration_ms": duration_ms,
                "durationMs": duration_ms,
                "timeout_seconds": timeout_seconds,
                "timedOut": False,
            },
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            timed_out=False,
        )
        return _check_result("tests", "error", 0, report, duration_ms)

    if counts.errors > 0:
        status = "error"
        score = 0
        summary = _error_summary(counts.errors)
    elif counts.total == 0 and completed.returncode != 0:
        status = "error"
        score = 0
        summary = "Pytest collected no tests"
    elif counts.failed > 0 or completed.returncode != 0:
        status = "failed"
        score = _score(counts.passed, counts.total)
        summary = f"{counts.passed} of {counts.total} tests passed"
    else:
        status = "passed"
        score = 100
        summary = "All tests passed"

    report = _process_report(
        total=counts.total,
        passed=counts.passed,
        failed=counts.failed,
        errors=counts.errors,
        summary=summary,
        details=counts.details,
        metrics={
            "runner": "python_pytest",
            "entry_file": config.entry_file,
            "test_file": config.test_file,
            "visible": config.visible,
            "exit_code": completed.returncode,
            "duration_ms": duration_ms,
            "durationMs": duration_ms,
            "timeout_seconds": timeout_seconds,
            "skipped": counts.skipped,
            "timedOut": False,
        },
        stdout=stdout,
        stderr=stderr,
        exit_code=completed.returncode,
        duration_ms=duration_ms,
        timed_out=False,
    )
    return _check_result("tests", status, score, report, duration_ms)


def _run_ruff(payload: dict[str, Any], started_at: float) -> dict[str, Any]:
    _validate_python(payload)
    check_name = _string(payload.get("check_name"), "ruff")
    timeout_seconds = _timeout_seconds(payload)
    config = _parse_lint_config(_config(payload))

    workspace = Path.cwd()
    (workspace / config.entry_file).write_text(
        _string(payload.get("source_code"), ""),
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        config.entry_file,
        "--output-format=json",
        "--no-cache",
    ]
    if config.select:
        command.extend(["--select", ",".join(config.select)])
    if config.ignore:
        command.extend(["--ignore", ",".join(config.ignore)])
    if config.line_length is not None:
        command.extend(["--line-length", str(config.line_length)])

    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = _duration_ms(started_at)
        summary = f"Ruff timed out after {timeout_seconds} seconds"
        report = _process_report(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=summary,
            details=[
                _detail(
                    name=check_name,
                    status="error",
                    message=summary,
                    details={"runner": "python_ruff_lint", "timeout": True},
                )
            ],
            metrics=_lint_metrics(config, None, duration_ms, timeout_seconds, True),
            stdout=_normalize_output(exc.stdout),
            stderr=_normalize_output(exc.stderr),
            exit_code=None,
            duration_ms=duration_ms,
            timed_out=True,
        )
        return _check_result("lint", "error", 0, report, duration_ms, timed_out=True)

    duration_ms = _duration_ms(started_at)
    stdout = _normalize_output(completed.stdout)
    stderr = _normalize_output(completed.stderr)
    findings = _parse_ruff_findings(stdout)

    if findings is None:
        summary = "Ruff output could not be parsed"
        report = _process_report(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=summary,
            details=[
                _detail(
                    name=check_name,
                    status="error",
                    message=summary,
                    details={"runner": "python_ruff_lint"},
                )
            ],
            metrics=_lint_metrics(
                config,
                completed.returncode,
                duration_ms,
                timeout_seconds,
                False,
            ),
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            timed_out=False,
        )
        return _check_result("lint", "error", 0, report, duration_ms)

    if findings:
        details = [_ruff_detail(finding) for finding in findings]
        summary = _issues_summary("Ruff found", len(details))
        report = _process_report(
            total=len(details),
            passed=0,
            failed=len(details),
            errors=0,
            summary=summary,
            details=details,
            metrics=_lint_metrics(
                config,
                completed.returncode,
                duration_ms,
                timeout_seconds,
                False,
            ),
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            timed_out=False,
        )
        return _check_result("lint", "failed", 0, report, duration_ms)

    if completed.returncode != 0:
        summary = "Ruff exited with an error"
        report = _process_report(
            total=1,
            passed=0,
            failed=0,
            errors=1,
            summary=summary,
            details=[
                _detail(
                    name=check_name,
                    status="error",
                    message=summary,
                    details={"runner": "python_ruff_lint"},
                )
            ],
            metrics=_lint_metrics(
                config,
                completed.returncode,
                duration_ms,
                timeout_seconds,
                False,
            ),
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            timed_out=False,
        )
        return _check_result("lint", "error", 0, report, duration_ms)

    summary = "Lint passed"
    report = _process_report(
        total=1,
        passed=1,
        failed=0,
        errors=0,
        summary=summary,
        details=[
            _detail(
                name=check_name,
                status="passed",
                message=summary,
                details={"runner": "python_ruff_lint"},
            )
        ],
        metrics=_lint_metrics(
            config,
            completed.returncode,
            duration_ms,
            timeout_seconds,
            False,
        ),
        stdout=stdout,
        stderr=stderr,
        exit_code=completed.returncode,
        duration_ms=duration_ms,
        timed_out=False,
    )
    return _check_result("lint", "passed", 100, report, duration_ms)


def _run_static(payload: dict[str, Any], started_at: float) -> dict[str, Any]:
    _validate_python(payload)
    config = _parse_static_config(_config(payload))
    tree = ast.parse(_string(payload.get("source_code"), ""))
    findings = _static_findings(tree, config)
    duration_ms = _duration_ms(started_at)
    report = _ast_report(
        check_name=_string(payload.get("check_name"), "static"),
        runner="python_static_ast",
        duration_ms=duration_ms,
        findings=findings,
        passed_summary="Static checks passed",
        failed_summary=_issues_summary("Static checks found", len(findings)),
        config={
            "forbidden_imports": config.forbidden_imports,
            "forbidden_calls": config.forbidden_calls,
            "required_symbols": config.required_symbols,
        },
    )
    return _check_result(
        "static",
        "failed" if findings else "passed",
        0 if findings else 100,
        report,
        duration_ms,
    )


def _run_architecture(payload: dict[str, Any], started_at: float) -> dict[str, Any]:
    _validate_python(payload)
    config = _parse_architecture_config(_config(payload))
    tree = ast.parse(_string(payload.get("source_code"), ""))
    findings = _architecture_findings(tree, config)
    duration_ms = _duration_ms(started_at)
    report = _ast_report(
        check_name=_string(payload.get("check_name"), "architecture"),
        runner="python_architecture_ast",
        duration_ms=duration_ms,
        findings=findings,
        passed_summary="Architecture checks passed",
        failed_summary=_issues_summary("Architecture checks found", len(findings)),
        config={
            "required_classes": config.required_classes,
            "required_methods": config.required_methods,
            "forbidden_functions": config.forbidden_functions,
            "max_function_length": config.max_function_length,
        },
    )
    return _check_result(
        "architecture",
        "failed" if findings else "passed",
        0 if findings else 100,
        report,
        duration_ms,
    )


def _parse_pytest_config(config: dict[str, Any]) -> PytestConfig:
    entry_file = _required_python_file(config.get("entry_file"), "tests", "entry_file")
    test_file = _required_python_file(config.get("test_file"), "tests", "test_file")
    test_code = config.get("test_code")
    if not isinstance(test_code, str) or not test_code.strip():
        raise CheckerConfigError("tests config_json.test_code must be a non-empty string")
    visible = config.get("visible", False)
    if not isinstance(visible, bool):
        raise CheckerConfigError("tests config_json.visible must be a boolean")
    return PytestConfig(
        entry_file=entry_file,
        test_file=test_file,
        test_code=test_code,
        visible=visible,
    )


def _parse_lint_config(config: dict[str, Any]) -> LintConfig:
    entry_file = _required_python_file(
        config.get("entry_file", "solution.py"),
        "lint",
        "entry_file",
    )
    line_length = config.get("line_length")
    if line_length is not None and (
        not isinstance(line_length, int) or line_length <= 0
    ):
        raise CheckerConfigError("lint config_json.line_length must be a positive integer")
    return LintConfig(
        entry_file=entry_file,
        select=_string_list(config.get("select", []), "lint", "select"),
        ignore=_string_list(config.get("ignore", []), "lint", "ignore"),
        line_length=line_length,
    )


def _parse_static_config(config: dict[str, Any]) -> StaticConfig:
    return StaticConfig(
        forbidden_imports=_string_list(config.get("forbidden_imports", []), "static", "forbidden_imports"),
        forbidden_calls=_string_list(config.get("forbidden_calls", []), "static", "forbidden_calls"),
        required_symbols=_string_list(config.get("required_symbols", []), "static", "required_symbols"),
    )


def _parse_architecture_config(config: dict[str, Any]) -> ArchitectureConfig:
    max_function_length = config.get("max_function_length")
    if max_function_length is not None and (
        not isinstance(max_function_length, int) or max_function_length <= 0
    ):
        raise CheckerConfigError(
            "architecture config_json.max_function_length must be a positive integer"
        )
    return ArchitectureConfig(
        required_classes=_string_list(config.get("required_classes", []), "architecture", "required_classes"),
        required_methods=_required_methods(config.get("required_methods", {})),
        forbidden_functions=_string_list(config.get("forbidden_functions", []), "architecture", "forbidden_functions"),
        max_function_length=max_function_length,
    )


def _required_python_file(value: object, check_type: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CheckerConfigError(
            f"{check_type} config_json.{field_name} must be a non-empty string"
        )
    file_name = value.strip()
    path = Path(file_name)
    if path.name != file_name or path.is_absolute() or ".." in path.parts:
        raise CheckerConfigError(
            f"{check_type} config_json.{field_name} must be a local file name"
        )
    if not file_name.endswith(".py"):
        raise CheckerConfigError(
            f"{check_type} config_json.{field_name} must point to a Python file"
        )
    return file_name


def _string_list(value: object, check_type: str, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        raise CheckerConfigError(
            f"{check_type} config_json.{field_name} must be a list of non-empty strings"
        )
    return [item.strip() for item in value]


def _required_methods(value: object) -> dict[str, list[str]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise CheckerConfigError(
            "architecture config_json.required_methods must be an object"
        )
    result: dict[str, list[str]] = {}
    for class_name, method_names in value.items():
        if not isinstance(class_name, str) or not class_name.strip():
            raise CheckerConfigError(
                "architecture config_json.required_methods keys must be non-empty strings"
            )
        result[class_name.strip()] = _string_list(
            method_names,
            "architecture",
            "required_methods values",
        )
    return result


def _static_findings(
    tree: ast.AST,
    config: StaticConfig,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    forbidden_imports = set(config.forbidden_imports)
    forbidden_calls = set(config.forbidden_calls)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _matches_module(alias.name, forbidden_imports):
                    findings.append(
                        _finding(
                            runner="python_static_ast",
                            name="forbidden_import",
                            message=f"Import '{alias.name}' is forbidden",
                            rule="forbidden_imports",
                            value=alias.name,
                            line=node.lineno,
                            column=node.col_offset + 1,
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            matched_name = _matched_import_from_name(node, forbidden_imports)
            if matched_name:
                findings.append(
                    _finding(
                        runner="python_static_ast",
                        name="forbidden_import",
                        message=f"Import from '{matched_name}' is forbidden",
                        rule="forbidden_imports",
                        value=matched_name,
                        line=node.lineno,
                        column=node.col_offset + 1,
                    )
                )
        elif isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if call_name and _matches_call(call_name, forbidden_calls):
                findings.append(
                    _finding(
                        runner="python_static_ast",
                        name="forbidden_call",
                        message=f"Call '{call_name}' is forbidden",
                        rule="forbidden_calls",
                        value=call_name,
                        line=node.lineno,
                        column=node.col_offset + 1,
                    )
                )

    symbols = _top_level_symbols(tree)
    for symbol in config.required_symbols:
        if symbol not in symbols:
            findings.append(
                _finding(
                    runner="python_static_ast",
                    name="required_symbol",
                    message=f"Required symbol '{symbol}' is missing",
                    rule="required_symbols",
                    value=symbol,
                )
            )
    return findings


def _architecture_findings(
    tree: ast.AST,
    config: ArchitectureConfig,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    classes = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }
    required_class_names = set(config.required_classes)

    for class_name in config.required_classes:
        if class_name not in classes:
            findings.append(
                _finding(
                    runner="python_architecture_ast",
                    name="required_class",
                    message=f"Required class '{class_name}' is missing",
                    rule="required_classes",
                    value=class_name,
                )
            )

    for class_name, method_names in config.required_methods.items():
        class_node = classes.get(class_name)
        if class_node is None:
            if class_name not in required_class_names:
                findings.append(
                    _finding(
                        runner="python_architecture_ast",
                        name="required_class",
                        message=f"Required class '{class_name}' is missing",
                        rule="required_methods",
                        value=class_name,
                    )
                )
            continue

        existing_methods = {
            node.name
            for node in class_node.body
            if isinstance(node, FUNCTION_NODES)
        }
        for method_name in method_names:
            if method_name not in existing_methods:
                findings.append(
                    _finding(
                        runner="python_architecture_ast",
                        name="required_method",
                        message=f"Required method '{class_name}.{method_name}' is missing",
                        rule="required_methods",
                        value=f"{class_name}.{method_name}",
                        line=class_node.lineno,
                        column=class_node.col_offset + 1,
                    )
                )

    forbidden_functions = set(config.forbidden_functions)
    for node in ast.walk(tree):
        if not isinstance(node, FUNCTION_NODES):
            continue
        if node.name in forbidden_functions:
            findings.append(
                _finding(
                    runner="python_architecture_ast",
                    name="forbidden_function",
                    message=f"Function '{node.name}' is forbidden",
                    rule="forbidden_functions",
                    value=node.name,
                    line=node.lineno,
                    column=node.col_offset + 1,
                )
            )
        if config.max_function_length is not None:
            length = _function_length(node)
            if length > config.max_function_length:
                findings.append(
                    _finding(
                        runner="python_architecture_ast",
                        name="max_function_length",
                        message=(
                            f"Function '{node.name}' has {length} lines; "
                            f"maximum is {config.max_function_length}"
                        ),
                        rule="max_function_length",
                        value=node.name,
                        line=node.lineno,
                        column=node.col_offset + 1,
                        extra={
                            "length": length,
                            "max_function_length": config.max_function_length,
                        },
                    )
                )
    return findings


def _ast_report(
    *,
    check_name: str,
    runner: str,
    duration_ms: int,
    findings: list[dict[str, Any]],
    passed_summary: str,
    failed_summary: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    has_findings = bool(findings)
    metrics = {
        "runner": runner,
        "duration_ms": duration_ms,
        "durationMs": duration_ms,
        "timedOut": False,
    }
    metrics.update(config)
    return {
        "total": max(len(findings), 1),
        "passed": 0 if has_findings else 1,
        "failed": len(findings),
        "errors": 0,
        "summary": failed_summary if has_findings else passed_summary,
        "details": findings
        or [
            _detail(
                name=check_name,
                status="passed",
                message=passed_summary,
                details={"runner": runner},
            )
        ],
        "metrics": metrics,
        "artifacts": {
            "stdout": "",
            "stderr": "",
            "exit_code": 0,
            "duration_ms": duration_ms,
            "durationMs": duration_ms,
            "timedOut": False,
        },
    }


def _parse_junit_report(path: Path) -> PytestCounts | None:
    if not path.exists():
        return None
    root = ElementTree.parse(path).getroot()
    suites = [root] if _tag_name(root) == "testsuite" else [
        element
        for element in root.iter()
        if _tag_name(element) == "testsuite"
    ]
    if not suites:
        return None
    total = sum(_int_attr(suite, "tests") for suite in suites)
    failed = sum(_int_attr(suite, "failures") for suite in suites)
    errors = sum(_int_attr(suite, "errors") for suite in suites)
    skipped = sum(_int_attr(suite, "skipped") for suite in suites)
    passed = max(total - failed - errors - skipped, 0)
    details = []
    for suite in suites:
        for case in suite:
            if _tag_name(case) != "testcase":
                continue
            failures = _children(case, "failure")
            errors_nodes = _children(case, "error")
            skipped_nodes = _children(case, "skipped")
            message_node = (errors_nodes or failures or skipped_nodes or [None])[0]
            details.append(
                _detail(
                    name=_case_name(case),
                    status=_case_status(
                        has_failures=bool(failures),
                        has_errors=bool(errors_nodes),
                    ),
                    message=_node_message(message_node),
                    path=case.attrib.get("file"),
                    line=_line_number(case.attrib.get("line")),
                    details={
                        "runner": "python_pytest",
                        "classname": case.attrib.get("classname"),
                        "time": case.attrib.get("time"),
                        "skipped": bool(skipped_nodes),
                    },
                )
            )
    return PytestCounts(total, passed, failed, errors, skipped, details)


def _parse_ruff_findings(stdout: str) -> list[dict[str, Any]] | None:
    try:
        parsed = json.loads(stdout or "[]")
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    return [finding for finding in parsed if isinstance(finding, dict)]


def _ruff_detail(finding: dict[str, Any]) -> dict[str, Any]:
    location = finding.get("location")
    if not isinstance(location, dict):
        location = {}
    code = _string(finding.get("code"), "ruff")
    message = _string(finding.get("message"), "Ruff lint issue")
    filename = _string(finding.get("filename"), "solution.py")
    return _detail(
        name=code,
        status="failed",
        message=message,
        path=Path(filename).name,
        line=_positive_int(location.get("row")),
        column=_positive_int(location.get("column")),
        details={
            "runner": "python_ruff_lint",
            "code": code,
            "url": finding.get("url"),
        },
    )


def _process_report(
    *,
    total: int,
    passed: int,
    failed: int,
    errors: int,
    summary: str,
    details: list[dict[str, Any]],
    metrics: dict[str, Any],
    stdout: str,
    stderr: str,
    exit_code: int | None,
    duration_ms: int,
    timed_out: bool,
) -> dict[str, Any]:
    stdout_value, stdout_truncated = _truncate(stdout)
    stderr_value, stderr_truncated = _truncate(stderr)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "summary": summary,
        "details": details,
        "metrics": metrics,
        "artifacts": {
            "stdout": stdout_value,
            "stderr": stderr_value,
            "stdout_truncated": stdout_truncated,
            "stderr_truncated": stderr_truncated,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "durationMs": duration_ms,
            "timedOut": timed_out,
        },
    }


def _check_result(
    check_type: str,
    status: str,
    score: int,
    report: dict[str, Any],
    duration_ms: int,
    timed_out: bool = False,
) -> dict[str, Any]:
    return {
        "check_type": check_type,
        "status": status,
        "score": score,
        "report": report,
        "execution_time_ms": duration_ms,
        "memory_used_kb": 0,
        "timedOut": timed_out,
    }


def _error_result(
    *,
    check_type: str,
    check_name: str,
    runner: str,
    message: str,
    duration_ms: int,
    error_type: str,
    detail_name: str | None = None,
    line: int | None = None,
    column: int | None = None,
) -> dict[str, Any]:
    report = {
        "total": 1,
        "passed": 0,
        "failed": 0,
        "errors": 1,
        "summary": message,
        "details": [
            _detail(
                name=detail_name or check_name,
                status="error",
                message=message,
                line=_positive_int(line),
                column=_positive_int(column),
                details={"runner": runner, "error_type": error_type},
            )
        ],
        "metrics": {
            "runner": runner,
            "duration_ms": duration_ms,
            "durationMs": duration_ms,
            "timedOut": False,
        },
        "artifacts": {
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "duration_ms": duration_ms,
            "durationMs": duration_ms,
            "timedOut": False,
        },
    }
    return _check_result(check_type, "error", 0, report, duration_ms)


def _detail(
    *,
    name: str,
    status: str,
    message: str | None = None,
    path: str | None = None,
    line: int | None = None,
    column: int | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "message": message,
        "path": path,
        "line": _positive_int(line),
        "column": _positive_int(column),
        "details": details or {},
    }


def _finding(
    *,
    runner: str,
    name: str,
    message: str,
    rule: str,
    value: str,
    line: int | None = None,
    column: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    details = {"runner": runner, "rule": rule, "value": value}
    if extra:
        details.update(extra)
    return _detail(
        name=name,
        status="failed",
        message=message,
        line=line,
        column=column,
        details=details,
    )


def _lint_metrics(
    config: LintConfig,
    exit_code: int | None,
    duration_ms: int,
    timeout_seconds: int,
    timed_out: bool,
) -> dict[str, Any]:
    return {
        "runner": "python_ruff_lint",
        "entry_file": config.entry_file,
        "select": config.select,
        "ignore": config.ignore,
        "line_length": config.line_length,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "durationMs": duration_ms,
        "timeout_seconds": timeout_seconds,
        "timedOut": timed_out,
    }


def _validate_python(payload: dict[str, Any]) -> None:
    if _string(payload.get("program_language"), "python").lower() != "python":
        raise CheckerConfigError("Python checker only supports python submissions")


def _config(payload: dict[str, Any]) -> dict[str, Any]:
    config = payload.get("config")
    if not isinstance(config, dict):
        check_type = _string(payload.get("check_type"), "check")
        raise CheckerConfigError(f"{check_type} config_json must be an object")
    return config


def _timeout_seconds(payload: dict[str, Any]) -> int:
    value = payload.get("timeout_seconds")
    if isinstance(value, int) and value > 0:
        return value
    return 10


def _runner_name(check_type: str) -> str:
    return {
        "tests": "python_pytest",
        "lint": "python_ruff_lint",
        "static": "python_static_ast",
        "architecture": "python_architecture_ast",
    }.get(check_type, "legacy_checker")


def _string(value: object, fallback: str) -> str:
    if isinstance(value, str) and value:
        return value
    return fallback


def _score(passed: int, total: int) -> int:
    if total <= 0:
        return 0
    return int((passed / total) * 100)


def _duration_ms(started_at: float) -> int:
    return max(int((time.perf_counter() - started_at) * 1000), 0)


def _error_summary(errors: int) -> str:
    suffix = "error" if errors == 1 else "errors"
    return f"Pytest finished with {errors} {suffix}"


def _issues_summary(prefix: str, count: int) -> str:
    suffix = "issue" if count == 1 else "issues"
    return f"{prefix} {count} {suffix}"


def _case_status(*, has_failures: bool, has_errors: bool) -> str:
    if has_errors:
        return "error"
    if has_failures:
        return "failed"
    return "passed"


def _case_name(case: ElementTree.Element) -> str:
    classname = case.attrib.get("classname")
    name = case.attrib.get("name", "testcase")
    if classname:
        return f"{classname}.{name}"
    return name


def _node_message(node: ElementTree.Element | None) -> str | None:
    if node is None:
        return None
    message = node.attrib.get("message") or node.text
    if message is None:
        return None
    return _truncate(message.strip())[0]


def _children(
    element: ElementTree.Element,
    tag_name: str,
) -> list[ElementTree.Element]:
    return [child for child in element if _tag_name(child) == tag_name]


def _tag_name(element: ElementTree.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _int_attr(element: ElementTree.Element, name: str) -> int:
    try:
        return int(element.attrib.get(name, "0"))
    except ValueError:
        return 0


def _line_number(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return _positive_int(int(value))
    except ValueError:
        return None


def _positive_int(value: object) -> int | None:
    if not isinstance(value, int) or value < 1:
        return None
    return value


def _normalize_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _truncate(value: str) -> tuple[str, bool]:
    if len(value) <= OUTPUT_LIMIT:
        return value, False
    return value[:OUTPUT_LIMIT], True


def _matched_import_from_name(
    node: ast.ImportFrom,
    forbidden_imports: set[str],
) -> str | None:
    module = node.module or ""
    candidates: list[str] = []
    if module:
        candidates.append(module)
        candidates.extend(f"{module}.{alias.name}" for alias in node.names)
    else:
        candidates.extend(alias.name for alias in node.names)
    return next(
        (
            candidate
            for candidate in candidates
            if _matches_module(candidate, forbidden_imports)
        ),
        None,
    )


def _matches_module(module_name: str, forbidden_imports: set[str]) -> bool:
    root_name = module_name.split(".", 1)[0]
    return any(
        module_name == forbidden
        or module_name.startswith(f"{forbidden}.")
        or root_name == forbidden
        for forbidden in forbidden_imports
    )


def _matches_call(call_name: str, forbidden_calls: set[str]) -> bool:
    return any(
        call_name == forbidden or call_name.endswith(f".{forbidden}")
        for forbidden in forbidden_calls
    )


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent_name = _call_name(node.value)
        if parent_name:
            return f"{parent_name}.{node.attr}"
        return node.attr
    return None


def _top_level_symbols(tree: ast.AST) -> set[str]:
    if not isinstance(tree, ast.Module):
        return set()
    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, SYMBOL_NODES):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                symbols.update(_assignment_names(target))
        elif isinstance(node, ast.AnnAssign):
            symbols.update(_assignment_names(node.target))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.add(alias.asname or alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                symbols.add(alias.asname or alias.name)
    return symbols


def _assignment_names(target: ast.AST) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        names: set[str] = set()
        for element in target.elts:
            names.update(_assignment_names(element))
        return names
    return set()


def _function_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    end_lineno = getattr(node, "end_lineno", None)
    if not isinstance(end_lineno, int):
        return 1
    return end_lineno - node.lineno + 1
