"""Validate release-line and Release Please configuration before publishing."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"invalid release configuration {path}: {error}") from error


def main() -> int:
    lines = load_json(ROOT / ".github" / "release-lines.json")
    versions: set[str] = set()
    for line_name in ("development", "maintenance"):
        line = lines.get(line_name)
        if not isinstance(line, dict):
            raise SystemExit(f"missing release line: {line_name}")
        branch = line.get("branch")
        config_name = line.get("release_please_config")
        manifest_name = line.get("release_please_manifest")
        if not all(
            isinstance(value, str) and value
            for value in (branch, config_name, manifest_name)
        ):
            raise SystemExit(f"incomplete release line: {line_name}")
        config = ROOT / str(config_name)
        manifest = ROOT / str(manifest_name)
        if not config.is_file() or not manifest.is_file():
            raise SystemExit(f"release files missing for {line_name}")
        package = load_json(manifest).get(".")
        if not isinstance(package, str) or not SEMVER.fullmatch(package):
            raise SystemExit(f"invalid manifest version for {line_name}: {package}")
        versions.add(package)
    if lines["development"]["branch"] == lines["maintenance"]["branch"]:
        raise SystemExit("development and maintenance branches must differ")
    version_file = ROOT / "VERSION"
    if not version_file.is_file() or not SEMVER.fullmatch(
        version_file.read_text().strip()
    ):
        raise SystemExit("VERSION must contain a stable semantic version")
    print(f"release configuration OK ({', '.join(sorted(versions))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
