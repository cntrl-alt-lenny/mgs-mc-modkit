<div align="center">

<img src="assets/banner.svg" alt="MGS Master Collection Mod Kit — vanilla-faithful fixes for Steam Deck, Linux and Windows" width="100%">

<br><br>

[![Latest release](https://img.shields.io/github/v/release/cntrl-alt-lenny/mgs-mc-modkit?style=for-the-badge&color=4ade80&label=release)](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/cntrl-alt-lenny/mgs-mc-modkit/ci.yml?style=for-the-badge&label=CI&logo=github)](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/workflows/ci.yml)
![Steam Deck](https://img.shields.io/badge/Steam_Deck-verified-1A9FFF?style=for-the-badge&logo=steamdeck&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logoColor=white)
![Python](https://img.shields.io/badge/python3-no_deps-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Licence](https://img.shields.io/badge/licence-MIT-green?style=for-the-badge)

**The essential MGS 1 / 2 / 3 fixes, installed for you.**

Steam Deck · Linux · Windows — one double-click, nothing to configure, fully reversible

</div>

---

## Install

1. Install MGS1, MGS2 and/or MGS3 through Steam.

2. Download the matching shortcut:
   - **Windows:** [`Install-MGS-Mods.cmd`](Install-MGS-Mods.cmd). Double-click it. You need free [Python](https://www.python.org/downloads/) 3.
   - **Steam Deck/Linux:** [`Install-MGS-Mods.desktop`](Install-MGS-Mods.desktop). Put it on your Desktop, then right-click → **Properties → Permissions → Is executable**.

3. Run the shortcut. Choose your games, optionally select Better Audio files, and press **Install now**.

4. **Steam Deck/Linux only:** paste the launch options shown by the installer into Steam → each game → **Properties → Launch Options**:

   ```text
   MGS2 & MGS3: WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%
   MGS1:        WINEDLLOVERRIDES="dinput8=n,b;d3d11=n,b" %command%
   ```

   The installer offers **Copy to clipboard** and saves the same lines to `MGS Steam Launch Options.txt` on your Desktop. Without them, Linux/Proton will not load the mods.

Windows needs no launch options. Just play.

## What you get

| Game | Included fixes | Result |
|:--|:--|:--|
| **MGS1** | [MGSM2Fix](https://github.com/nuggslet/MGSM2Fix) `3.6.0` | High internal resolution, restored Western textures, no analog deadzone, skipped startup notices |
| **MGS2** | [MGSHDFix](https://github.com/ShizCalev/MGSHDFix) `4.1.0` + [Community Bugfix Compilation](https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation) `3.0.0` | Correct aspect ratio/FOV, lower CPU use, restored assets, high-quality cutscenes, launcher skip, and bug fixes |
| **MGS3** | [MGSHDFix](https://github.com/ShizCalev/MGSHDFix) `4.1.0` + [Community Bugfix Compilation](https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation) `2.0.1` | Correct aspect ratio/FOV, lower CPU use, restored assets, high-quality cutscenes, launcher skip, and bug fixes |

Everything is installed from the authors’ official releases. Nothing is rehosted here.

> **Vanilla-faithful:** the kit installs fixes and restorations only. AI-upscaled textures and gameplay-changing mods are deliberately excluded.

## Better Audio (optional)

The audio files are hosted on Nexus Mods, which requires a free account. Their author does not permit redistribution, so you download them yourself and point the installer at the files.

| Game | Download |
|:--|:--|
| MGS2 | **2.0 Full Version** for the complete restoration, or the smaller **2.0 Lite Version** |
| MGS3 | **Main file** (v1.0) **and** **Update 2.0** |
| MGS3 ending | **HQ Ending Cutscenes** is optional and off by default; those scenes may pause at the end and need a button press |

[MGS2 Better Audio](https://www.nexusmods.com/metalgearsolid2mc/mods/3) · [MGS3 Better Audio](https://www.nexusmods.com/metalgearsolid3mc/mods/4)

Files can live anywhere and be renamed. The installer checks their contents and refuses files belonging to the wrong game. Better Audio replaces some multi-GB originals that cannot be backed up; Steam → **Verify integrity** restores those originals if needed.

## Defaults

The installer is preset for a simple, console-like experience:

| Setting | Default |
|:--|:--|
| Button prompts | Steam Deck on Deck; Xbox elsewhere; PS5, PS2 and keyboard options available |
| Sound | Stereo |
| High-quality cutscenes | On |
| KONAMI intro logos | Skipped |
| Launcher | Skipped; games boot directly |

Use **Change settings…** if you want different prompts, 5.1 sound, or the logos back. Your choices are remembered.

## Repair or remove

Run the same shortcut again:

- **Install or repair mods** re-applies the selected setup and is also how you add audio later.
- **Remove the mods** restores backed-up originals and removes files installed by the kit.

Your saves are never touched. If a large Better Audio file was replaced, use Steam’s **Verify integrity** after removal. The shortcut is also the repair and uninstall button—keep it.

<details>
<summary><b>MGS1 first-boot recommendation</b></summary>

Choose **METAL GEAR SOLID (US)**, **Max** resolution, **Original / 4:3** screen size, and **Smoothing Off**. The version menu appears once; you can change versions later from the pause menu.

</details>

<details>
<summary><b>Quick troubleshooting</b></summary>

- **Mods do not load on Steam Deck/Linux:** check the launch options in step 4.
- **“Failed to read config key…”:** run `plugins/MGSHDFix Config Tool.exe` once and choose **Save and Exit**.
- **Want the KONAMI launcher back:** set `Skip Launcher=0` in `plugins/MGSHDFix.settings`.

Terminal uninstall: `python3 install.py --uninstall`.

</details>

## For maintainers

Pinned versions are checked weekly. Read [`docs/UPGRADING.md`](docs/UPGRADING.md) before changing a mod version; MGSHDFix updates require a matching settings template and full test run.

## Credits

The fixes come from **[ShizCalev](https://github.com/ShizCalev)**, **[Lyall](https://github.com/Lyall)**, **[nuggslet](https://github.com/nuggslet)** and **knight_killer**. This kit only automates installing their work—please endorse and star their projects.

**MIT** · [LICENSE](LICENSE)
