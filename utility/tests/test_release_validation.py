"""Regression coverage for the shared release version and export gate."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml  # type: ignore[import]

from src import version


ROOT = Path(__file__).resolve().parents[2]


class VersionTests(unittest.TestCase):
    def test_version_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "PROJECT_VERSION"
            (root / "VERSION").write_text("9.8.7")
            self.assertEqual(version._read_version(path), (0, 1, 0))
            for text, expected in (
                ("1.2.3", (1, 2, 3)),
                (" \n1.2.3\t\n", (1, 2, 3)),
                ("1.2.3.4", (0, 1, 0)),
                ("1.two.3", (0, 1, 0)),
            ):
                with self.subTest(text=text):
                    path.write_text(text)
                    self.assertEqual(version._read_version(path), expected)


class ReleaseConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".github").mkdir()
        shutil.copy(ROOT / ".github/release-lines.json", self.root / ".github")
        for name in ("development", "maintenance"):
            for filename in (
                f"release-please-config.{name}.json",
                f".release-please-manifest.{name}.json",
            ):
                shutil.copy(ROOT / filename, self.root)
        (self.root / "src").mkdir()
        shutil.copy(ROOT / "src/version.py", self.root / "src")
        (self.root / "PROJECT_VERSION").write_text("1.2.3\n")

    def run_check(self):
        script = (
            "from pathlib import Path; import sys; "
            "from utility import check_release_config as check; "
            "check.ROOT = Path(sys.argv[1]); raise SystemExit(check.main())"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(self.root)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        return result.returncode, (result.stdout + result.stderr).strip()

    def test_shared_project_version(self):
        status, output = self.run_check()
        self.assertEqual(status, 0)
        self.assertIn("release configuration OK (", output)

    def test_config_drift_is_rejected_for_each_release_line(self):
        for name in ("development", "maintenance"):
            for source in ("VERSION", "src/version.py"):
                with self.subTest(line=name, source=source):
                    path = self.root / f"release-please-config.{name}.json"
                    original = path.read_text()
                    config = json.loads(original)
                    config["packages"]["."]["version-file"] = source
                    path.write_text(json.dumps(config))
                    status, output = self.run_check()
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        output, f"{name} version-file must be PROJECT_VERSION"
                    )
                    path.write_text(original)

    def test_missing_version(self):
        (self.root / "PROJECT_VERSION").unlink()
        self.assertEqual(
            self.run_check(),
            (1, "PROJECT_VERSION must contain a stable semantic version"),
        )

    def test_version_is_not_a_fallback(self):
        (self.root / "PROJECT_VERSION").rename(self.root / "VERSION")
        self.assertEqual(
            self.run_check(),
            (1, "PROJECT_VERSION must contain a stable semantic version"),
        )

    def test_non_stable_versions(self):
        for text in ("1.2.3-rc.1", "1.2.3+build", "1.2", "01.2.3"):
            with self.subTest(text=text):
                (self.root / "PROJECT_VERSION").write_text(text)
                self.assertEqual(
                    self.run_check(),
                    (1, "PROJECT_VERSION must contain a stable semantic version"),
                )

    def test_module_version_must_match(self):
        (self.root / "src/version.py").write_text("major, minor, patch = 9, 8, 7\n")
        self.assertEqual(
            self.run_check(), (1, "src/version.py must match PROJECT_VERSION")
        )

    def test_version_export_gate(self):
        action = yaml.safe_load(
            (ROOT / ".github/actions/init-version/action.yml").read_text()
        )
        script = next(
            step["run"]
            for step in action["runs"]["steps"]
            if step["name"] == "Set PLUGIN_VERSION"
        )
        for text in (None, "1.2.3-rc.1", "01.2.3", "1.2.3", " \n1.2.3\n"):
            with self.subTest(text=text):
                path = self.root / "PROJECT_VERSION"
                if text is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(text)
                env_file = self.root / "env"
                output_file = self.root / "output"
                env_file.write_text("")
                output_file.write_text("")
                result = subprocess.run(
                    ["bash", "-e", "-c", script],
                    cwd=self.root,
                    env={
                        **os.environ,
                        "GITHUB_ENV": str(env_file),
                        "GITHUB_OUTPUT": str(output_file),
                    },
                    capture_output=True,
                    text=True,
                )
                if text is None or text in ("1.2.3-rc.1", "01.2.3"):
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "PROJECT_VERSION must exist and contain a stable MAJOR.MINOR.PATCH version",
                        result.stderr,
                    )
                    self.assertEqual(env_file.read_text(), "")
                    self.assertEqual(output_file.read_text(), "")
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(env_file.read_text(), "PLUGIN_VERSION=1.2.3\n")
                    self.assertEqual(output_file.read_text(), "version=1.2.3\n")
