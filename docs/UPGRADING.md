# Upgrading the pinned mods

> **Read this before changing any version number in `install.py`.**

The four pinned mod versions are **a set, not four independent choices**. They
are pinned together because they depend on each other, and because MGSHDFix has
no runtime defaults — the kit ships a `MGSHDFix.settings` file matched to one
specific version of its Config Tool, and the game **hard-aborts on a single
missing key**.

`tools/check_pins.py` (and the weekly `check-mod-versions` workflow) tells you
when something newer exists. It deliberately never edits anything.

---

## Why you can't bump them individually

Two separate couplings:

**1. The Bugfix Compilations delete fixes that MGSHDFix takes over.**
MGS2 Bugfix `3.0.0`'s own notes say *"Removed the Snake hair texture fix — this
issue has been completely fixed at the engine level by MGSHDFix"* and *"Removed
all GCX typo fixes — fixed by MGSHDFix's new string replacement feature."*

So pairing a **new** Bugfix pack with an **old** MGSHDFix silently loses those
fixes: the Bugfix pack no longer ships them and the old MGSHDFix never provided
them. Nothing errors. The game just quietly has bugs back.

**2. MGSHDFix major releases change the settings schema.**
`SETTINGS_TEMPLATE` in `install.py` is a schema-matched template for the pinned
MGSHDFix Config Tool. A major release adds and renames sections, and the mod
aborts on anything it can't find:

```
[MGSHDFix Config Helper] Failed to read config key 'Debug Logging'
in section 'Internal Settings': Section not found
```

For a future major release, regenerate the template with the real **Windows**
Config Tool. The ini section names are not the tab labels shown in its UI.

---

## The upgrade procedure

Do the whole set in one change. Budget an evening, not ten minutes.

### 1. Read every release note in between
Check what changed for each mod, and specifically look for:
- fixes moved from a Bugfix pack into MGSHDFix (tells you the versions are paired)
- changed install instructions (e.g. "delete `d3d11.dll` when updating")
- new or renamed settings sections

### 2. Regenerate `MGSHDFix.settings` — the long pole
On a Windows machine (or the Deck via Proton):

1. Install the new MGSHDFix into a copy of the game folder.
2. Run `plugins/MGSHDFix Config Tool.exe`.
3. Set the options to match the kit's defaults — see the defaults in `docs/SETTINGS.md` (Steam Deck buttons, Stereo, HQ cutscenes on,
   skip logos on, skip launcher on, **update checks off**).
4. Hit **Save and Exit** to write a fresh `plugins/MGSHDFix.settings`.
5. Paste its contents into `SETTINGS_TEMPLATE` in `install.py`, restoring the
   `@PLACEHOLDER@` tokens: `@BUTTON_ICONS@`, `@REGION@`, `@SKIP_LAUNCHER@`,
   `@SKIP_SPLASH@`, `@AUDIO_MODE@`, `@UPDATE_CHECK@`.
6. Capture the exact upstream fields with `tools/capture_settings_schema.py`;
   review its supported syntax, then update the fixture and embedded
   `SETTINGS_SCHEMA` / `SETTINGS_CONSTRAINTS`. Validate exact section/key names
   and values against the new export; section/key counts alone are insufficient.

> Keep CRLF line endings. The Config Tool writes them and the kit reproduces
> them byte-for-byte.

### 3. Update the versions and checksums
Bump `HDFIX_VERSION`, both `bugfix_version`/`bugfix_url` entries, and
`M2FIX_VERSION`/`M2FIX_TAG` as needed, then:

```bash
python3 tools/refresh_checksums.py     # prints the new SHA-256s
```

Paste each into the matching `*_SHA256` constant and re-run until it reports
all match.

### 4. Re-check the file layout assumptions
`verify_install()` asserts specific files exist. Confirm the new archives still
ship them:

```bash
bsdtar -tf MGSHDFix_<new>.zip     # expect winhttp.dll, wininet.dll,
                                  # plugins/MGSHDFix.asi
```

New extra files are fine — staged install handles them. **Missing** ones mean
`verify_install()` needs updating too.

### 5. Test
```bash
python3 -m pytest tests/ -q        # all green
```
Then a real install on a real machine: install → launch **both** MGS2 and MGS3
→ confirm they actually boot (this is the step that catches settings-schema
breakage) → re-run for repair → uninstall back to stock.

### 6. Release
Follow `docs/RELEASING.md`: bump `MODKIT_VERSION`, write release notes, run
`tools/pin_shortcuts.py`, commit, then tag after real-machine validation. CI
requires Linux and Windows checks on that tagged commit and refuses to publish
if either shortcut's pin disagrees with `install.py`.

---

## Current pinned set (August 2026)

| Mod | Pinned | Notes |
|:--|:--|:--|
| MGSHDFix | `4.1.0` | Includes the matching 4.x settings schema and the QoL fixes used by this kit. |
| MGS2 Bugfix | `3.0.0` | Paired with MGSHDFix 4.x. |
| MGS3 Bugfix | `2.0.1` | Paired with MGSHDFix 4.x. |
| MGSM2Fix | `v3.6` | Independent MGS1 component. |

This set is the known-good baseline. Any future version change must update the
whole coupled set, regenerate the settings template, and pass a real install →
launch → repair → uninstall check.
