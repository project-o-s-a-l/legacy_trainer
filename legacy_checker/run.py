from __future__ import annotations

import json
import sys
from typing import Any

from legacy_checker.checks import run_check


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            payload = {}
        result = run_check(payload)
    except Exception as exc:
        result = _fatal_result(exc)

    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


def _fatal_result(exc: Exception) -> dict[str, Any]:
    message = f"checker fatal error: {exc}"
    return {
        "check_type": "unknown",
        "status": "error",
        "score": 0,
        "execution_time_ms": 0,
        "memory_used_kb": 0,
        "timedOut": False,
        "report": {
            "total": 1,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "summary": message,
            "details": [
                {
                    "name": "checker_fatal_error",
                    "status": "error",
                    "message": message,
                    "path": None,
                    "line": None,
                    "column": None,
                    "details": {
                        "runner": "legacy_checker",
                        "error_type": exc.__class__.__name__,
                    },
                }
            ],
            "metrics": {
                "runner": "legacy_checker",
                "duration_ms": 0,
                "durationMs": 0,
                "timedOut": False,
            },
            "artifacts": {
                "stdout": "",
                "stderr": "",
                "exit_code": None,
                "duration_ms": 0,
                "durationMs": 0,
                "timedOut": False,
            },
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
