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
`Show Pressure Level Overlay="Disabled"` value to the upstream boolean `0`. A complete legacy 128-key file also gains
the three omitted runtime keys: `MSX Skip Launcher Game="Metal Gear (MSX)"`,
`Crop Overscan Area=1` and `Correct Aspect Ratio to 4:3=1`, using upstream
4.1.0 defaults. Existing supported preferences survive; other missing keys,
partial migrations and malformed values are refused. Preview migrates in memory;
only the normal installation transaction writes the repaired file.

The shipped MGSHDFix schema contains 27 sections and 131 exact keys. It is derived
from `ConfigTool/tab_data.cpp` and `src/resources/config_keys.hpp` in MGSHDFix
4.1.0, independently of the installer template. Game flags hide controls in the UI;
the universal Config Tool still creates, reads and saves those controls. The
runtime reads all 131 keys (some conditionally), including all three MG-only
fields even in MGS2/MGS3. The earlier game-filtered fixture was incomplete. The capture records upstream
tree and source hashes in `tests/fixtures/hdfix-4.1.0-schema.json`. Runtime
validation checks exact keys, value types, and upstream choices/ranges where
the Config Tool declares them. Dynamic language/hotkey choices still require
the mod's own validation on a real boot.

To regenerate the independent capture from a local upstream checkout:

```bash
python tools/capture_settings_schema.py /path/to/MGSHDFix --tag 4.1.0 --tree f4f662d67a2a033dee0877e436a0fe65eb719e0b
```

This writes a candidate JSON to stdout for review. Update the fixture and the
installer's embedded schema together after authenticating the source and reviewing runtime readers and saving logic.
Native per-game exports and Windows/Deck initialization remain required release
evidence; static completeness does not prove a successful game boot.
Upstream Config Tool definitions are by Afevis and contributors, under MIT.

## MGS4 / PatriotFix 0.2.2

The independent capture has 8 sections / 28 exact keys, including hidden PW
controls. `ConfigTool/main.cpp` creates every non-spacer control and saves all
of them; game flags control visibility. Runtime readers include conditional
launcher/controller keys and PW values. No PW game support is installed.
`tools/capture_patriot_schema.py` checks the exact Git tree plus a byte allowlist
and inventory of all reviewed upstream C++ source before deriving keys, defaults,
choices, integer/float bounds and language pairs. Any source change refuses and
requires a new source review. Capture never reads this installer's defaults.

```bash
python3 tools/capture_patriot_schema.py /path/to/MGSPatriotFix
```

The kit uses one transactional writer for root `MGSPatriotFix.settings`, with
CRLF. Defaults differ deliberately from upstream: filtering **8** (the hooks only
replace existing values of 8, making 8 a no-op), pause on focus loss **on**, skip
launcher and in-game logos **on**, update checks **off**. Motion blur and dynamic
resolution remain enabled, shadows use **0 / original**, mouse sensitivity **1.0**,
raw mouse and DS3 **off**, button icons **AUTO**, menu buttons **Default**, language
**eu/en**. Hidden PW fields retain upstream defaults. No frame-rate override exists.

Before installing, Change settings offers MGS4 button icons, menu buttons, shadow
resolution, filtering, logo skipping, raw mouse, DS3 and visual overrides.
Repair preserves all supported values, including manual languages, float mouse
sensitivities, diagnostic toggles and hidden PW choices. Only explicitly selected
options change, and update checks always remain off. Reset discards custom mod
settings separately. Unknown/missing/duplicate keys, invalid region/language pairs,
unsupported choices, non-finite floats and out-of-range values refuse.

MGS4 game saves at `mgs4_savedata_win` and launcher saves are never edited or
synthesized. Language/controller/launcher choices are handled by PatriotFix itself.
The Config Tool's fullscreen optimization setting also writes Windows registry
compatibility flags when it saves; the kit does not reproduce or remove those
registry effects. Native exports and boots are pending; source completeness is
not proof of runtime compatibility.
