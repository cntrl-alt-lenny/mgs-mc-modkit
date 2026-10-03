# Settings and repair

Fresh installs use Steam Deck buttons on Deck, Xbox buttons elsewhere, stereo sound,
HQ cutscenes, launcher skipping and skipped intro logos. Choose **Change settings…**
to apply selected options across the games being installed. Each game's existing
choices appear separately on the review screen.

Repair preserves every supported MGSHDFix setting, including language, render
resolution, hotkeys and manually changed options. MGS1's existing MGSM2Fix INI
values are merged into the pinned release's defaults. Both mods' own update
checks stay off so their versions continue to match the kit's configuration.

**Reset to recommended settings** is a separate review-screen action. It replaces
custom mod settings with this kit's defaults. The review screen updates before
you press **Install now**. Launcher save preferences not managed by the kit remain
unchanged. MGS3 on Steam Deck disables the unsupported official HQ texture flag;
desktop installs preserve it. Internal launcher rendering and upscaling stay at
Original because MGSHDFix handles resolution.

Unsupported keys or malformed settings stop repair before replacement. Use the
Config Tool shipped with the pinned release to correct them. Keep a copy of
your current configuration first. The kit migrates the old template's incorrect
`Show Pressure Level Overlay="Disabled"` value to the upstream boolean `0`.

The shipped MGSHDFix schema contains 27 sections and 128 exact keys. It is derived
from `ConfigTool/tab_data.cpp` and `src/resources/config_keys.hpp` in MGSHDFix
4.1.0, independently of the installer template. The capture records upstream
tree and source hashes in `tests/fixtures/hdfix-4.1.0-schema.json`. Runtime
validation checks exact keys, value types, and upstream choices/ranges where
the Config Tool declares them. Dynamic language/hotkey choices still require
the mod's own validation on a real boot.

To regenerate the independent capture from a local upstream checkout:

```bash
python tools/capture_settings_schema.py /path/to/MGSHDFix --tag 4.1.0 --tree f4f662d67a2a033dee0877e436a0fe65eb719e0b
```

This writes a candidate JSON to stdout for review. Update the fixture and the
installer's embedded schema together only after comparing a Config Tool export.
Upstream Config Tool definitions are by Afevis and contributors, under MIT.
