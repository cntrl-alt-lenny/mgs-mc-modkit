<div align="center">

<img src="assets/banner.svg" alt="MGS Master Collection Mod Kit — one-click vanilla-faithful fixes for Steam Deck / SteamOS" width="100%">

<br><br>

[![Latest release](https://img.shields.io/github/v/release/cntrl-alt-lenny/mgs-mc-deck-modkit?style=for-the-badge&color=4ade80&label=release)](https://github.com/cntrl-alt-lenny/mgs-mc-deck-modkit/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/cntrl-alt-lenny/mgs-mc-deck-modkit/ci.yml?style=for-the-badge&label=CI&logo=github)](https://github.com/cntrl-alt-lenny/mgs-mc-deck-modkit/actions/workflows/ci.yml)
![Steam Deck](https://img.shields.io/badge/Steam_Deck-verified-1A9FFF?style=for-the-badge&logo=steamdeck&logoColor=white)
![SteamOS](https://img.shields.io/badge/SteamOS-3.x-000000?style=for-the-badge&logo=steam&logoColor=white)
![Python](https://img.shields.io/badge/python3-no_deps-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Licence](https://img.shields.io/badge/licence-MIT-green?style=for-the-badge)

*One double-click. The whole setup. No guesswork.*

</div>

> **Why this exists** — the Steam releases of MGS 1/2/3 are transformed by a
> handful of community fixes, but wiring them up correctly on SteamOS is
> fiddly (MGSHDFix won't even boot without a config file its Windows-only tool
> generates). This kit makes the best *vanilla-faithful* setup as close to
> one-click as possible, and does it **safely** — checksummed downloads,
> staged extraction, backups, and a real uninstall.

## 🎯 What it does

- 🔍 **Auto-detects** your MGS 1 / 2 / 3 installs — internal drive, microSD, and secondary Steam libraries
- 📥 **Installs the essential fix mods** in the exact required order, straight from the authors' official releases
- ⚙️ **Writes a known-good config** (MGSHDFix won't launch without one) and applies the Konami launcher's own options so it can be skipped
- 🔒 **Verifies every download** against a pinned SHA-256 and stages/​path-checks archives before touching your game
- ♻️ **Transactional + reversible** — backups, rollback on failure, and a one-command `--uninstall`
- 🌿 **Vanilla-faithful only** — fixes and restorations, never AI-upscaled texture packs

## 🎮 Per-game

| Game | Installs | What it fixes / restores |
|:--|:--|:--|
| **MGS1** | MGSM2Fix | Analog deadzone removed, uncensored Western textures restored, startup notices skipped, custom/high internal resolution |
| **MGS2** | MGSHDFix + Community Bugfix + *(optional)* Better Audio | Native res & 16:10, corrected FOV/framebuffer, lower CPU, restored PS2 assets, launcher skipped, uncompressed audio *(also fixes a late-game cutscene crash)* |
| **MGS3** | MGSHDFix + Community Bugfix + *(optional)* Better Audio | Native res & 16:10, corrected FOV/framebuffer, lower CPU, restored PS2 assets, launcher skipped, uncompressed audio |

---

## ⚡ Quick start

<table>
<tr><td width="60" align="center"><h3>1</h3></td><td>
Download <a href="Install-MGS-Mods.desktop"><b><code>Install-MGS-Mods.desktop</code></b></a> and drop it on your Desktop.<br>
<sub>KDE blocks downloaded shortcuts until you allow them: <b>right-click → Properties → Permissions → tick "Is executable"</b>.</sub><br>
<sub>🔒 The shortcut downloads <code>install.py</code> from a <b>pinned GitHub release</b> and verifies its SHA-256 before running it — never an unchecked live script.</sub>
</td></tr>
<tr><td align="center"><h3>2</h3></td><td>
<i>(Recommended)</i> Grab the <b>Better Audio Mod</b> for each game from NexusMods (free login). You'll pick the files in the installer — Downloads, Google Drive, external storage, wherever — renamed is fine:<br><br>
🔊 <a href="https://www.nexusmods.com/metalgearsolid2mc/mods/3"><b>MGS2 Better Audio</b></a> — <i>Full Version</i> (v2.0)<br>
🔊 <a href="https://www.nexusmods.com/metalgearsolid3mc/mods/4"><b>MGS3 Better Audio</b></a> — <i>Base</i> (v1.0), <i>Update 2.0</i> (~25 MB, recommended), and optional <i>HQ Ending Cutscenes</i>.
<br><br><sub>The installer shows one checklist where <b>every component is independently selectable</b> — tick what you want (e.g. just Update 2.0 if you already have the base), then point at each file. An "Open Nexus page" button is there if you still need it.</sub>
</td></tr>
<tr><td align="center"><h3>3</h3></td><td>
<b>Double-click the installer.</b> Answer a few questions. Done.
</td></tr>
<tr><td align="center"><h3>4</h3></td><td>
In Steam, for <b>each</b> game → <i>Properties → Launch Options</i>, paste
<b>its</b> line:<br><br>
<b>MGS2 & MGS3:</b> <code>WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%</code><br>
<b>MGS1:</b> <code>WINEDLLOVERRIDES="dinput8=n,b;d3d11=n,b" %command%</code>
<br><br><sub>The installer offers to save these to <b><code>MGS Steam Launch Options.txt</code></b> on your Desktop, so you can copy-paste them without switching back here.</sub>
</td></tr>
</table>

> **Step 4 is the only manual bit.** Steam silently reverts config edits made
> while it's running, so no script can do it reliably.

---

## 📦 What you get

|  | |
|:--|:--|
| 🖥️ **True 16:10** | Native resolution, correct FOV, no pillarboxing (MGS2/3) |
| 🎨 **Restored PS2 assets** | Original textures & full-quality models put back |
| 🎬 **HQ cinematics** | Enabled for you — no launcher trip needed |
| 🔊 **Better audio** | Uncompressed PS3-quality sound — also fixes an MGS2 cutscene crash *(strongly recommended)* |
| 🎮 **Correct buttons** | Steam Deck glyphs instead of keyboard prompts |
| ⚡ **Straight in** | KONAMI logos and the launcher both skipped |
| 🔋 **Runs cool** | The high-CPU-usage fix, on by default |
| 🕹️ **MGS1 fixed too** | MGSM2Fix — analog deadzone removed, original uncensored textures restored, notices skipped |

> 🌿 **Vanilla-faithful by design.** Every mod here is a *fix* or a
> *restoration*. AI-upscaled texture packs are deliberately **not** included.

---

## 🧩 The stack

| # | Mod | Author |
|:-:|:--|:--|
| 1 | [MGSHDFix](https://github.com/ShizCalev/MGSHDFix) `3.1.0` *(MGS2/3)* | ShizCalev · *orig.* Lyall |
| 2 | Better Audio Mod *(strongly recommended)* · [MGS2](https://www.nexusmods.com/metalgearsolid2mc/mods/3) `2.0` / [MGS3](https://www.nexusmods.com/metalgearsolid3mc/mods/4) `2.0` | knight_killer |
| 3 | Community Bugfix Compilation — Base · [MGS2](https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation) `2.2.0` / [MGS3](https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation) `1.1.0` | ShizCalev |
| 4 | [MGSM2Fix](https://github.com/nuggslet/MGSM2Fix) `3.6.0` *(MGS1)* | nuggslet |

Installed in that exact order — it's required, and the kit enforces it.
Everything is fetched live from the authors' official releases; **nothing is
rehosted here.**

---

## 🔒 Safe by design

| | |
|:--|:--|
| ✅ **Checksummed downloads** | Every auto-fetched archive is verified against a pinned SHA-256 before it's touched — a corrupted or tampered file never reaches your game folder |
| ✅ **Transactional installs** | Archives are extracted to a staging area and every path is validated (no `../` traversal, no absolute paths, no symlinks) before anything is copied in |
| ✅ **Backups + rollback** | Fix-mod files are backed up and every change recorded, so a mid-install failure rolls that game back (and a failed re-install falls back to your previous working setup). All archives are downloaded *before* anything is written, so a dropped connection can't strand you |
| ✅ **One-command uninstall** | `python3 install.py --uninstall` reverses everything using the recorded manifest |
| ✅ **Tested** | A [CI](.github/workflows/ci.yml) test-suite covers discovery, every game combo, malicious/corrupt archives, rollback, idempotent re-installs and uninstall |

<sub>One honest caveat: the Better Audio Mod overwrites some multi-GB stock game
files, which are too large to back up. Those specific files are restored with
Steam's *Verify integrity* rather than by the kit — everything else is fully
reversible.</sub>

<sub>Run the tests yourself: `pip install pytest && python3 -m pytest tests/`
(needs `bsdtar`). Bumping a mod version? `python3 tools/refresh_checksums.py`
prints the new hashes.</sub>

<sub>🛠️ **Maintainers:** the shortcut pins the installer to release **`v1.5.0`**.
To cut a release, push a matching tag (`git tag v1.5.0 && git push --tags`) —
[`release.yml`](.github/workflows/release.yml) runs the tests, **fails if the
shortcut's baked-in tag/hash doesn't match `install.py`**, then publishes
`install.py` + a `SHA256SUMS` file. After editing `install.py`, update the
`TAG=`/`SHA=` values in `Install-MGS-Mods.desktop` (`sha256sum install.py`) and
bump the tag.</sub>

---

<details>
<summary><b>🔍 Why this kit exists</b></summary>

<br>

**MGSHDFix has no runtime defaults.** Without a complete `MGSHDFix.settings`
it refuses to launch, and it hard-aborts on any *single* missing key:

```
[MGSHDFix Config Helper] Failed to read config key 'Debug Logging'
in section 'Internal Settings': Section not found
```

That file can normally only be made by the mod's **Windows Config Tool** — a
GUI you'd have to wrestle through Proton. And its ini section names aren't the
tab labels the tool shows you (`[Internal Settings]`, `[Launcher Config]`,
`[Skip Logo Screens]`…), so hand-writing one doesn't work either.

This kit ships a canonical settings file captured from the real Config Tool,
verified **byte-for-byte** against a known-working install.

**The launcher is the other trap.** It's the only place to enable *high quality
cinematics* — so skipping it normally locks you out of that setting forever.
The kit writes the launcher's own save (`launcher_sv`, plain JSON) directly, so
you get the good cutscenes *and* skip the launcher.

</details>

<details>
<summary><b>🎚️ Options you'll be asked</b></summary>

<br>

| Option | Default |
|:--|:--|
| Button icons | `Steam Deck` — Xbox (Steam Machine / pads), PS5, PS2, Keyboard also offered |
| Audio output | `Stereo (2.0)` — right for handheld, docked *and* TV speakers. Pick 5.1 **only** with a real surround receiver/speaker setup |
| High-quality cinematics | **on** |
| Skip KONAMI intro logos | **on** |
| Skip the launcher | **on** |
| Mod update checks | off |

> 🚫 **No MGS3 high-res texture option:** Konami's official High Resolution
> Texture Pack can be *installed* on the Steam Deck but **cannot be used
> in-game** there, so on a detected Deck the kit keeps its launcher flag off.
> On other hardware an existing high-res-texture setup is left untouched.
> (The Bugfix Compilation's restored textures are unrelated and always
> installed.)
>
> 🔎 **Device detection:** the installer recognises a Steam Deck (DMI
> `Valve` + `Jupiter`/`Galileo`, or the `SteamDeck` env var) and shows what
> it detected on the confirm screen. Detection selects appropriate menu
> defaults and applies the Steam Deck-specific high-resolution-texture
> restriction — nothing else. Every mod works identically on Deck, Steam
> Machine, and any Linux PC, and a failed detection simply falls back to
> the generic defaults.

> 🖥️ **Docked / TV:** SteamOS may default a game to 1280×720. Set the game's
> *Properties → Game Resolution* to **Native** for full quality. Handheld needs
> no changes.
>
> 🌍 **Playing in another language?** The kit writes English defaults. Run
> `MGSHDFix Config Tool.exe` (in the game's `plugins/` folder) once to pick
> another region/language — MGSHDFix validates the pair and falls back safely.

Everything else stays at MGSHDFix's own defaults, which are already right for
the Deck.

</details>

<details>
<summary><b>🔊 Why the audio mod needs one click from you</b></summary>

<br>

It's **strongly recommended**, not just cosmetic: besides restoring the
PS3-quality audio, the MGS2 version replaces a corrupted audio file in the
stock port that can freeze or crash a late-game cutscene (MGSHDFix itself
checks for this fix and warns when it's absent).

It lives on NexusMods, which requires a free login, and **the author does not
permit it being mirrored** — that's the primary reason this kit will never
host or auto-fetch it (the 2–3 GB files also exceed GitHub's 2 GB release
limit).

**The components (each independently selectable):**

- **MGS2 Better Audio** — *Full Version* (v2.0).
- **MGS3 Better Audio — Base** (v1.0).
- **MGS3 Better Audio — Update 2.0** (~25 MB) — recommended patch, but
  optional. You can install it **on its own** if you already have the base
  from an earlier run.
- **MGS3 HQ Ending Cutscenes** (~178 MB) — optional, **off by default**.

**How selection works (redesigned after real Steam Deck testing):**

1. One **checklist** lists exactly those components for the games you chose.
   Tick any combination — nothing is forced, nothing blocks on anything else.
2. For each ticked item, a **Select file / Open Nexus page / Skip** dialog
   lets you point at the archive. It remembers the last folder and accepts
   files from **anywhere** (Downloads, Google Drive, external storage, a
   renamed copy).
3. Files are validated by **content**, and the installer tries to confirm each
   MGS3 archive's role (Base / Update / HQ) from its structure. When it can't
   prove the exact component it asks you to confirm rather than guessing, flags
   a likely wrong component or wrong game, and rejects the same file picked
   twice.
4. When several MGS3 components are chosen, install order is enforced —
   base → HQ Ending → **Update last** — and the confirmation screen plus the
   logs name each component (and its filename) explicitly.

🔊 **[MGS2 Better Audio Mod](https://www.nexusmods.com/metalgearsolid2mc/mods/3)**
&nbsp;·&nbsp;
🔊 **[MGS3 Better Audio Mod](https://www.nexusmods.com/metalgearsolid3mc/mods/4)**

Opening Nexus is always a button, never the default — the installer won't
nag you to open it after you've declined. Extraction runs inside a **progress
window** (Preparing → Extracting → Verifying → Complete), it verifies every
audio file landed on disk, and it records each component separately in the
manifest.

The optional MGS3 *HQ Ending Cutscenes* archive has one quirk, per its
author: the final two cutscenes **pause at the end and need a button press
(A/X) to continue** — which is why it defaults to **off** for a first
playthrough.

</details>

<details>
<summary><b>🕹️ MGS1: first boot & recommended settings</b></summary>

<br>

MGS1's "launcher" is the Master Collection's own **version-select menu**
(part of the game, unlike MGS2/3's separate Konami launcher). The kit sets
MGSM2Fix's launcher-skip, which **boots your last-launched version** — so the
menu appears on first boot for you to choose, then never again. To change
versions later, use the in-game pause menu.

**What to pick, first time:**

| Setting | Pick | Why |
|:--|:--|:--|
| **Game version** | **METAL GEAR SOLID (US)** | Full-speed 60 Hz NTSC in English. The EU release is 50 Hz PAL — it genuinely runs ~17% slower with borders. |
| Resolution / rendering | **Max** | M2's official internal upscale — sharp, era-authentic 3D, effortless for any modern device. |
| Screen size / aspect | Normal / Original (4:3) | Vanilla framing (side bars are correct). Never the stretch option. |
| Smoothing | Off | PS1 hardware had no texture filtering — off is the authentic sharp look. Taste, though. |
| Scanlines / wallpaper | Off / any | Pure cosmetics. |

MGSM2Fix's shipped defaults (which the kit keeps) already restore the
original western presentation — the censored Master Collection texture swaps
(Johnny, mosaic, ghosts, medicine) are all reverted, the analog deadzone is
removed, and startup notices are skipped.

</details>

<details>
<summary><b>🧹 Uninstalling & troubleshooting</b></summary>

<br>

**Clean uninstall (recommended):** re-run the installer with `--uninstall`:

```bash
python3 install.py --uninstall
```

Every install is **transactional** — the kit records exactly which files it
added and backs up any it overwrote in a hidden `mgs-modkit/` folder inside the
game directory. `--uninstall` reads that manifest, removes the files it added,
restores the originals it backed up, and clears the obsolete legacy
`MGSM2Fix.asi` that upstream warns can clash with the unified 3.x release. Your
game saves are never touched. (Multi-GB Better Audio assets are recorded but
not backed up — use *Verify integrity* below to restore those.)

**Manual revert to stock:** Steam → the game → *Properties → Installed Files →
Verify integrity of game files*. To also delete the added files by hand:

- **MGS2 / MGS3:** `winhttp.dll`, `wininet.dll`, `plugins/`, `mgs-modkit/`,
  `logs/`, `steam_appid.txt`
- **MGS1:** `d3d11.dll`, `dinput8.dll`, `MGSM2Fix64.asi`, `MGSM2Fix32.asi`,
  `MGSM2Fix.ini`, `mgs-modkit/` — and delete the obsolete `MGSM2Fix.asi` (a
  pre-unified build) if you see one, as it conflicts with newer releases.

**"Failed to read config key…"** — your settings file doesn't match your
MGSHDFix version. Run `MGSHDFix Config Tool.exe` in the game's `plugins/`
folder and hit *Save and Exit*.

**Mod doesn't load at all** — the launch options aren't set. See step 4.

**Want the launcher back?** `plugins/MGSHDFix.settings` → `Skip Launcher=0`.

**Reading the logs** — MGSHDFix writes `logs/MGSHDFix_Game.log` with every
setting it parsed. They contain embedded binary, so use `grep -a`.

**`No display-attached GPUs were detected`** — harmless on Deck/Proton, appears
every run.

**Versions are pinned on purpose** — the bundled settings file is matched to
MGSHDFix `3.1.0`. A future release could rename sections and break launching.

</details>

---

<div align="center">

### 🙏 Credits

All the real work belongs to **[ShizCalev](https://github.com/ShizCalev)**,
**[Lyall](https://github.com/Lyall)** and **knight_killer**.
<br>This kit only automates installing it — please endorse and star their work.

<br>

**MIT** · [LICENSE](LICENSE) · Requires only `python3`, `bsdtar`, `kdialog`/`zenity` — all stock on SteamOS

</div>
