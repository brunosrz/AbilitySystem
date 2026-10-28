"""Exercise metadata and package boundaries with an isolated addon fixture."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AssetLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addon = self.root / "addons/ability_system"
        self.addon.mkdir(parents=True)
        for name in (
            "plugin.cfg",
            "README.md",
            "LICENSE",
            "ability_system.gdextension",
        ):
            shutil.copy(ROOT / "addons/ability_system" / name, self.addon)
        (self.addon / "icons").mkdir()
        (self.addon / "icons/ASComponent.svg").write_text("<svg/>")
        # A declared Windows library, independent of the host platform.
        self.library = self.addon / "bin/ability_system.windows.editor.x86_64.dll"
        self.library.parent.mkdir()
        self.library.write_bytes(b"synthetic package fixture")
        self.original_config = (self.addon / "plugin.cfg").read_text()

    def config(self, old, new):
        (self.addon / "plugin.cfg").write_text(self.original_config.replace(old, new))

    def validate(self):
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "utility/validate_asset_library.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )

    def test_semver(self):
        valid = (
            "0.1.0",
            "1.2.3",
            "1.2.3-alpha.1",
            "1.2.3+build.01",
            "1.2.3-rc.1+sha.0123",
            "1.2.3-01a",
        )
        invalid = (
            "01.2.3",
            "1.02.3",
            "1.2.03",
            "1.2.3-alpha..1",
            "1.2.3-",
            "1.2.3-.alpha",
            "1.2.3-alpha.",
            "1.2.3-01",
            "1.2.3+",
            "1.2.3+build..1",
        )
        for text in valid + invalid:
            with self.subTest(version=text):
                self.config('version="0.1.0"', f'version="{text}"')
                result = self.validate()
                self.assertEqual(
                    result.returncode, 0 if text in valid else 1, result.stderr
                )
                if text in valid:
                    self.assertIn("asset-library validation: OK", result.stdout)
                else:
                    self.assertIn("invalid plugin version", result.stderr)

    def test_godot_minimum(self):
        for text in ("4.7", "4.8", "4.10", "4.99", "4.2", "4.6", "3.7", "5.0", "4.07"):
            with self.subTest(version=text):
                self.config('godot="4.7"', f'godot="{text}"')
                result = self.validate()
                self.assertEqual(
                    result.returncode,
                    0 if text in ("4.7", "4.8", "4.10", "4.99") else 1,
                    result.stderr,
                )
                if result.returncode:
                    self.assertIn("invalid Godot compatibility", result.stderr)

    def test_icon_traversal_is_rejected(self):
        (self.addon / "outside.svg").write_text("<svg/>")
        self.config('icon="icons/ASComponent.svg"', 'icon="icons/../outside.svg"')
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("plugin icon does not resolve inside the addon", result.stderr)

    def test_icon_symlink_is_rejected(self):
        target = self.root / "external.svg"
        target.write_text("<svg/>")
        (self.addon / "icons/escape.svg").symlink_to(target)
        self.config('icon="icons/ASComponent.svg"', 'icon="icons/escape.svg"')
        self.assertEqual(self.validate().returncode, 1)

    def test_declared_library_is_required(self):
        self.assertEqual(self.validate().returncode, 0)
        self.library.unlink()
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "no declared library for a supported platform exists inside the addon",
            result.stderr,
        )

    def test_undeclared_library_does_not_satisfy_gate(self):
        self.library.rename(self.library.with_name("undeclared.dll"))
        self.assertEqual(self.validate().returncode, 1)

    def test_library_outside_package_or_unsupported_platform_is_rejected(self):
        external = self.root / "external.dll"
        external.write_bytes(b"fixture")
        (self.addon / "escape.dll").symlink_to(external)
        for key, resource in (
            ("linux.debug.x86_64", "res://addons/ability_system/../../external.dll"),
            ("linux.debug.x86_64", "res://addons/ability_system/escape.dll"),
            (
                "unsupported.debug",
                "res://addons/ability_system/bin/ability_system.windows.editor.x86_64.dll",
            ),
        ):
            with self.subTest(key=key, resource=resource):
                (self.addon / "ability_system.gdextension").write_text(
                    f'[libraries]\n{key} = "{resource}"\n'
                )
                self.assertEqual(self.validate().returncode, 1)
