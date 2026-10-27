"""Reject planning/reviewer metadata in PR title and body."""

from __future__ import annotations

import os
import re


FORBIDDEN = re.compile(
    r"\b(?:sprint|bloco|fase|coderabbit|copilot|claude|chatgpt)\b",
    re.IGNORECASE,
)


def main() -> int:
    title = os.environ.get("PR_TITLE", "")
    body = os.environ.get("PR_BODY", "")
    failures: list[str] = []
    if FORBIDDEN.search(title):
        failures.append(f"PR title contains planning/reviewer metadata: {title!r}")
    if FORBIDDEN.search(body):
        failures.append("PR body contains planning/reviewer metadata")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PR metadata check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
