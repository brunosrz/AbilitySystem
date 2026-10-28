"""Validate the repository metadata required for a Godot Asset Library submission."""

from __future__ import annotations

import configparser
import argparse
import re
import sys
from pathlib import Path


NUMERIC = r"(?:0|[1-9][0-9]*)"
PRERELEASE = rf"(?:{NUMERIC}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    rf"{NUMERIC}\.{NUMERIC}\.{NUMERIC}"
    rf"(?:-{PRERELEASE}(?:\.{PRERELEASE})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
SUPPORTED_PLATFORMS = {"windows", "linux", "macos", "android", "ios", "web"}
REQUIRED_PLUGIN_FIELDS = ("name", "description", "author", "version", "godot", "icon")


def value(plugin: configparser.SectionProxy, key: str) -> str:
    """Read a Godot config value while accepting its quoted INI form."""

    return plugin.get(key, "").strip().strip('"')


def fail(message: str) -> None:
    print(f"asset-library validation: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root containing addons/ability_system",
    )
    args = argument_parser.parse_args()
    addon = args.root / "addons" / "ability_system"
    plugin_path = addon / "plugin.cfg"
    if not plugin_path.is_file():
        fail("addons/ability_system/plugin.cfg is missing")

    parser = configparser.ConfigParser()
    parser.read(plugin_path, encoding="utf-8")
    if not parser.has_section("plugin"):
        fail("plugin.cfg has no [plugin] section")

    plugin = parser["plugin"]
    missing = [field for field in REQUIRED_PLUGIN_FIELDS if not value(plugin, field)]
    if missing:
        fail(f"plugin.cfg is missing fields: {', '.join(missing)}")
    if not SEMVER.fullmatch(value(plugin, "version")):
        fail(f"invalid plugin version: {value(plugin, 'version')}")
    if not re.fullmatch(r"4\.(?:[7-9]|[1-9][0-9]+)", value(plugin, "godot")):
        fail(f"invalid Godot compatibility: {value(plugin, 'godot')}")

    icon = value(plugin, "icon")
    icon_path = (addon / icon).resolve()
    if (
        not icon.startswith("icons/")
        or not icon_path.is_relative_to((addon / "icons").resolve())
        or not icon_path.is_file()
    ):
        fail(f"plugin icon does not resolve inside the addon: {icon}")

    for required in ("README.md", "LICENSE", "ability_system.gdextension"):
        if not (addon / required).is_file():
            fail(f"required addon file is missing: {required}")

    extension = configparser.ConfigParser(interpolation=None)
    try:
        extension.read(addon / "ability_system.gdextension", encoding="utf-8")
    except configparser.Error as error:
        fail(f"invalid ability_system.gdextension: {error}")
    if not extension.has_section("libraries"):
        fail("ability_system.gdextension has no [libraries] section")
    prefix = "res://addons/ability_system/"
    for platform, resource in extension["libraries"].items():
        resource = resource.strip().strip('"')
        if platform.split(".")[0] not in SUPPORTED_PLATFORMS or not resource.startswith(
            prefix
        ):
            continue
        library = (addon / resource.removeprefix(prefix)).resolve()
        if library.is_relative_to(addon.resolve()) and library.is_file():
            break
    else:
        fail("no declared library for a supported platform exists inside the addon")

    forbidden = [
        path
        for path in addon.rglob("*")
        if path.is_file() and any(part in {".git", ".godot"} for part in path.parts)
    ]
    if forbidden:
        fail(f"generated or VCS files are present in the addon: {forbidden[0]}")

    print(
        f"asset-library validation: OK ({value(plugin, 'name')} {value(plugin, 'version')}, Godot {value(plugin, 'godot')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
