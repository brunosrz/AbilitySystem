"""Regression checks for cache producers, required caches, and C++ extraction."""

import csv
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import yaml  # type: ignore[import]

from utility import check_codeql_extraction


ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


class CacheTests(unittest.TestCase):
    def test_packaging_keys_exactly_match_producer_matrix(self):
        producer_keys = set()
        for platform in ("windows", "linux", "macos", "android", "ios", "web"):
            job = workflow(f"{platform}_gdextension_builds.yml")["jobs"]["build"]
            matrix = job["strategy"]["matrix"]
            template = next(
                step["with"]["key"]
                for step in job["steps"]
                if step.get("name") == "Cache Build for Packaging"
            )
            for values in itertools.product(*matrix.values()):
                key = template
                for axis, value in zip(matrix, values):
                    key = key.replace("${{ matrix." + axis + " }}", value)
                producer_keys.add(key)
        restores = [
            step
            for step in workflow("package_plugin.yml")["jobs"]["package"]["steps"]
            if "/cache/restore@" in step.get("uses", "")
        ]
        self.assertEqual({step["with"]["key"] for step in restores}, producer_keys)
        self.assertTrue(
            all(step["with"].get("fail-on-cache-miss") is True for step in restores)
        )
        self.assertEqual(len(restores), len(producer_keys))

    def test_missing_required_cache_fails_gate(self):
        steps = workflow("package_plugin.yml")["jobs"]["package"]["steps"]
        gate = next(
            step for step in steps if step.get("name") == "Require all build caches"
        )
        required = json.loads(gate["env"]["REQUIRED_CACHE_HITS"])
        restore_ids = {
            step["id"] for step in steps if "/cache/restore@" in step.get("uses", "")
        }
        self.assertEqual(set(required), restore_ids)
        for name, expression in required.items():
            self.assertEqual(expression, "${{ steps." + name + ".outputs.cache-hit }}")
        for hit in ("true", "false", ""):
            with self.subTest(hit=hit):
                hits = dict.fromkeys(required, "true")
                hits[next(iter(hits))] = hit
                result = subprocess.run(
                    ["bash", "-e", "-c", gate["run"]],
                    env={**os.environ, "REQUIRED_CACHE_HITS": json.dumps(hits)},
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode, 0 if hit == "true" else 1, result.stderr
                )
                if hit != "true":
                    self.assertIn("Missing required build caches", result.stderr)

    def test_external_actions_in_changed_workflows_are_pinned(self):
        for name in (
            "codeql.yml",
            "package_plugin.yml",
            "runner.yml",
            "web_gdextension_builds.yml",
            "web_module_builds.yml",
            "asset_library_validation.yml",
        ):
            for job in workflow(name)["jobs"].values():
                for step in job.get("steps", []):
                    action = step.get("uses", "")
                    if action and not action.startswith("./"):
                        self.assertRegex(action, r"@[0-9a-f]{40}$", f"{name}: {action}")


class ExtractionTests(unittest.TestCase):
    def test_extraction_requires_all_sources_and_no_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/core").mkdir(parents=True)
            for name in ("src/register_types.cpp", "src/core/ability_system.cpp"):
                (root / name).touch()
            report = root / "report.csv"
            complete = [
                ("compiled", "src/register_types.cpp"),
                ("compiled", "src/core/ability_system.cpp"),
            ]
            for rows, error in (
                (complete, None),
                (complete[:1], "Incomplete CodeQL extension coverage"),
                (
                    complete
                    + [("error", "cannot open source file godot_cpp/classes/node.hpp")],
                    "CodeQL extraction errors",
                ),
                ([], "Incomplete CodeQL extension coverage"),
            ):
                with self.subTest(rows=rows):
                    with report.open("w", newline="") as output:
                        writer = csv.writer(output)
                        writer.writerow(("kind", "detail"))
                        writer.writerows(rows)
                    if error:
                        with self.assertRaisesRegex(SystemExit, re.escape(error)):
                            check_codeql_extraction.validate(root, report)
                    else:
                        check_codeql_extraction.validate(root, report)
