"""Reject extractor errors and missing extension translation units."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def validate(root: Path, report: Path) -> None:
    with report.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    errors = [row["detail"] for row in rows if row["kind"] == "error"]
    if errors:
        raise SystemExit("CodeQL extraction errors: " + "; ".join(errors))
    compiled = {row["detail"] for row in rows if row["kind"] == "compiled"}
    # These are the extension's source directories compiled by SConstruct.
    directories = ("", "core", "resources", "scene", "editor", "compat", "bridge")
    expected = {
        path.relative_to(root).as_posix()
        for directory in directories
        for path in (root / "src" / directory).glob("*.cpp")
    }
    missing = expected - compiled
    if not expected or missing:
        raise SystemExit(
            "Incomplete CodeQL extension coverage: " + ", ".join(sorted(missing))
        )
    print(f"CodeQL extraction OK ({len(expected)} extension translation units)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    validate(args.root, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
