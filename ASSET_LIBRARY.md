# Publishing to the Godot Asset Library

## Status

AbilitySystem is prepared for an initial public release as a GDExtension plugin
for **Godot 4.7+**. Version `0.1.0` should be presented as an initial release,
without guaranteeing stability for every game and platform.

## Submitted package

The package must contain `addons/ability_system/` with the following files:

- `plugin.cfg` with the name, description, author, version, compatibility, and icon;
- `ability_system.gdextension`;
- `README.md` in English and supplementary documentation in Portuguese;
- `LICENSE` with the MIT license text and copyright holder;
- icons and the native libraries available for the release platform.

The publishing workflow uses a custom download from a GitHub Release when the
package needs to load precompiled libraries. This avoids depending on submodules,
which are not included in GitHub's automatically generated ZIP archives.

## Submission form

Use the following values when submitting:

- repository: `https://github.com/brunosrz/AbilitySystem`;
- issues: `https://github.com/brunosrz/AbilitySystem/issues`;
- license: `MIT`;
- minimum version: `4.7`;
- asset version: the published tag, for example `0.1.0`;
- download: the direct URL of the corresponding release ZIP;
- icon: a direct `raw.githubusercontent.com` URL for a PNG/JPG or another accepted format.

Before submitting the asset, attach build, headless smoke test, and metadata
validation evidence from the same commit as the tag.
