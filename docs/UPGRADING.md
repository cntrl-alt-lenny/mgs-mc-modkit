# Upgrading the pinned mods

> **Read this before changing any version number in `install.py`.**

The four MGS1–3 pinned mod versions are **a set, not four independent choices**.
MGS4 has its own separately coupled PatriotFix archive/settings set below. They
are pinned together because they depend on each other, and because MGSHDFix requires all runtime-read settings. The kit ships a
`MGSHDFix.settings` file matched to one
specific version of its Config Tool, and the mod **aborts initialization on a single
missing key**. C++ initial values do not provide missing-key fallback.

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

#### Static capture boundary

`python3 tools/capture_settings_schema.py <reviewed-checkout> --tag <tag> --tree <literal-commit>`
prints JSON only after successfully reading the whole reviewed `kTabs` initializer.
The caller must verify the checkout identity; the supplied tag/tree labels are
recorded, not authenticated by this tool. `source_sha256` hashes the original
bytes of both source files, including BOM and line endings. No source is rewritten.

The supported layouts are those reviewed at 4.1.0, 4.1.1 and 4.1.2: braced tab
and field initializers, canonical `ConfigKeys::*_Section` / `*_Setting` references,
literal string constants (including concatenation) and string aliases in one
unconditional `ConfigKeys` namespace. The whole namespace is checked: an
unrecognized declaration spelling, duplicate name, nested namespace, or
conditional/preprocessor context around its declarations stops capture rather
than allowing a referenced section, key, or choice value to disappear. The
namespace must be at global scope. The complete header context is checked:
only optional `#pragma once`, the completed `_CRT_SECURE_NO_WARNINGS` guard
(`#if !defined(...)`, its empty `#define`, then `#endif`), and the ordered
`<string>` / `<initializer_list>` includes are accepted before it. No other
includes, macros, enclosing namespaces, aliases or declarations are accepted.
After it, only an empty tail or the exact reviewed 4.1.0/4.1.1/4.1.2 lexical
token sequence is accepted. That shared tail contains controller lists,
language helpers and camera bounds; its SHA-256 fingerprint is in the tool,
and an offline copy is `tests/fixtures/hdfix-reviewed-header-tail.hpp`.
Comments and whitespace between tokens can vary; string contents and all
other tokens must match. Any tail change requires source-format review,
even if it appears unrelated to canonical keys. This is an explicit bounded
allowlist, not general C++ namespace or preprocessor support. Spacers and the
reviewed inline achievement Safety Switch row are outside the canonical schema.
Canonical `MG`-only fields are included: game flags control visibility, while
hidden controls are still serialized. Runtime-required fields must not be
filtered by the target game. Unknown game names, computed keys, new field
types, malformed initializers and unreviewed flag/preprocessor syntax stop
capture with an offending-construct error requesting source-format review. Do
not turn an error into a count-based guess.

Game expressions support `MG`, `MGS2`, `MGS3`, parentheses and bitwise OR, plus
`constexpr int` aliases and alias chains. The reviewed conditional form is
`#if defined(NAME)` / one alias declaration / `#else` / the same alias declaration
/ `#endif`. Capture takes the **union of both branches** and records resolved
`flag_unions` when aliases occur. It does not evaluate macros or assert which
branch an upstream release binary uses. In particular, 4.1.2's
`kFirstPersonViewGameFlags` union includes MGS3 through `MGS3_FPS_DEV`; this does
**not** establish MGS3 FPS support in a release build or a per-game export.
Nested/other directives and field declarations behind directives are unsupported.

Constraints remain bounded: explicit literal/ConfigKeys choice lists and integer
bounds written as integers or the two reviewed D3D11 limits are captured. Empty
choice lists and the reviewed launcher-controller iterator list are dynamic and
not captured. The reviewed `k3rdPersonMinCameraDistance` /
`k3rdPersonMaxCameraDistance` bounds remain opaque. Float bounds, defaults,
dynamic language/button/hotkey choices and actual generated per-game settings
remain unverified by static capture. Validate them against real Config Tool
exports before changing the coupled template, schema, constraints or pins.

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

This is the pinned baseline, with native compatibility still unproven. Batch 10
Windows logs exposed an incomplete kit schema; the three omitted runtime keys
are corrected by batch 11, subject to independent review and native retesting.
Any future version change must update the
whole coupled set, regenerate the settings template, and pass a real install →
launch → repair → uninstall check.

## MGS4's separate pinned set

MGSPatriotFix stable **0.2.2**, tree
`c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de`, uses the official
`MGS4_MGSPatriotFix_0.2.2.zip` (not the PW archive), SHA-256
`4f8fa5dd493c9d5d023fd4dfdcad39a2259b2aedf02685840751c263f497a6b1`.
Review version, official archive layout/checksum, runtime readers, Config Tool
saving, embedded fields/constraints/defaults and capture fixture together.
Do not change the MGS1–3 pins as part of a PatriotFix upgrade.

Authenticate the upstream tag, then use `tools/capture_patriot_schema.py` on that
exact source tree. Its byte allowlist authenticates the exact `.cpp`, `.hpp` and `.h` inventory
under `src/` and `ConfigTool/`, refusing additions, omissions and byte drift.
Build projects, resources, external dependencies and generated binaries are not
authenticated; this does not establish build or binary reproducibility. Audit
a changed input before extending this bounded allowlist.
Inspect `MGS4/winmm.dll`, `MGS4/scripts/MGSPatriotFix.asi`,
`Launcher/d3d11.dll`, `Launcher/scripts/MGSPatriotFix.asi` and root Config Tool.
The installer requires the exact reviewed file inventory and skips upstream's
placeholder `.log` files to preserve existing runtime diagnostics. An unknown
archive member, missing member or PW path stops before live payload writes.

`tools/refresh_checksums.py` includes PatriotFix; `tools/check_pins.py` remains
advisory. Regenerate both shortcuts, run complete offline checks, then follow
[native handoff](batches/evidence/14-mgs4-patriotfix/native-handoff.md) for fresh
install → export/boot/gameplay → repair → removal on Windows and Deck. Never
infer native compatibility from source capture, synthetic fixtures or CI.
