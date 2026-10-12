#!/usr/bin/env python3
"""
Metal Gear Solid 1, 2 & 3 (Master Collection) — Mod Kit
=======================================================
A guided, dependency-free installer for the "essential" vanilla-faithful mod
stack on the Steam Deck, any SteamOS / Linux Steam install, and Windows 10/11.

One codebase, both platforms: dialogs come from kdialog/zenity on Linux and
tkinter on Windows; archives are unpacked by bsdtar, which Windows ships in
System32 as tar.exe. On Windows the mods load natively, so the Proton
launch-options step below does not exist there at all.

It will:
  1. Auto-detect your MGS1 / MGS2 / MGS3 Master Collection installs
     (incl. microSD and secondary libraries).
  2. MGS2/MGS3: install MGSHDFix (resolution / 16:10 / FOV / CPU fixes).
  3. MGS2/MGS3: install the Community Bugfix Compilation (Base) — restores the
     original PS2 textures/models and fixes the port's broken assets.
  4. MGS2/MGS3: optionally install the Better Audio Mod from a zip you supply
     (it lives on NexusMods, which requires a login, so it cannot be fetched
     automatically).
  5. MGS2/MGS3: write a schema-matched MGSHDFix.settings file.
  6. MGS2/MGS3: set the Konami launcher's own options — including "high
     quality cinematics" — so the launcher can be skipped entirely.
  7. MGS1: install MGSM2Fix (M2-emulator fix: analog deadzone removal,
     censored-texture restorations, skippable notices, custom resolution).

Steps 5 and 6 provide the runtime configuration MGSHDFix requires. A missing
section or key aborts mod initialization. The kit reconstructs its template
from the pinned Config Tool definitions and runtime readers; INI section names
are not the UI tab names. Native Config Tool exports and game boots remain
separate validation requirements.

Mods are downloaded live from their official GitHub releases — nothing is
rehosted here. Every auto-downloaded archive is checked against a pinned
SHA-256 before it is touched (see *_SHA256 below).

Installs are TRANSACTIONAL. Each archive is extracted to a staging folder and
every path is validated (no absolute paths, no `../` traversal, no symlinks)
before anything is copied into the live game directory. Overwritten originals
are backed up and every change is recorded in a manifest, so a mid-install
failure rolls back cleanly and the mods can be removed again later.

Because the machine can lose power mid-write, an intent journal is flushed to
disk before any file is moved into the game folder, and backups are never
overwritten — the copy closest to the user's original always wins. A record we
cannot parse is treated as a hard stop, never as "no previous install".

Run it again any time: if a previous install is found you are asked whether to
install/repair or remove the mods, so the shortcut stays useful and is never
deleted.

On Linux it deliberately does NOT set Steam launch options: Steam rewrites its
config from memory and will silently revert edits made while it is running.
The one line you must paste is shown at the end and saved to a file on your
Desktop. (Windows needs no launch options — the mods load natively.)

Requirements: python3 and bsdtar — both preinstalled on SteamOS; on Windows,
tar.exe is built in and Python is a free install. No pip packages, no admin.

Run it:                    python3 install.py
Skip straight to removal:  python3 install.py --uninstall
"""

from __future__ import annotations

import hashlib
import configparser
import math
import traceback
import threading
import time
import uuid
import io
import queue
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# BEGIN EMBEDDED INSTALL PLAN
# Game-neutral, versioned planning lifecycle (also embedded in install.py).
from contextlib import ExitStack
from dataclasses import dataclass


class ReplanRequired(RuntimeError):
    """Confirmed inputs changed; collect and confirm a fresh plan."""


@dataclass(frozen=True)
class AudioAcceptance:
    source: str
    sha256: str
    game: str
    role: str
    classification: str
    explicit: bool


@dataclass(frozen=True)
class PlanPackage:
    name: str
    version: str
    source: str
    sha256: str
    role: str = "package"
    acceptance: object = None


@dataclass(frozen=True)
class PlanGame:
    key: str
    path: str
    steam_root: str
    settings: str
    packages: tuple
    inputs: str
    incompatibilities: tuple = ()


@dataclass(frozen=True)
class InstallPlan:
    games: tuple
    schema: int = 1
    profile: str = "vanilla-faithful"

    def validate(self):
        if self.schema != 1 or self.profile != "vanilla-faithful" or not self.games:
            raise ValueError("Unsupported or empty installation plan")
        if len({g.key for g in self.games}) != len(self.games):
            raise ValueError("Duplicate games in installation plan")
        if len({g.path for g in self.games}) != len(self.games):
            raise ValueError("Games cannot share a destination")
        for game in self.games:
            if game.incompatibilities:
                raise ValueError("Incompatible plan: " + "; ".join(game.incompatibilities))
            if not game.packages:
                raise ValueError("Game has no payloads")
            for package in game.packages:
                if len(package.sha256) != 64 or any(
                        c not in "0123456789abcdef" for c in package.sha256):
                    raise ValueError("Payload requires an exact SHA-256 identity")
                if package.role != "package":
                    accepted = package.acceptance
                    if (not isinstance(accepted, AudioAcceptance) or
                            (accepted.source, accepted.sha256, accepted.game, accepted.role) !=
                            (package.source, package.sha256, game.key, package.role) or
                            accepted.classification not in
                            ("ok", "unknown_mod", "missing_identity", "mismatch", "ambiguous") or
                            (accepted.classification != "ok" and accepted.explicit is not True)):
                        raise ReplanRequired("Supplied audio acceptance is missing or changed; select and confirm again")


@dataclass(frozen=True)
class PreparedGame:
    game: PlanGame
    actions: tuple
    identities: tuple
    mods: tuple
    required_bytes: int


@dataclass(frozen=True)
class PreparedPlan:
    plan: InstallPlan
    games: tuple


def prepare_plan(plan, adapter, workspace):
    """Stage every game before allowing the executor to open a transaction."""
    plan.validate()
    adapter.recheck(plan)
    games = []
    for index, game in enumerate(plan.games):
        adapter.check_cancelled()
        games.append(adapter.prepare(game, workspace, index))
    prepared = PreparedPlan(plan, tuple(games))
    adapter.recheck(plan)
    adapter.check_prepared(prepared)
    adapter.check_space(prepared)
    return prepared


def execute_plan(prepared, adapter, outcomes):
    """No UI callbacks: locks, recheck all inputs, then independent commits."""
    prepared.plan.validate()
    if tuple(g.game for g in prepared.games) != prepared.plan.games:
        raise ValueError("Prepared games do not match plan order")
    with ExitStack() as locks:
        # A stable lock order prevents competing plans from deadlocking.
        for game in sorted(prepared.plan.games, key=lambda g: g.path):
            locks.enter_context(adapter.lock(game))
        adapter.recheck(prepared.plan)
        adapter.check_prepared(prepared)
        adapter.check_space(prepared)
        for index, game in enumerate(prepared.games):
            adapter.check_cancelled()
            adapter.execute(game, index, outcomes)
# END EMBEDDED INSTALL PLAN

UA = "Mozilla/5.0 mgs-mc-modkit"

MODKIT_VERSION = "2.3.0"

# One codebase, two platforms. On Windows the mods load natively (no Proton,
# so no WINEDLLOVERRIDES launch options at all) and the dialogs come from
# tkinter, which ships with every python.org / Microsoft Store Python.
# Read at call time (not captured) so tests can monkeypatch it.
IS_WINDOWS = os.name == "nt"


def find_tar() -> str | None:
    """The archive tool. Must be bsdtar — GNU tar cannot read .zip files.

    Linux/SteamOS ship it as `bsdtar`; Windows 10+ ships it in System32 as
    `tar.exe`, which IS bsdtar (libarchive). A plain `tar` that is GNU tar is
    rejected rather than half-working.
    """
    p = shutil.which("bsdtar")
    if p:
        return p
    p = shutil.which("tar")
    if p:
        try:
            r = subprocess.run([p, "--version"], capture_output=True,
                               text=True, timeout=15)
            if "bsdtar" in (r.stdout + r.stderr).lower():
                return p
        except (OSError, subprocess.SubprocessError):
            pass
    return None


# Resolved once at startup by main(); tests and library callers get the same
# lazy default the first time an archive helper runs.
TAR: str | None = None


def tar_cmd() -> str:
    global TAR
    if TAR is None:
        TAR = find_tar() or "bsdtar"
    return TAR

# Directory (inside each game folder) where this kit records what it installed,
# keeps backups of any files it overwrote, and stages archives before copying
# them into place. It is the anchor for repair/uninstall — see InstallTxn.
MODKIT_DIRNAME = "mgs-modkit"
MANIFEST_NAME = "manifest.json"
# Written just before files are moved into the game folder and removed on
# commit/rollback. Its only job is to survive a power loss or SIGKILL so the
# next run knows those files are OURS, not the game's originals.
JOURNAL_NAME = "in-progress.json"

# Overwritten originals larger than this are recorded but NOT copied into the
# backup folder — backing up multi-GB game assets (the Better Audio Mod
# replaces some) would double disk usage for no real benefit, since Steam's
# "Verify integrity of game files" restores them for free. Small fix files
# (dlls, .asi, .ini, save files) are always backed up so uninstall is exact.
BACKUP_MAX_BYTES = 64 * 1024 * 1024

# ---------------------------------------------------------------------------
# Pinned versions.
#
# These versions are pinned ON PURPOSE. The bundled MGSHDFix.settings
# below matches MGSHDFix 4.1.0's Config Tool schema, and a future MGSHDFix
# release may rename ini sections/keys and abort mod initialization.
# Pinning prevents silent upgrades; it does not prove runtime compatibility.
# To move to a newer MGSHDFix, bump HDFIX_VERSION and regenerate the settings
# file with the Config Tool (see README).
# ---------------------------------------------------------------------------
HDFIX_VERSION = "4.1.0"
HDFIX_URL = (
    "https://github.com/ShizCalev/MGSHDFix/releases/download/"
    f"{HDFIX_VERSION}/MGSHDFix_{HDFIX_VERSION}.zip"
)
# SHA-256 of the release asset above, so a tampered/truncated download is
# caught before it touches the game folder. Regenerate with `sha256sum` after
# bumping a version (see tools/refresh_checksums.py).
HDFIX_SHA256 = "413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523"

# MGS1 (M2 emulator) fix — nuggslet's MGSM2Fix. Ships its own MGSM2Fix.ini
# whose defaults are already vanilla-faithful (censored-texture restorations
# on, analog deadzone removal, notice-skip), so we install it as-is.
M2FIX_VERSION = "3.6.0"
M2FIX_TAG = "v3.6"
M2FIX_URL = (
    "https://github.com/nuggslet/MGSM2Fix/releases/download/"
    f"{M2FIX_TAG}/MGSM2Fix_{M2FIX_VERSION}.zip"
)
M2FIX_SHA256 = "a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d"

GAMES = {
    "mgs2": {
        "key": "mgs2",
        "name": "Metal Gear Solid 2: Sons of Liberty",
        "short": "MGS2",
        "appid": "2131640",
        "dirname": "MGS2",
        "exe": "METAL GEAR SOLID2.exe",
        # Region value the Config Tool writes for this title's option list.
        "region": "eu",
        "bugfix_version": "3.0.0",
        "bugfix_url": (
            "https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation/"
            "releases/download/3.0.0/"
            "MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip"
        ),
        "bugfix_sha256":
            "a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003",
        "bugfix_asi": "MGS2-Community-Bugfix-Compilation.asi",
        "audio_page": "https://www.nexusmods.com/metalgearsolid2mc/mods/3",
    },
    "mgs3": {
        "key": "mgs3",
        "name": "Metal Gear Solid 3: Snake Eater",
        "short": "MGS3",
        "appid": "2131650",
        "dirname": "MGS3",
        "exe": "METAL GEAR SOLID3.exe",
        "region": "us",
        "bugfix_version": "2.0.1",
        "bugfix_url": (
            "https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation/"
            "releases/download/2.0.1/"
            "MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip"
        ),
        "bugfix_sha256":
            "a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769",
        "bugfix_asi": "MGS3-Community-Bugfix-Compilation.asi",
        "audio_page": "https://www.nexusmods.com/metalgearsolid3mc/mods/4",
    },
    "mgs1": {
        "key": "mgs1",
        "kind": "m2fix",
        "name": "Metal Gear Solid (1)",
        "short": "MGS1",
        "appid": "2131630",
        "dirname": "MGS1",
        "exe": "METAL GEAR SOLID.exe",
        "launch": 'WINEDLLOVERRIDES="dinput8=n,b;d3d11=n,b" %command%',
    },
}

LAUNCH_OPTIONS = 'WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%'

# Better Audio lives on NexusMods (free login, no mirroring allowed), so the
# user supplies the archives. Nexus download filenames end in
# -<modid>-<major>-<minor>-<timestamp>.<ext>; the modid identifies the mod
# page and is used as corroborating evidence (never the sole check) that a
# selected file is for the right game. See the Better Audio section below for
# the per-game component model and install order.
#
#   MGS2 (mod 3): choose either "Full Version" v2.0 or the smaller "Lite
#                 Version" v2.0.
#   MGS3 (mod 4): the main mod (v1.0, NOT obsolete) PLUS a required small
#                 "Update 2.0", and an OPTIONAL "HQ Ending Cutscenes" archive.
NEXUS_SUFFIX = re.compile(r"-(\d+)-(\d+)-(\d+)-(\d{9,11})\.(?:zip|7z|rar)$",
                          re.IGNORECASE)

# ---------------------------------------------------------------------------
# Canonical MGSHDFix.settings (MGSHDFix 4.1.0).
#
# Reconstructed from the pinned release's Config Tool field definitions — 131
# keys across 27 sections. Placeholders (@NAME@) are substituted at write time.
# Written with CRLF line endings, as the Config Tool writes it.
#
# The section names are the INI schema, not the tab labels shown in the Config
# Tool's UI. Getting these wrong aborts the mod's configuration initialization.
# ---------------------------------------------------------------------------
SETTINGS_TEMPLATE = """\
[Bugfixes]
Boost Reverb Volume=1
Depth of Field Blur Strength=10.0
Fix  High  CPU  Usage="Full"
Fix Achievement Stat Tracking=1
Fix Aiming After Equip=1
Fix Aiming On Full Tilt=1
Fix Alt-Tab Loading Bugs=1
Fix Broken PS2 Visual Effects=1
Fix Depth of Field=1
Fix Film Grain=1
Fix M92 Laser Origin in FPV=1
Fix Motion Trails="Full (Gameplay + Cutscenes)"
Fix Mouse Cursor Showing=1
Reverb Volume Multiplier=1.4

[CAUTION - THIS WILL RESET ALL ACHIEVEMENTS]
Reset All Achievements=0

[Camera Positioning]
Disable HD Collection Camera Positioning=0
HD Collection Camera Toggle="F6"

[Caption Settings]
Caption Opacity (%)=100
Caption Outline Opacity (%)=100
Caption Size (%)=100

[Controller Settings]
Button Icons="@BUTTON_ICONS@"
Dualshock 2 && 3 Controller Support=0
DualShock Rumble Strength (%)=100
Restore PS2 Pressure Sensitive Binds=0
Set Menu OK && Cancel Button="Default"

[DISABLE STEAM ACHIEVEMENTS]
Disable Unlocking Steam Achievements=0

[Damaged Steam Cloud Save Data Fix]
Enable Console Notification When Fixed=1
Fix Mode="Move Outdated Save Data to Backup Folder"

[Debugging]
Debug Logging=0
Start Game in Developer Menu=0

[Difficulty Restoration]
Enable Grenade Cooking=0
Restore PS2 Solidus Choking Difficulty="Disabled"
Toggle Grenade Cooking="Num9"

[Enable Game Warnings]
Warn When FSR Upscaling is Enabled=1
Warn When Game is Muted=1
Warn When Missing Major Bugfix Mods=1
Warn When Save Files Are Read-Only=1
Warn When Save Folders Not Writable=1
Warn When Windows Slideshow Enabled=1

[Enhancements and Tweaks]
Anisotropic Filtering Level=16
Correct Aspect Ratio to 4:3=1
Correct Gamma Levels=1
Crop Overscan Area=1
Enable SMAA Anti-Aliasing=1
Nearest Neighbor Texture Filtering=0
Reduce Photosensitive Effects=0

[First Person Shooter Mode]
Enable First Person Shooter Mode=0
First Person Shooter - Movement Enabled By Default=1
Keep First Person View Across Rooms=0
Tap to Keep First Person View Active=0
Toggle First Person Shooter Mode="Right"
Toggle First Person Shooter Movement="Down"
Toggle Tap for First Person View="Up"

[Hotkeys]
Capture Hotkeys While Alt Tabbed=1
Cycle Wireframe Mode="End"
Return to Developer Menu="F8"
Toggle Vector Line Fixes="Insert"

[Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)]
Render Height=0
Render Width=0

[Keep Aiming After Firing]
Always Keep Aiming=0
While Holding Lock On=1
While in FPS Mode=0
While in First Person=1

[Language Settings]
Game Language="en"
Game Region="@REGION@"

[Launcher and Splashscreens]
MSX Skip Launcher Game="Metal Gear (MSX)"
Skip In-Game Splashscreens=@SKIP_SPLASH@
Skip Launcher=@SKIP_LAUNCHER@
Skip Launcher Splashscreens=@SKIP_SPLASH@

[MGS2 Community Bugfix Compilation Integration]
Restore Title Screen 2 Color Swapping=1
Retro MSX Colonel Sprite="Disabled"

[Model Quality && Level of Detail Enhancements]
Always Show Grass=1
Always Show Weapon Shell Casings=1
Custom Grass Distance Multiplier=1.0
Force High Quality Characters=1
Increase Shadow Resolution=1
Make Snake's Bandana Heavier=0
Show Soft Particles=1
Toggle Always Show Grass="Page Up"

[Mouse Sensitivity]
Override Mouse Sensitivity=0
X Multiplier=1
Y Multiplier=1

[Speedrunner Settings]
Fix In-Game Timer Loading Pause=1
Force RTC Hostage Type="Normal"
Gameplay Stats Overlay="Disabled"
Restore SoL Elevator Glitch=0
Show Pressure Level Overlay=0

[System Specific Fixes]
Audio Output Mode="@AUDIO_MODE@"
Disable Windows Fullscreen Optimization=0
Force Dedicated GPU=1
Limit Game to 2 CPU Cores=0

[Third Person Freecam]
Camera - Zoom In Hotkey="WheelUp"
Camera - Zoom Out Hotkey="WheelDown"
Camera - Zoom Reset Hotkey="Mouse4"
Camera - Zoom Speed=25
Camera - Zoom Step Amount=250
Enable Third Person Freecam=0
Horizontal Camera Sensitivity=0.6
Inherit Camera Rotation=0
Inherit Camera Rotation Toggle="NumMultiply"
Max Camera Distance=4000
Third Person View Toggle="Mouse5"
Vertical Camera Sensitivity=0.4

[Ultra-Wide / 16:10+]
Fix Aspect Ratio=1
Fix FOV=1
Fix Framebuffer=1
Lock HUD && Movies to 16:9=0

[Update Notifications]
Check For MGSHDFix Updates=@UPDATE_CHECK@
In-Game Update Notifications=1

[Various]
Camera Triggers Steam Screenshot=1
Custom Lifebar Name="LIFE"
Enable Radar in Snake Tales=0
Fix Vamp Punch Damage Type=0
Force Sunglasses="Normal"
High Frequency Blade Anywhere=0
Pause On Focus Loss=0
Restore Japanese Phone Ringtone=1
Restore Main Menu Voiceovers=1
Restore Node DoB && Bloodtype Entry=1
Restore Original Dogtag Names=1
Restore PS2 Memory Card Strings=0
Restore SoL Radar Rotation=0
T.Goggle Color Cycle Hotkey="Num7"
Thermal Goggle Default Palette="Substance"
Thermal Goggle Palette Swapping=0
Use Character Names for Lifebar=0
Use Custom Lifebar Name=0

[Window Settings]
Enable Resolution Overrides=1
Fullscreen, Borderless, and Windowed="Borderless Fullscreen"
Window Height=0
Window Width=0

"""

# The MGSHDFix release whose Config Tool source defines the template above.
# MGSHDFix aborts mod initialization on a missing key; schema changes between major
# releases, so this MUST equal HDFIX_VERSION. A test enforces that — which is
# a guard against an isolated version bump, not proof of a native game boot.
SETTINGS_CAPTURED_FROM = "4.1.0"

SETTINGS_EXPECTED_SECTIONS = 27
SETTINGS_EXPECTED_KEYS = 131

# Derived independently from the pinned upstream Config Tool field definitions.
SETTINGS_SCHEMA = {'Bugfixes': {'Boost Reverb Volume': 'Bool',
              'Depth of Field Blur Strength': 'Float',
              'Fix  High  CPU  Usage': 'Choice',
              'Fix Achievement Stat Tracking': 'Bool',
              'Fix Aiming After Equip': 'Bool',
              'Fix Aiming On Full Tilt': 'Bool',
              'Fix Alt-Tab Loading Bugs': 'Bool',
              'Fix Broken PS2 Visual Effects': 'Bool',
              'Fix Depth of Field': 'Bool',
              'Fix Film Grain': 'Bool',
              'Fix M92 Laser Origin in FPV': 'Bool',
              'Fix Motion Trails': 'Choice',
              'Fix Mouse Cursor Showing': 'Bool',
              'Reverb Volume Multiplier': 'Float'},
 'CAUTION - THIS WILL RESET ALL ACHIEVEMENTS': {'Reset All Achievements': 'Bool'},
 'Camera Positioning': {'Disable HD Collection Camera Positioning': 'Bool',
                        'HD Collection Camera Toggle': 'Hotkey'},
 'Caption Settings': {'Caption Opacity (%)': 'Int',
                      'Caption Outline Opacity (%)': 'Int',
                      'Caption Size (%)': 'Int'},
 'Controller Settings': {'Button Icons': 'Choice',
                         'DualShock Rumble Strength (%)': 'Int',
                         'Dualshock 2 && 3 Controller Support': 'Bool',
                         'Restore PS2 Pressure Sensitive Binds': 'Bool',
                         'Set Menu OK && Cancel Button': 'Choice'},
 'DISABLE STEAM ACHIEVEMENTS': {'Disable Unlocking Steam Achievements': 'Bool'},
 'Damaged Steam Cloud Save Data Fix': {'Enable Console Notification When Fixed': 'Bool',
                                       'Fix Mode': 'Choice'},
 'Debugging': {'Debug Logging': 'Bool', 'Start Game in Developer Menu': 'Bool'},
 'Difficulty Restoration': {'Enable Grenade Cooking': 'Bool',
                            'Restore PS2 Solidus Choking Difficulty': 'Choice',
                            'Toggle Grenade Cooking': 'Hotkey'},
 'Enable Game Warnings': {'Warn When FSR Upscaling is Enabled': 'Bool',
                          'Warn When Game is Muted': 'Bool',
                          'Warn When Missing Major Bugfix Mods': 'Bool',
                          'Warn When Save Files Are Read-Only': 'Bool',
                          'Warn When Save Folders Not Writable': 'Bool',
                          'Warn When Windows Slideshow Enabled': 'Bool'},
 'Enhancements and Tweaks': {'Anisotropic Filtering Level': 'Int',
                             'Correct Aspect Ratio to 4:3': 'Bool',
                             'Correct Gamma Levels': 'Bool',
                             'Crop Overscan Area': 'Bool',
                             'Enable SMAA Anti-Aliasing': 'Bool',
                             'Nearest Neighbor Texture Filtering': 'Bool',
                             'Reduce Photosensitive Effects': 'Bool'},
 'First Person Shooter Mode': {'Enable First Person Shooter Mode': 'Bool',
                               'First Person Shooter - Movement Enabled By Default': 'Bool',
                               'Keep First Person View Across Rooms': 'Bool',
                               'Tap to Keep First Person View Active': 'Bool',
                               'Toggle First Person Shooter Mode': 'Hotkey',
                               'Toggle First Person Shooter Movement': 'Hotkey',
                               'Toggle Tap for First Person View': 'Hotkey'},
 'Hotkeys': {'Capture Hotkeys While Alt Tabbed': 'Bool',
             'Cycle Wireframe Mode': 'Hotkey',
             'Return to Developer Menu': 'Hotkey',
             'Toggle Vector Line Fixes': 'Hotkey'},
 'Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)': {'Render Height': 'Int',
                                                                                                 'Render Width': 'Int'},
 'Keep Aiming After Firing': {'Always Keep Aiming': 'Bool',
                              'While Holding Lock On': 'Bool',
                              'While in FPS Mode': 'Bool',
                              'While in First Person': 'Bool'},
 'Language Settings': {'Game Language': 'Choice', 'Game Region': 'Choice'},
 'Launcher and Splashscreens': {'MSX Skip Launcher Game': 'Choice',
                                'Skip In-Game Splashscreens': 'Bool',
                                'Skip Launcher': 'Bool',
                                'Skip Launcher Splashscreens': 'Bool'},
 'MGS2 Community Bugfix Compilation Integration': {'Restore Title Screen 2 Color Swapping': 'Bool',
                                                   'Retro MSX Colonel Sprite': 'Choice'},
 'Model Quality && Level of Detail Enhancements': {'Always Show Grass': 'Bool',
                                                   'Always Show Weapon Shell Casings': 'Bool',
                                                   'Custom Grass Distance Multiplier': 'Float',
                                                   'Force High Quality Characters': 'Bool',
                                                   'Increase Shadow Resolution': 'Bool',
                                                   "Make Snake's Bandana Heavier": 'Bool',
                                                   'Show Soft Particles': 'Bool',
                                                   'Toggle Always Show Grass': 'Hotkey'},
 'Mouse Sensitivity': {'Override Mouse Sensitivity': 'Bool',
                       'X Multiplier': 'Int',
                       'Y Multiplier': 'Int'},
 'Speedrunner Settings': {'Fix In-Game Timer Loading Pause': 'Bool',
                          'Force RTC Hostage Type': 'Choice',
                          'Gameplay Stats Overlay': 'Choice',
                          'Restore SoL Elevator Glitch': 'Bool',
                          'Show Pressure Level Overlay': 'Bool'},
 'System Specific Fixes': {'Audio Output Mode': 'Choice',
                           'Disable Windows Fullscreen Optimization': 'Bool',
                           'Force Dedicated GPU': 'Bool',
                           'Limit Game to 2 CPU Cores': 'Bool'},
 'Third Person Freecam': {'Camera - Zoom In Hotkey': 'Hotkey',
                          'Camera - Zoom Out Hotkey': 'Hotkey',
                          'Camera - Zoom Reset Hotkey': 'Hotkey',
                          'Camera - Zoom Speed': 'Int',
                          'Camera - Zoom Step Amount': 'Int',
                          'Enable Third Person Freecam': 'Bool',
                          'Horizontal Camera Sensitivity': 'Float',
                          'Inherit Camera Rotation': 'Bool',
                          'Inherit Camera Rotation Toggle': 'Hotkey',
                          'Max Camera Distance': 'Int',
                          'Third Person View Toggle': 'Hotkey',
                          'Vertical Camera Sensitivity': 'Float'},
 'Ultra-Wide / 16:10+': {'Fix Aspect Ratio': 'Bool',
                         'Fix FOV': 'Bool',
                         'Fix Framebuffer': 'Bool',
                         'Lock HUD && Movies to 16:9': 'Bool'},
 'Update Notifications': {'Check For MGSHDFix Updates': 'Bool',
                          'In-Game Update Notifications': 'Bool'},
 'Various': {'Camera Triggers Steam Screenshot': 'Bool',
             'Custom Lifebar Name': 'Str',
             'Enable Radar in Snake Tales': 'Bool',
             'Fix Vamp Punch Damage Type': 'Bool',
             'Force Sunglasses': 'Choice',
             'High Frequency Blade Anywhere': 'Bool',
             'Pause On Focus Loss': 'Bool',
             'Restore Japanese Phone Ringtone': 'Bool',
             'Restore Main Menu Voiceovers': 'Bool',
             'Restore Node DoB && Bloodtype Entry': 'Bool',
             'Restore Original Dogtag Names': 'Bool',
             'Restore PS2 Memory Card Strings': 'Bool',
             'Restore SoL Radar Rotation': 'Bool',
             'T.Goggle Color Cycle Hotkey': 'Hotkey',
             'Thermal Goggle Default Palette': 'Choice',
             'Thermal Goggle Palette Swapping': 'Bool',
             'Use Character Names for Lifebar': 'Bool',
             'Use Custom Lifebar Name': 'Bool'},
 'Window Settings': {'Enable Resolution Overrides': 'Bool',
                     'Fullscreen, Borderless, and Windowed': 'Choice',
                     'Window Height': 'Int',
                     'Window Width': 'Int'}}
SETTINGS_CONSTRAINTS = {'Bugfixes': {'Fix  High  CPU  Usage': {'choices': ['Full', 'Half', 'Disabled']},
              'Fix Motion Trails': {'choices': ['Full (Gameplay + Cutscenes)',
                                                'Cutscenes Only',
                                                'Disabled']}},
 'Launcher and Splashscreens': {'MSX Skip Launcher Game': {'choices': ['Metal Gear (MSX)',
                                                                       'Metal Gear 2: Solid Snake']}},
 'System Specific Fixes': {'Audio Output Mode': {'choices': ['Stereo (2.0)', 'Surround Sound (5.1)']}},
 'Damaged Steam Cloud Save Data Fix': {'Fix Mode': {'choices': ['Move Outdated Save Data to Backup '
                                                                'Folder',
                                                                'Delete Outdated Save Data',
                                                                'Disable Damaged Save Data Fix']}},
 'Controller Settings': {'Set Menu OK && Cancel Button': {'choices': ['Default',
                                                                      'East for OK',
                                                                      'South for OK']},
                         'DualShock Rumble Strength (%)': {'range': [0, 200]}},
 'Window Settings': {'Window Width': {'range': [0, 16384]},
                     'Fullscreen, Borderless, and Windowed': {'choices': ['Exclusive Fullscreen',
                                                                          'Borderless Fullscreen',
                                                                          'Borderless Windowed',
                                                                          'Windowed (with borders)']},
                     'Window Height': {'range': [0, 16384]}},
 'Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)': {'Render Width': {'range': [0,
                                                                                                                            16384]},
                                                                                                 'Render Height': {'range': [0,
                                                                                                                             16384]}},
 'Enhancements and Tweaks': {'Anisotropic Filtering Level': {'range': [0, 16]}},
 'Various': {'Force Sunglasses': {'choices': ['Normal', 'Always', 'Never']},
             'Thermal Goggle Default Palette': {'choices': ['Substance',
                                                            'Sons of Liberty',
                                                            'Splinter Cell',
                                                            'White Hot',
                                                            'Black Hot']}},
 'Caption Settings': {'Caption Size (%)': {'range': [1, 100]},
                      'Caption Opacity (%)': {'range': [0, 100]},
                      'Caption Outline Opacity (%)': {'range': [0, 100]}},
 'Speedrunner Settings': {'Gameplay Stats Overlay': {'choices': ['Disabled',
                                                                 'Top Left',
                                                                 'Top Right',
                                                                 'Bottom Left',
                                                                 'Bottom Right']},
                          'Force RTC Hostage Type': {'choices': ['Normal',
                                                                 'Kato-chan',
                                                                 'Old Beauties',
                                                                 'Jennifer']}},
 'MGS2 Community Bugfix Compilation Integration': {'Retro MSX Colonel Sprite': {'choices': ['Disabled',
                                                                                            'MSX2',
                                                                                            'Subsistence']}},
 'Difficulty Restoration': {'Restore PS2 Solidus Choking Difficulty': {'choices': ['Disabled',
                                                                                   'Duration Increase '
                                                                                   'Only',
                                                                                   'Life Reduction Only',
                                                                                   'Full Restoration']}},
 'Third Person Freecam': {'Camera - Zoom Speed': {'range': [1, 500]}},
 'Mouse Sensitivity': {'X Multiplier': {'range': [1, 100]}, 'Y Multiplier': {'range': [1, 100]}}}

# ---------------------------------------------------------------------------
# The Konami launcher's own settings.
#
# The launcher persists its options to
#   <game>/<name>_savedata_win/<steamid64>/launcher/launcher_sv
# which is plain JSON with a UTF-8 BOM, stored as two parallel arrays:
#   {"keyList":["HiresoMovie",...],"valueList":["1",...]}
#
# The keys we care about:
#   HiresoMovie    1 = "high quality" cinematics  (the one everyone wants)
#   HiresoRender   internal resolution   -> 0, MGSHDFix owns resolution
#   HiresoUpScale  internal upscaling    -> 0, ditto
#   HiresoTexture  high-res textures (MGS3 only)
#
# Writing this ourselves is what lets the kit skip the launcher entirely:
# otherwise the launcher is the ONLY place those options can be set.
#
# Templates below are used only when no save exists yet (a fresh install).
# When one already exists we patch it in place and leave everything else —
# volume, language, MGS2's big ScenarioSave blob — untouched.
# ---------------------------------------------------------------------------
LAUNCHER_TEMPLATES = {
    "mgs2": (
        ["GDPRHash", "firstStart", "languageLauncher", "HiresoPreset",
         "launcherMasterVolume", "launcherMute", "HiresoRender",
         "HiresoUpScale", "HiresoMovie", "prevPlayLanguage",
         "prevPlayLanguage2", "prevGameRegion", "prevSelectStartUpNumber"],
        ["first", "0", "1", "2", "10", "0", "0", "0", "1", "2", "0", "2", "-1"],
    ),
    "mgs3": (
        ["GDPRHash", "firstStart", "languageLauncher", "HiresoPreset",
         "HiresoRender", "HiresoUpScale", "HiresoMovie", "HiresoTexture",
         "launcherMasterVolume", "launcherMute", "prevPlayLanguage",
         "prevPlayLanguage2", "prevGameRegion", "prevSelectStartUpNumber"],
        ["first", "0", "1", "2", "0", "0", "1", "0", "10", "0", "2", "0",
         "1", "-1"],
    ),
}

STEAMID64_BASE = 76561197960265728


# ---------------------------------------------------------------------------
# Tiny GUI abstraction: prefer kdialog (KDE/Deck desktop), fall back to zenity,
# then to a plain-terminal prompt so the script still works headless.
# ---------------------------------------------------------------------------
class UI:
    # Class-level defaults so a UI built by any route always has them.
    kind = "term"
    _degraded = False

    def __init__(self) -> None:
        if IS_WINDOWS:
            # tkinter ships with python.org and Microsoft Store Pythons. If it
            # is missing (a stripped custom build), the terminal UI still works
            # end to end in the console window the .cmd opens.
            self.kind = "tk" if self._tk_root_ok() else "term"
        else:
            # Without a display, every kdialog/zenity call exits non-zero:
            # info() and error() vanish and yesno() reads as "No", so the run
            # would abort with no visible reason (a real problem when SSH'd
            # into a Deck). Fall back to the terminal, which works end to end.
            has_display = bool(os.environ.get("DISPLAY")
                               or os.environ.get("WAYLAND_DISPLAY"))
            self.kind = (
                "kdialog" if has_display and shutil.which("kdialog")
                else "zenity" if has_display and shutil.which("zenity")
                else "term"
            )
        # The folder the file picker opens in — starts at Downloads, then
        # follows wherever the user last picked a file, so choosing several
        # archives in a row (e.g. MGS3 base + Update 2.0) stays quick even if
        # they live on external storage or a synced folder.
        dl = Path.home() / "Downloads"
        self.last_dir = dl if dl.is_dir() else Path.home()
        self._degraded = False      # set when a dialog tool fails mid-run

    def _run(self, args: list[str]) -> tuple[int, str]:
        """Run a dialog command, telling tool FAILURE apart from user CANCEL.

        This distinction matters a lot: a cancel legitimately means "stop", but
        a broken dialog tool returning non-zero would look identical and quit
        the installer instantly with no visible reason. When the tool itself
        fails we drop to the terminal and let the caller retry there.
        """
        try:
            p = subprocess.run(args, capture_output=True, text=True)
        except OSError as e:
            self._degrade(f"{args[0]} could not be started ({e})")
            return 1, ""
        if p.returncode != 0 and p.stderr.strip():
            # Cancel is a silent non-zero; output on stderr means it broke.
            self._degrade(p.stderr.strip().splitlines()[0])
            return 1, ""
        return p.returncode, p.stdout.strip()

    def _degrade(self, why: str) -> None:
        if self.kind == "term":
            return
        print(f"\n[!] The pop-up windows aren't working here ({why}).")
        print("[!] Carrying on in this terminal window instead.\n")
        self.kind = "term"
        self._degraded = True

    def _retryable(self, fn, *a, **k):
        """Run a dialog; if the tool broke, run it again in terminal mode."""
        try:
            out = fn(*a, **k)
        except Exception as e:
            if self.kind == "term":
                raise                       # terminal prompts must not be eaten
            self._degrade(f"dialog failed: {e.__class__.__name__}")
            out = fn(*a, **k)
            self._degraded = False
            return out
        if self._degraded:
            self._degraded = False
            out = fn(*a, **k)
        return out

    # -- tkinter backend (Windows) ---------------------------------------
    _tk_root = None

    def _tk_root_ok(self) -> bool:
        """Create (once) the hidden tk root window; False if tk is unusable."""
        if self._tk_root is not None:
            return True
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            self._tk_root = root
            return True
        except Exception:
            return False

    def _tk_modal(self, title: str, build):
        """Show a small modal window; `build(top, done)` fills it in.

        `done(value)` closes the window and makes _tk_modal return value.
        Closing the window any other way returns None (a cancel).
        """
        import tkinter as tk
        result = [None]
        top = tk.Toplevel(self._tk_root)
        top.title(title)
        top.attributes("-topmost", True)     # not behind the console window
        top.resizable(False, False)

        def done(value):
            result[0] = value
            top.destroy()

        build(top, done)
        top.update_idletasks()
        # Centre on screen.
        w, h = top.winfo_reqwidth(), top.winfo_reqheight()
        x = (top.winfo_screenwidth() - w) // 2
        y = (top.winfo_screenheight() - h) // 3
        top.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        top.grab_set()
        top.wait_window()
        return result[0]

    def _tk_choices(self, title: str, text: str, items, multi: bool):
        """Shared body for menu (single-choice) and checklist (multi)."""
        import tkinter as tk

        def build(top, done):
            tk.Label(top, text=text, justify="left", wraplength=460,
                     padx=14, pady=10, anchor="w").pack(fill="x")
            body = tk.Frame(top, padx=14)
            body.pack(fill="both", expand=True)
            if multi:
                vars_ = []
                for tag, label, checked in items:
                    v = tk.BooleanVar(value=checked)
                    tk.Checkbutton(body, text=label, variable=v,
                                   anchor="w").pack(fill="x")
                    vars_.append((tag, v))

                def ok():
                    done([t for t, v in vars_ if v.get()])
            else:
                lb = tk.Listbox(body, height=min(len(items), 8),
                                exportselection=False, activestyle="dotbox")
                for _tag, label in items:
                    lb.insert("end", label)
                lb.selection_set(0)
                lb.pack(fill="both", expand=True)
                lb.bind("<Double-Button-1>", lambda _e: ok())

                def ok():
                    sel = lb.curselection()
                    done(items[sel[0]][0] if sel else None)
            btns = tk.Frame(top, pady=10)
            btns.pack()
            tk.Button(btns, text="OK", width=10, command=ok,
                      default="active").pack(side="left", padx=6)
            tk.Button(btns, text="Cancel", width=10,
                      command=lambda: done(None)).pack(side="left", padx=6)
            top.bind("<Return>", lambda _e: ok())
            top.bind("<Escape>", lambda _e: done(None))

        return self._tk_modal(title, build)

    def _info_impl(self, text: str, title: str = "MGS Mod Kit") -> None:
        if self.kind == "tk":
            from tkinter import messagebox
            messagebox.showinfo(title, text, parent=self._tk_root)
        elif self.kind == "kdialog":
            self._run(["kdialog", "--title", title, "--msgbox", text])
        elif self.kind == "zenity":
            self._run(["zenity", "--info", "--title", title,
                       "--no-wrap", "--text", text])
        else:
            print(f"\n=== {title} ===\n{text}\n")

    def _error_impl(self, text: str, title: str = "MGS Mod Kit — Error",
              details: str | None = None) -> None:
        """Show an error. `details` goes in an expandable pane where supported.

        Keeps the headline readable on an 800p screen instead of dumping hashes
        and recovery paragraphs into one box.
        """
        if self.kind == "tk":
            from tkinter import messagebox
            body = text if not details else f"{text}\n\n{details}"
            messagebox.showerror(title, body, parent=self._tk_root)
        elif self.kind == "kdialog":
            if details:
                self._run(["kdialog", "--title", title, "--detailederror",
                           text, details])
            else:
                self._run(["kdialog", "--title", title, "--error", text])
        elif self.kind == "zenity":
            body = text if not details else f"{text}\n\n{details}"
            self._run(["zenity", "--error", "--title", title,
                       "--no-wrap", "--text", body])
        else:
            print(f"\n!!! {title} !!!\n{text}\n", file=sys.stderr)
            if details:
                print(f"{details}\n", file=sys.stderr)

    def _yesno_impl(self, text: str, title: str = "MGS Mod Kit") -> bool:
        if self.kind == "tk":
            from tkinter import messagebox
            return bool(messagebox.askyesno(title, text, parent=self._tk_root))
        if self.kind == "kdialog":
            return self._run(["kdialog", "--title", title, "--yesno", text])[0] == 0
        if self.kind == "zenity":
            return self._run(["zenity", "--question", "--title", title,
                              "--no-wrap", "--text", text])[0] == 0
        return input(f"{text} [y/N] ").strip().lower().startswith("y")

    def _pick_dir_impl(self, text: str) -> str | None:
        start = str(Path.home())
        if self.kind == "tk":
            from tkinter import filedialog
            out = filedialog.askdirectory(title=text, initialdir=start,
                                          parent=self._tk_root)
            return out or None
        if self.kind == "kdialog":
            rc, out = self._run(["kdialog", "--title", text,
                                 "--getexistingdirectory", start])
            return out or None if rc == 0 else None
        if self.kind == "zenity":
            rc, out = self._run(["zenity", "--file-selection", "--directory",
                                 "--title", text])
            return out or None if rc == 0 else None
        ans = input(f"{text}\nPath: ").strip()
        return ans or None

    def _pick_file_impl(self, text: str, start: Path | None = None) -> str | None:
        start_s = str(start or (Path.home() / "Downloads"))
        if self.kind == "tk":
            from tkinter import filedialog
            out = filedialog.askopenfilename(
                title=text, initialdir=start_s, parent=self._tk_root,
                filetypes=[("Mod archives", "*.zip *.7z *.rar"),
                           ("All files", "*.*")])
            return out or None
        if self.kind == "kdialog":
            # The filter MUST be the described "Name (globs)" form: KF5-era
            # kdialog silently ignored a bare glob and showed every file
            # (KDE bug 467868); the described form works on both generations.
            rc, out = self._run(["kdialog", "--title", text,
                                 "--getopenfilename", start_s,
                                 "Mod archives (*.zip *.7z *.rar)"])
            return out or None if rc == 0 else None
        if self.kind == "zenity":
            rc, out = self._run(["zenity", "--file-selection", "--title", text,
                                 "--filename", start_s + "/",
                                 "--file-filter=Mod archives | *.zip *.7z *.rar",
                                 "--file-filter=All files | *"])
            return out or None if rc == 0 else None
        ans = input(f"{text}\nPath to archive (blank to skip): ").strip()
        return ans or None

    def pick_archive_file(self, text: str) -> str | None:
        """pick_file, but opening in (and remembering) the last-used folder."""
        sel = self.pick_file(text, start=self.last_dir)
        if sel:
            parent = Path(sel).parent
            if parent.is_dir():
                self.last_dir = parent
        return sel

    def _checklist_impl(self, title: str, text: str,
                  items: list[tuple[str, str, bool]]) -> list[str] | None:
        """items: (tag, label, checked).

        Returns the selected tags, or ``None`` if the user CANCELLED the
        dialog. That distinction matters: an empty list means "the user
        deliberately unchecked everything", whereas None means "the user
        backed out" — the caller keeps its defaults instead of silently
        treating a cancel as "turn every option off".
        """
        if self.kind == "tk":
            return self._tk_choices(title, text, items, multi=True)
        if self.kind == "kdialog":
            args = ["kdialog", "--title", title, "--separate-output",
                    "--checklist", text]
            for tag, label, chk in items:
                args += [tag, label, "on" if chk else "off"]
            rc, out = self._run(args)
            return out.splitlines() if rc == 0 else None
        if self.kind == "zenity":
            args = ["zenity", "--list", "--checklist", "--title", title,
                    "--text", text,
                    "--column", "Pick", "--column", "Tag", "--column", "Item",
                    "--hide-column", "2", "--print-column", "2"]
            for tag, label, chk in items:
                args += ["TRUE" if chk else "FALSE", tag, label]
            rc, out = self._run(args)
            if rc != 0:
                return None
            return out.split("|") if out else []
        print(f"\n{title}\n{text}")
        for i, (tag, label, chk) in enumerate(items):
            print(f"  [{i}] {'x' if chk else ' '} {label}")
        raw = input("Enter numbers to toggle (space-separated, "
                    "blank=keep defaults, 'c'=cancel): ")
        if raw.strip().lower() == "c":
            return None
        chosen = {tag for tag, _, chk in items if chk}
        if raw.strip():
            toggles = {int(x) for x in raw.split() if x.isdigit()}
            chosen = set()
            for i, (tag, _, chk) in enumerate(items):
                if chk ^ (i in toggles):
                    chosen.add(tag)
        return list(chosen)

    def _menu_impl(self, title: str, text: str,
             items: list[tuple[str, str]]) -> str | None:
        if self.kind == "tk":
            return self._tk_choices(title, text, items, multi=False)
        if self.kind == "kdialog":
            args = ["kdialog", "--title", title, "--menu", text]
            for tag, label in items:
                args += [tag, label]
            rc, out = self._run(args)
            return out if rc == 0 else None
        if self.kind == "zenity":
            args = ["zenity", "--list", "--title", title, "--text", text,
                    "--column", "Tag", "--column", "Option",
                    "--hide-column", "1", "--print-column", "1"]
            for tag, label in items:
                args += [tag, label]
            rc, out = self._run(args)
            return out if rc == 0 and out else None
        print(f"\n{title}: {text}")
        for tag, label in items:
            print(f"  {tag}) {label}")
        return input("Choice: ").strip() or None

    # -- public API: every dialog retries in the terminal if the tool breaks --
    def info(self, text, title="MGS Mod Kit"):
        return self._retryable(self._info_impl, text, title)

    def error(self, text, title="MGS Mod Kit — Error", details=None):
        return self._retryable(self._error_impl, text, title, details)

    def yesno(self, text, title="MGS Mod Kit"):
        return self._retryable(self._yesno_impl, text, title)

    def pick_dir(self, text):
        return self._retryable(self._pick_dir_impl, text)

    def pick_file(self, text, start=None):
        return self._retryable(self._pick_file_impl, text, start)

    def checklist(self, title, text, items):
        return self._retryable(self._checklist_impl, title, text, items)

    def menu(self, title, text, items):
        return self._retryable(self._menu_impl, title, text, items)

    def progress(self, title: str, log) -> "Progress":
        return Progress(self.kind, title, log, tk_root=self._tk_root)


# ---------------------------------------------------------------------------
# Progress window shown during install/extraction.
#
# Best-effort GUI: a zenity --progress pipe when available (simple, reliable),
# a kdialog --progressbar driven over D-Bus via qdbus when that's present, and
# otherwise plain log lines — which are always emitted too and are visible in
# the Konsole the shortcut opens. Everything is defensive: a progress failure
# can NEVER break or block the install, and close() always tears the dialog
# down (with a kill fallback) so nothing is left hanging.
# ---------------------------------------------------------------------------
class Progress:
    def __init__(self, kind: str, title: str, log, tk_root=None) -> None:
        self.title = title
        self.log = log
        self.cancel_event = threading.Event()
        self._owner_thread = threading.get_ident()
        self._pending = queue.Queue(maxsize=1)
        self._proc = None
        self._backend = "term"
        self._dbus = None           # (service, path) for kdialog
        self._qdbus = None
        self._last_cancel_poll = 0
        self._tk = None             # (window, bar, label) for tkinter
        if kind == "tk" and tk_root is not None:
            try:
                import tkinter as tk
                from tkinter import ttk
                top = tk.Toplevel(tk_root)
                top.title(title)
                top.attributes("-topmost", True)
                top.resizable(False, False)
                top.protocol("WM_DELETE_WINDOW", self.cancel_event.set)
                lbl = tk.Label(top, text="Preparing…", anchor="w",
                               padx=14, pady=8, width=52)
                lbl.pack(fill="x")
                bar = ttk.Progressbar(top, length=420, maximum=100)
                bar.pack(padx=14, pady=(0, 12))
                tk.Button(top, text="Cancel", command=self.cancel_event.set).pack(pady=(0, 12))
                top.update()
                self._tk = (top, bar, lbl)
                self._backend = "tk"
            except Exception:
                self._tk = None
        elif kind == "zenity" and shutil.which("zenity"):
            try:
                self._proc = subprocess.Popen(
                    ["zenity", "--progress", "--title", title, "--width", "460",
                     "--auto-close", "--percentage", "0"],
                    stdin=subprocess.PIPE, text=True)
                self._backend = "zenity"
            except OSError:
                self._proc = None
        elif kind == "kdialog" and shutil.which("kdialog"):
            self._qdbus = find_qdbus()
            if self._qdbus:
                try:
                    r = subprocess.run(
                        ["kdialog", "--title", title, "--progressbar", title,
                         "100"], capture_output=True, text=True, timeout=10)
                    parts = r.stdout.split()
                    if r.returncode == 0 and len(parts) == 2:
                        self._dbus = (parts[0], parts[1])
                        self._backend = "kdialog"
                        self._qdbus_call("showCancelButton", "true")
                except (OSError, subprocess.SubprocessError):
                    self._dbus = None

    def _qdbus_call(self, *args) -> None:
        if not (self._qdbus and self._dbus):
            return
        try:
            subprocess.run([self._qdbus, self._dbus[0], self._dbus[1], *args],
                           capture_output=True, timeout=5)
        except (OSError, subprocess.SubprocessError):
            self._backend = "term"      # stop trying if D-Bus misbehaves

    def pump(self) -> None:
        while True:
            try:
                label, pct = self._pending.get_nowait()
            except queue.Empty:
                break
            self.update(label, pct)
        if self._tk:
            try:
                self._tk[0].update()
            except Exception:
                self.cancel_event.set()
        # Keep polling after a broken pipe: the exit status may arrive later.
        if self._proc and self._proc.poll() is not None:
            if self._proc.returncode == 1:
                self.cancel_event.set()
        if (self._backend == "kdialog" and self._qdbus and self._dbus
                and time.monotonic() - self._last_cancel_poll >= 0.5):
            self._last_cancel_poll = time.monotonic()
            try:
                result = subprocess.run([self._qdbus, *self._dbus, "wasCancelled"],
                                        capture_output=True, text=True, timeout=1)
                if result.returncode == 0 and result.stdout.strip().lower() == "true":
                    self.cancel_event.set()
            except (OSError, subprocess.SubprocessError):
                pass

    def update(self, label: str, pct: float) -> None:
        if threading.get_ident() != self._owner_thread:
            # Coalesce rapid byte/file events so the UI cannot fall behind.
            try:
                self._pending.put_nowait((label, pct))
            except queue.Full:
                try:
                    self._pending.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self._pending.put_nowait((label, pct))
                except queue.Full:
                    pass
            return
        pct = max(0, min(100, int(pct)))
        self.log(f"  … {label}  ({pct}%)")
        if self._backend == "zenity" and self._proc and self._proc.stdin:
            try:
                self._proc.stdin.write(f"{pct}\n# {label}\n")
                self._proc.stdin.flush()
            except (OSError, ValueError):
                self._backend = "term"
                # Retain the process for cancellation polling and close() cleanup.
        elif self._backend == "kdialog":
            self._qdbus_call("org.freedesktop.DBus.Properties.Set",
                             "org.kde.kdialog.ProgressDialog", "value", str(pct))
            self._qdbus_call("setLabelText", label)
        elif self._backend == "tk" and self._tk:
            try:
                top, bar, lbl = self._tk
                bar["value"] = pct
                lbl.config(text=label)
                top.update()             # pump events without a mainloop
            except Exception:
                self._backend = "term"
                self._tk = None

    def close(self) -> None:
        if self._tk:
            try:
                self._tk[0].destroy()
            except Exception:
                pass
            self._tk = None
        if self._backend == "kdialog":
            self._qdbus_call("close")
        if self._proc:
            try:
                if self._proc.stdin:
                    self._proc.stdin.write("100\n")
                    self._proc.stdin.close()
            except (OSError, ValueError):
                pass
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            except OSError:
                pass
        self._proc = None


# ---------------------------------------------------------------------------
# Steam / game discovery
# ---------------------------------------------------------------------------
def _windows_steam_from_registry() -> Path | None:
    """Steam's install path as the registry records it, or None.

    Split out so tests can stub it — exactly like
    _windows_desktop_from_registry. On a real Windows box with Steam installed
    this SUCCEEDS, which would otherwise make the "no Steam anywhere" branch
    untestable there (and CI's Windows runner, which has no Steam, would never
    notice).
    """
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Valve\Steam") as k:
            return Path(winreg.QueryValueEx(k, "SteamPath")[0])
    except (OSError, ImportError):
        return None


def steam_roots() -> list[Path]:
    if IS_WINDOWS:
        candidates = []
        # Steam records its install path in the registry; the defaults below
        # are the fallback for the rare setup where it doesn't.
        reg = _windows_steam_from_registry()
        if reg is not None:
            candidates.append(reg)
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        candidates += [Path(pf86) / "Steam", Path(pf) / "Steam"]
    else:
        candidates = [
            Path.home() / ".local/share/Steam",
            Path.home() / ".steam/steam",
            Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
        ]
    out, seen = [], set()
    for c in candidates:
        if c.is_dir():
            real = c.resolve()
            if real not in seen:
                seen.add(real)
                out.append(c)
    return out


def library_paths(steam_root: Path) -> list[Path]:
    """Parse libraryfolders.vdf for all Steam library roots (incl. microSD)."""
    vdf = steam_root / "steamapps/libraryfolders.vdf"
    paths = [steam_root]
    if vdf.is_file():
        for m in re.finditer(r'"path"\s*"([^"]+)"',
                             vdf.read_text(errors="ignore")):
            paths.append(Path(m.group(1)))
    seen, out = set(), []
    for p in paths:
        # Windows paths are case-insensitive, and the two sources genuinely
        # disagree on case: the registry stores "c:\program files (x86)\steam"
        # while libraryfolders.vdf stores "C:\Program Files (x86)\Steam". A
        # case-sensitive key sees those as two libraries and scans both.
        key = os.path.normcase(str(p))
        if IS_WINDOWS:
            key = key.casefold()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def find_games() -> dict[str, tuple[Path, Path]]:
    """Return {game_key: (game_dir, steam_root)} for whatever is installed."""
    found: dict[str, tuple[Path, Path]] = {}
    for root in steam_roots():
        for lib in library_paths(root):
            for key, g in GAMES.items():
                if key in found:
                    continue
                d = lib / "steamapps/common" / g["dirname"]
                if (d / g["exe"]).is_file():
                    found[key] = (d, root)
    return found


# ---------------------------------------------------------------------------
# Download / extract helpers
# ---------------------------------------------------------------------------
class CancelledInstall(RuntimeError):
    pass


CANCEL_EVENT = None
TRANSFER_PROGRESS = None


def check_cancelled() -> None:
    if CANCEL_EVENT is not None and CANCEL_EVENT.is_set():
        raise CancelledInstall("Installation cancelled. Recovery is finishing before the window closes.")


def download(url: str, dest: Path, log, sha256: str | None = None) -> None:
    """Bounded retries, interruptible chunks, pinned verification before use."""
    name = url.rsplit("/", 1)[-1]
    log(f"  ↓ {name}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        check_cancelled()
        h, count = hashlib.sha256(), 0
        try:
            with urllib.request.urlopen(req, timeout=15) as r, open(dest, "wb") as f:
                headers = getattr(r, "headers", {})
                length = headers.get("Content-Length", "0")
                total = int(length) if str(length).isdigit() else 0
                while True:
                    check_cancelled()
                    chunk = r.read(1024 * 256)
                    if not chunk:
                        break
                    h.update(chunk)
                    f.write(chunk)
                    count += len(chunk)
                    if TRANSFER_PROGRESS:
                        TRANSFER_PROGRESS(name, count, total)
            if not count:
                raise RuntimeError(f"The download of {name} arrived empty. Check your internet connection and run the installer again.")
            if sha256 is not None and h.hexdigest().lower() != sha256.lower():
                log(f"    ✗ {name}: expected {sha256}, got {h.hexdigest()}")
                raise RuntimeError(f"The download of {name} didn't arrive intact, so it was not installed. Please run the installer again.")
            if sha256:
                log("    ✓ download verified")
            return
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            dest.unlink(missing_ok=True)
            retryable = not isinstance(e, urllib.error.HTTPError) or e.code == 429 or e.code >= 500
            if attempt == 2 or not retryable:
                raise
            log(f"    Connection interrupted; retrying ({attempt + 2}/3)…")
            if CANCEL_EVENT is not None:
                CANCEL_EVENT.wait(2 ** attempt)
            else:
                time.sleep(2 ** attempt)
        except BaseException:
            dest.unlink(missing_ok=True)
            raise


def archive_command(args, on_progress=None, total=0, timeout=600):
    """Keep extraction cancellable even during a long, silent file write."""
    check_cancelled()
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    started = time.monotonic()
    reported = 0
    stdout, stderr, failures = [], [], []

    def read_pipe(pipe, output):
        try:
            for line in pipe:
                output.append(line)
        except (OSError, UnicodeError) as e:
            failures.append(e)
        finally:
            pipe.close()

    readers = [threading.Thread(target=read_pipe, args=(pipe, output), daemon=True)
               for pipe, output in ((proc.stdout, stdout), (proc.stderr, stderr))]
    for reader in readers:
        reader.start()
    try:
        # Windows communicate(timeout) does not expose partial output. Read
        # lines continuously on both platforms instead of waiting for EOF.
        while proc.poll() is None:
            check_cancelled()
            if time.monotonic() - started > timeout:
                raise RuntimeError("The archive tool took too long. Check the archive and try again.")
            if on_progress and total and len(stderr) > reported:
                reported = len(stderr)
                on_progress(min(0.99, reported / total))
            try:
                proc.wait(timeout=0.1)
            except subprocess.TimeoutExpired:
                pass
        for reader in readers:
            reader.join(timeout=1)
        if failures or any(reader.is_alive() for reader in readers):
            raise RuntimeError("The archive tool's output could not be read safely.")
        out, err = "".join(stdout), "".join(stderr)
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, args, out, err)
        if on_progress:
            on_progress(1.0)
        return subprocess.CompletedProcess(args, proc.returncode, out, err)
    except BaseException:
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=1)
        raise



def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            check_cancelled()
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path, log, sha256: str | None = None) -> None:
    """Download `url` unless `dest` already holds the pinned bytes.

    Lets main() pre-download every archive a game needs BEFORE any destructive
    extraction, so a network failure strikes before — never after — large stock
    files are overwritten (those over BACKUP_MAX_BYTES can't be rolled back).
    The per-step install functions then reuse the cached, verified file.
    """
    if (dest.is_file() and sha256
            and sha256_file(dest).lower() == sha256.lower()):
        log(f"  ↓ (verified, already downloaded) {url.rsplit('/', 1)[-1]}")
        return
    download(url, dest, log, sha256=sha256)


# ---------------------------------------------------------------------------
# Safe extraction — validate an archive's paths BEFORE trusting its contents.
#
# bsdtar already refuses absolute paths and `..` members, but we don't rely on
# that: we extract to an isolated staging dir, then walk the result and reject
# anything unsafe (symlinks, hardlinks, or paths that escape staging) rather
# than copying a single malicious entry into the live game folder.
# ---------------------------------------------------------------------------
class UnsafeArchiveError(RuntimeError):
    pass


def _rel_is_unsafe(rel: str) -> bool:
    if not isinstance(rel, str) or not rel or rel.startswith("/") or rel.startswith("\\"):
        return True
    # Windows has a second spelling of "absolute": a drive letter, with or
    # without a slash after it ("C:\x", "C:/x", "C:x" — the last is relative to
    # that drive's working directory, not ours). bsdtar strips these itself,
    # but this pre-flight is meant to reject them BEFORE extraction, and only
    # the user-supplied Nexus archives reach it without a pinned SHA-256.
    if re.match(r"^[A-Za-z]:", rel):
        return True
    parts = re.split(r"[\\/]+", rel)
    return any(p in ("..",) or ":" in p or "\x00" in p
               or p.endswith((" ", "."))
               or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p)
               for p in parts)


def _path_is_within(base: Path, candidate: Path) -> bool:
    """Return whether `candidate` resolves inside `base`."""
    try:
        candidate.resolve(strict=False).relative_to(base.resolve(strict=False))
        return True
    except (OSError, ValueError):
        return False


def _safe_game_path(game_dir: Path, rel: str) -> Path:
    """Resolve a relative path without following a link outside the game."""
    if _rel_is_unsafe(rel):
        raise RuntimeError(f"Refusing unsafe relative path {rel!r}")
    dest = game_dir / rel
    if not _path_is_within(game_dir, dest):
        raise RuntimeError(
            f"Refusing path {rel!r}: it would leave the game directory")
    return dest


def staged_files(archive: Path, staging: Path, on_progress=None) -> list[str]:
    """Extract `archive` into `staging` and return the safe relative paths.

    Raises UnsafeArchiveError if the archive lists an absolute/`..` path, or if
    anything extracted is a symlink or otherwise not a plain file/dir. The
    caller moves the returned paths into place; nothing here touches the game.

    If `on_progress` is given it's called with a 0.0–1.0 fraction as entries
    are extracted (genuine per-file progress for multi-GB audio archives).
    """
    # 1. Pre-flight the listing — reject obviously hostile members up front.
    listing = archive_command([tar_cmd(), "-tf", str(archive)], timeout=60)
    total = 0
    for ln in listing.stdout.splitlines():
        name = ln.rstrip("\r")
        if not name:
            continue
        total += 1
        if _rel_is_unsafe(name.rstrip("/")):
            raise UnsafeArchiveError(
                f"Archive '{archive.name}' contains an unsafe path "
                f"({name!r}); refusing to extract it.")

    # 2. Extract into the isolated staging dir.
    staging.mkdir(parents=True, exist_ok=True)
    args = [tar_cmd(), "-xvf" if on_progress else "-xf", str(archive), "-C", str(staging)]
    archive_command(args, on_progress=on_progress, total=total)

    # 3. Walk what landed. Any symlink (dir or file) is a traversal risk once
    #    we copy through it, so reject the archive outright. os.walk does not
    #    follow symlinks, so a symlinked dir is seen here, not descended into.
    root = staging.resolve()
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(staging):
        for d in dirnames:
            if os.path.islink(os.path.join(dirpath, d)):
                raise UnsafeArchiveError(
                    f"Archive '{archive.name}' contains a symlinked directory "
                    f"({d!r}); refusing to install it.")
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if os.path.islink(full):
                raise UnsafeArchiveError(
                    f"Archive '{archive.name}' contains a symlink "
                    f"({fn!r}); refusing to install it.")
            if not os.path.isfile(full) or os.stat(full).st_nlink > 1:
                # sockets, fifos, devices — nothing a mod archive should hold.
                raise UnsafeArchiveError(
                    f"Archive '{archive.name}' contains a non-regular file "
                    f"({fn!r}); refusing to install it.")
            resolved = Path(full).resolve()
            if root not in resolved.parents and resolved != root:
                raise UnsafeArchiveError(
                    f"Archive '{archive.name}' path escapes staging "
                    f"({fn!r}); refusing to install it.")
            # Always forward slashes: manifests stay identical across
            # platforms, and pathlib accepts them on Windows natively.
            files.append(os.path.relpath(full, staging).replace(os.sep, "/"))
    return files


# shutil.disk_usage works on every platform; os.statvfs is Unix-only.
def validate_payload_paths(rels: list[str], game_key: str,
                           component: str | None, log) -> list[str]:
    out, seen = [], set()
    for rel in rels:
        norm = rel.replace("\\", "/").lower()
        parts = norm.split("/")
        if (_rel_is_unsafe(rel) or MODKIT_DIRNAME in parts
                or any(p.endswith("_savedata_win") for p in parts)
                or parts[-1] in {g["exe"].lower() for g in GAMES.values()}):
            raise UnsafeArchiveError(f"Archive cannot write protected destination {rel!r}.")
        if norm in seen:
            raise UnsafeArchiveError(f"Archive has conflicting paths: {rel!r}.")
        seen.add(norm)
        if component == "audio":
            dirs = ("us/demo/", "us/movie/", "us/vox/")
            if game_key == "mgs2":
                dirs += ("us/demo2/", "us/movievr/")
            if not norm.startswith(dirs) or not norm.endswith(AUDIO_EXTS):
                if len(parts) == 1 and norm.endswith((".txt", ".md", ".pdf")):
                    log(f"    Skipped archive documentation: {rel}")
                    continue
                raise UnsafeArchiveError(f"Audio archive contains an unexpected destination: {rel!r}.")
        out.append(rel)
    if not out:
        raise UnsafeArchiveError("Archive contains no supported payload files.")
    return out


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / (1024 ** 3)


def free_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


# Extraction is staged inside the game folder before files are moved into
# place, so peak usage is roughly the payload twice over plus a safety margin.
SPACE_MARGIN_BYTES = 512 * 1024 * 1024


def archive_payload_bytes(archive: Path) -> int:
    """Total uncompressed size of an archive, or 0 if it can't be determined.

    `bsdtar -tvf` prints ls-style rows whose 5th column is the member size.
    Used only for a pre-flight space check, so an unparseable row is skipped
    rather than treated as an error.
    """
    try:
        p = archive_command([tar_cmd(), "-tvf", str(archive)], timeout=60)
    except (OSError, subprocess.SubprocessError):
        return 0
    if p.returncode != 0:
        return 0
    total = 0
    for line in p.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[0][:1] in "-d l":
            try:
                total += int(parts[4])
            except ValueError:
                continue
    return total


def check_space(game_dir: Path, payload_bytes: int,
                margin: int = SPACE_MARGIN_BYTES) -> tuple[bool, str]:
    """(ok, human message) — is there room to stage AND install `payload_bytes`?"""
    try:
        avail = free_bytes(game_dir)
    except OSError:
        return True, ""            # can't tell; don't block the install
    needed = payload_bytes * 2 + margin
    if avail >= needed:
        return True, ""
    gb = 1024 ** 3
    return False, (
        f"Not enough free space on the drive holding {game_dir.name}.\n\n"
        f"Needed: about {needed / gb:.1f} GB    Free: {avail / gb:.1f} GB\n\n"
        "The installer unpacks each mod before putting it in place, so it "
        "briefly needs roughly twice the mod's size. Free up some space (or "
        "move the game to another drive) and run this again.")


def detect_device(env: dict | None = None,
                  dmi_bases: tuple[str, ...] | None = None) -> str:
    """Best-effort hardware profile: 'steam_deck' or 'generic_linux'.

    Only nudges menu defaults and the one genuine Deck-specific rule
    (Konami's high-res texture pack being unusable in-game there) — it can
    never block or change what gets installed. Not every SteamOS device is
    a Deck (Steam Machines, desktop SteamOS), so unknown hardware falls
    back to 'generic_linux'.
    """
    env = os.environ if env is None else env
    if env.get("SteamDeck"):
        return "steam_deck"
    if IS_WINDOWS:
        return "windows"
    for base in dmi_bases or ("/sys/class/dmi/id",
                              "/sys/devices/virtual/dmi/id"):
        try:
            vendor = (Path(base) / "sys_vendor").read_text().strip()
            product = (Path(base) / "product_name").read_text().strip()
        except OSError:
            continue
        # Jupiter = LCD Deck, Galileo = OLED Deck
        if vendor == "Valve" and product in ("Jupiter", "Galileo"):
            return "steam_deck"
    return "generic_linux"


# ---------------------------------------------------------------------------
# Transactional installer.
#
# Every file that lands in the game folder goes through one InstallTxn, which:
#   • stages + path-validates each archive before copying anything in,
#   • backs up any original it overwrites (small files only — see
#     BACKUP_MAX_BYTES),
#   • records every added/overwritten path plus the mod versions in a manifest,
#   • rolls the whole thing back if any step raises, and
#   • is replayed in reverse by uninstall_game().
#
# The manifest and backups live in <game>/mgs-modkit/, so repair and uninstall
# need nothing but the game folder itself.
# ---------------------------------------------------------------------------
class CorruptManifestError(RuntimeError):
    """The mgs-modkit record exists but can't be read — refuse to guess."""


def _sync_dir(path: Path) -> None:
    """Flush directory entries where the platform supports it."""
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def durable_mkdir(path: Path) -> None:
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir(exist_ok=True)
        _sync_dir(directory.parent)


def flush_file(path: Path) -> None:
    # Windows CRT _commit/fsync rejects a read-only descriptor. The files
    # flushed here are staged payloads, snapshots or our own temporary copies.
    with open(path, "r+b" if sys.platform == "win32" else "rb") as stream:
        os.fsync(stream.fileno())


def atomic_bytes(path: Path, data: bytes) -> None:
    durable_mkdir(path.parent)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with open(temp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
        _sync_dir(path.parent)
    finally:
        temp.unlink(missing_ok=True)


def atomic_copy(src: Path, dest: Path) -> None:
    durable_mkdir(dest.parent)
    temp = dest.with_name(dest.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        shutil.copy2(src, temp)
        flush_file(temp)
        os.replace(temp, dest)
        _sync_dir(dest.parent)
    finally:
        temp.unlink(missing_ok=True)


def restore_snapshot(src: Path, dest: Path) -> None:
    durable_mkdir(dest.parent)
    temp = dest.with_name(dest.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        try:
            os.link(src, temp)
        except OSError:
            atomic_copy(src, temp)
        os.replace(temp, dest)
        _sync_dir(dest.parent)
    finally:
        temp.unlink(missing_ok=True)


def app_data_dir() -> Path:
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "MGSModKit"
    return Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "mgs-modkit"


class GameLock:
    """An OS-held lock: automatically released on exit, including crashes."""
    def __init__(self, game_dir: Path):
        key = hashlib.sha256(os.path.normcase(str(game_dir.resolve())).encode()).hexdigest()
        self.path = app_data_dir() / "locks" / (key + ".lock")
        self.file = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.path, "a+b")
        self.file.seek(0, 2)
        if not self.file.tell():
            self.file.write(b"0")
            self.file.flush()
        self.file.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            self.file.close()
            self.file = None
            raise RuntimeError("Another installer is working on this game. Close it and try again.") from e
        return self

    def __exit__(self, *args):
        if self.file is not None:
            if os.name == "nt":
                import msvcrt
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()
            self.file = None


def _read_record(path: Path) -> dict:
    if path.is_symlink():
        raise CorruptManifestError("A recovery record is linked; backups were kept.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("record is not an object")
        return data
    except (ValueError, OSError, UnicodeError) as e:
        raise CorruptManifestError(
            "This game's recovery record is damaged. No further changes were made. "
            "Keep the mgs-modkit folder and its backups; see docs/TROUBLESHOOTING.md.") from e


def recover_interrupted(game_dir: Path, log) -> tuple[list[str], bool]:
    """Restore the pre-run files, never guess that a planned path was added."""
    root = game_dir / MODKIT_DIRNAME
    journal = root / JOURNAL_NAME
    if not journal.exists():
        return [], True
    if root.is_symlink() or journal.is_symlink() or (root / "backups").is_symlink():
        raise CorruptManifestError("Recovery records are linked; backups were kept.")
    data = _read_record(journal)
    if data.get("schema") != 2 or not isinstance(data.get("entries"), list):
        raise CorruptManifestError(
            "An old or damaged interrupted-install record needs manual recovery. "
            "Keep the mgs-modkit folder and backups; see docs/TROUBLESHOOTING.md.")
    run_id = data.get("transaction_id")
    if not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise CorruptManifestError("Invalid recovery transaction ID; backups were kept.")
    rollback_dir = root / "rollback" / run_id
    if not _path_is_within(root, rollback_dir) or rollback_dir.is_symlink():
        raise CorruptManifestError("Unsafe recovery folder; backups were kept.")
    entries = data["entries"]
    try:
        if type(data.get("root_existed")) is not bool:
            raise ValueError("invalid original folder state")
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict) or type(entry.get("existed")) is not bool:
                raise ValueError("invalid recovery entry")
            rel = entry.get("path")
            folded = rel.replace("\\", "/").casefold() if isinstance(rel, str) else None
            if folded in seen:
                raise ValueError("duplicate recovery path")
            seen.add(folded)
            _safe_game_path(game_dir, rel)
            if rel.replace("\\", "/").split("/")[0].casefold() == MODKIT_DIRNAME:
                raise ValueError("recovery points at its own records")
            if entry["existed"]:
                before = rollback_dir / rel
                if not _path_is_within(rollback_dir, before) or before.is_symlink():
                    raise ValueError("unsafe recovery snapshot")
        new_backups = data.get("new_original_backups", [])
        if not isinstance(new_backups, list):
            raise ValueError("invalid backup list")
        for rel in new_backups:
            _safe_game_path(root / "backups", rel)
    except (ValueError, TypeError, RuntimeError, AttributeError) as e:
        raise CorruptManifestError("Unsafe recovery record; files and backups were kept.") from e
    # A durable matching manifest means the transaction committed before the
    # interruption. Cleanup only; reverting here would undo an accepted install.
    manifest = root / MANIFEST_NAME
    committed = False
    if manifest.exists():
        record = _read_record(manifest)
        try:
            _validate_manifest(record, game_dir, root)
        except (ValueError, RuntimeError) as e:
            raise CorruptManifestError("Invalid install record; recovery data was kept.") from e
        committed = record.get("transaction_id") == run_id
    errors = []
    if not committed:
        for entry in reversed(entries):
            rel = entry["path"]
            try:
                dest = _safe_game_path(game_dir, rel)
                if entry["existed"]:
                    before = rollback_dir / rel
                    if not before.is_file():
                        raise OSError("pre-run snapshot is missing")
                    restore_snapshot(before, dest)
                else:
                    dest.unlink(missing_ok=True)
            except (OSError, RuntimeError) as e:
                errors.append(f"Could not restore {rel}: {e}")
    if errors:
        for note in errors:
            log("    ⚠ " + note)
        return errors, False
    # Remove intent first, with its directory entry flushed. If cleanup is
    # interrupted, harmless orphan snapshots remain, never a journal with
    # missing snapshots. Failed restoration never reaches this point.
    journal.unlink()
    _sync_dir(root)
    if not committed:
        for rel in new_backups:
            (root / "backups" / rel).unlink(missing_ok=True)
        _prune_empty_dirs(game_dir, [e["path"] for e in entries if not e["existed"]])
    shutil.rmtree(rollback_dir, ignore_errors=True)
    shutil.rmtree(root / "staging", ignore_errors=True)
    if not committed and not data.get("root_existed", True):
        shutil.rmtree(root, ignore_errors=True)
    log("    ✓ " + ("finished committed-install cleanup" if committed else "restored the interrupted run"))
    return [], True


class InstallTxn:
    def __init__(self, game_dir: Path, game_key: str, log) -> None:
        self.game_dir, self.game_key, self.log = game_dir, game_key, log
        self.root = game_dir / MODKIT_DIRNAME
        if self.root.is_symlink():
            raise CorruptManifestError("The mgs-modkit folder is a symbolic link; nothing was changed.")
        if self.root.exists():
            notes, ok = recover_interrupted(game_dir, log)
            if not ok:
                raise CorruptManifestError("Recovery is incomplete. Backups were kept. " + "; ".join(notes))
        self._root_existed = self.root.exists()
        self.backups = self.root / "backups"
        self.staging = self.root / "staging"
        self.journal = self.root / JOURNAL_NAME
        self.run_id = uuid.uuid4().hex
        self.rollback_dir = self.root / "rollback" / self.run_id
        self.added, self.overwritten = [], []
        self.mods, self.settings = {}, {}
        self._added_set, self._backed_up = set(), set()
        self._prepared = set()
        self._new_added, self._new_backups = [], []
        self._entries = []
        self._expected_files = {}
        self.committed = False
        self._had_prior = False
        self._prior_added = set()
        self._prior_added_list = []
        self._prior_mods = {}
        self._prior_settings = {}
        prev = self.root / MANIFEST_NAME
        if prev.exists():
            data = _read_record(prev)
            try:
                added, overwritten = _validate_manifest(data, game_dir, self.root)
                if data.get("game") != game_key:
                    raise ValueError("record belongs to a different or unknown game")
                if "added" not in data or "overwritten" not in data:
                    raise ValueError("record is missing its file lists")
                if not isinstance(data.get("mods", {}), dict):
                    raise ValueError("invalid mod list")
                self._prior_added_list = list(added)
                self._prior_added = set(added)
                self._prior_mods = dict(data.get("mods", {}))
                self._prior_settings = dict(data.get("settings", {}))
                self.overwritten = list(overwritten)
                self._backed_up = {o["path"] for o in overwritten}
                self._had_prior = True
            except (ValueError, TypeError, RuntimeError) as e:
                raise CorruptManifestError("Invalid install record; backups were kept.") from e
        for directory in (self.staging, self.root / "rollback"):
            if directory.is_symlink():
                raise CorruptManifestError("A transaction folder is linked; nothing was changed.")
        self._adopt_orphan_backups()

    def _adopt_orphan_backups(self) -> None:
        if not self.backups.exists():
            return
        if self.backups.is_symlink():
            raise CorruptManifestError("The backups folder is a link; nothing was changed.")
        for dirpath, dirs, names in os.walk(self.backups):
            if any((Path(dirpath) / n).is_symlink() for n in dirs + names):
                raise CorruptManifestError("A backup is a link; nothing was changed.")
            for name in names:
                rel = (Path(dirpath) / name).relative_to(self.backups).as_posix()
                if rel not in self._backed_up:
                    self.overwritten.append({"path": rel, "backup": "backups/" + rel})
                    self._backed_up.add(rel)

    def note_mod(self, name: str, version: str) -> None:
        self.mods[name] = version

    def _prepare_dest(self, rel: str) -> None:
        if rel in self._prepared:
            return
        dest = _safe_game_path(self.game_dir, rel)
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            raise RuntimeError(f"Cannot replace {rel}: it is not a regular file.")
        existed = dest.exists()
        if existed:
            snapshot = self.rollback_dir / rel
            durable_mkdir(snapshot.parent)
            # Hardlink snapshots do not duplicate multi-GB audio. All live writes
            # below use atomic replacement, so the snapshot stays unchanged.
            try:
                os.link(dest, snapshot)
                flush_file(snapshot)
                _sync_dir(snapshot.parent)
            except OSError:
                snapshot.unlink(missing_ok=True)
                if free_bytes(self.game_dir) < dest.stat().st_size + SPACE_MARGIN_BYTES:
                    raise RuntimeError("Not enough space to safely preserve the current files for rollback.")
                atomic_copy(dest, snapshot)
            if rel not in self._prior_added and rel not in self._backed_up:
                self._backed_up.add(rel)
                bpath = self.backups / rel
                if dest.stat().st_size <= BACKUP_MAX_BYTES:
                    if not bpath.exists():
                        atomic_copy(dest, bpath)
                        self._new_backups.append(rel)
                    self.overwritten.append({"path": rel, "backup": "backups/" + rel})
                else:
                    self.overwritten.append({"path": rel, "backup": None, "original_sha256": sha256_file(dest)})
        if not existed or rel in self._prior_added:
            self.added.append(rel)
            self._added_set.add(rel)
            if not existed:
                self._new_added.append(rel)
        self._entries.append({"path": rel, "existed": existed})
        self._prepared.add(rel)

    def _journal_planned(self, rels: list[str]) -> None:
        for rel in rels:
            self._prepare_dest(rel)
        data = {"schema": 2, "transaction_id": self.run_id,
                "root_existed": self._root_existed, "entries": self._entries,
                "new_original_backups": self._new_backups}
        atomic_bytes(self.journal, json.dumps(data).encode("utf-8"))

    def install_archive(self, archive: Path, on_progress=None,
                        component: str | None = None) -> list[str]:
        ok, msg = check_space(self.game_dir, archive_payload_bytes(archive))
        if not ok:
            raise RuntimeError(msg)
        durable_mkdir(self.staging)
        stage = Path(tempfile.mkdtemp(prefix="stage_", dir=self.staging))
        try:
            rels = staged_files(archive, stage, on_progress=on_progress)
            rels = validate_payload_paths(rels, self.game_key, component, self.log)
            self._journal_planned(rels)
            for rel in rels:
                check_cancelled()
                dest = _safe_game_path(self.game_dir, rel)
                durable_mkdir(dest.parent)
                src = stage / rel
                flush_file(src)
                size = src.stat().st_size
                digest = sha256_file(src) if size <= BACKUP_MAX_BYTES else None
                os.replace(src, dest)
                self._expected_files[rel] = {"size": size, "sha256": digest}
                _sync_dir(dest.parent)
            return rels
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    def write_bytes(self, rel: str, data: bytes) -> None:
        self._journal_planned([rel])
        atomic_bytes(_safe_game_path(self.game_dir, rel), data)
        self._expected_files[rel] = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    def read_text_ours(self, rel: str, encoding: str = "utf-8") -> str:
        return _safe_game_path(self.game_dir, rel).read_text(encoding=encoding)

    def verify(self) -> None:
        for rel, expected in self._expected_files.items():
            check_cancelled()
            dest = _safe_game_path(self.game_dir, rel)
            if not dest.is_file() or dest.stat().st_size != expected["size"]:
                raise RuntimeError(f"Verification failed: {rel} has changed or is missing.")
            if expected["sha256"] and sha256_file(dest) != expected["sha256"]:
                raise RuntimeError(f"Verification failed: {rel} does not match the installed payload.")

    def commit(self) -> None:
        self.verify()
        added = list(dict.fromkeys(self._prior_added_list + self.added))
        manifest = {"schema": 2, "transaction_id": self.run_id,
                    "modkit_version": MODKIT_VERSION, "game": self.game_key,
                    "installed_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "mods": {**self._prior_mods, **self.mods}, "added": added,
                    "overwritten": self.overwritten,
                    "settings": self.settings or self._prior_settings,
                    "files": self._expected_files}
        try:
            atomic_bytes(self.root / MANIFEST_NAME, json.dumps(manifest, indent=2).encode("utf-8") + b"\n")
        except OSError:
            # Replacement may have completed before a directory flush failed.
            record = self.root / MANIFEST_NAME
            if record.exists() and _read_record(record).get("transaction_id") == self.run_id:
                self.committed = True
            raise
        self.committed = True
        # A failure here leaves a committed marker + journal: next run cleans
        # up rather than falsely undoing the successfully committed install.
        try:
            if self.journal.exists():
                self.journal.unlink()
                _sync_dir(self.root)
        except OSError as e:
            self.log(f"    ⚠ Installed successfully; recovery cleanup will be retried next run: {e}")
            return
        shutil.rmtree(self.rollback_dir, ignore_errors=True)
        shutil.rmtree(self.staging, ignore_errors=True)

    def rollback(self) -> bool:
        if self.journal.exists():
            try:
                _, ok = recover_interrupted(self.game_dir, self.log)
                return ok
            except (OSError, RuntimeError) as e:
                self.log(f"    ⚠ Recovery incomplete: {e}. Backups were kept.")
                return False
        # No durable intent means no live mutation was permitted. Only this
        # run's preparation data may be discarded.
        shutil.rmtree(self.rollback_dir, ignore_errors=True)
        for rel in self._new_backups:
            (self.backups / rel).unlink(missing_ok=True)
        if not self._root_existed:
            shutil.rmtree(self.root, ignore_errors=True)
        return True


def _prune_empty_dirs(base: Path, rels: list[str]) -> None:
    """Remove now-empty directories left behind after files were removed."""
    seen: set[Path] = set()
    for rel in rels:
        d = (base / rel).parent
        while d != base and base in d.parents:
            seen.add(d)
            d = d.parent
    for d in sorted(seen, key=lambda p: len(str(p)), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass  # not empty (other files live here) — leave it


# ---------------------------------------------------------------------------
# Install steps  (ORDER MATTERS — see the mods' own README:
#   1. MGSHDFix  →  2. Better Audio  →  3. Bugfix Compilation Base)
# ---------------------------------------------------------------------------
def install_hdfix(tx: InstallTxn, tmp: Path, log) -> None:
    log(f"  Installing MGSHDFix {HDFIX_VERSION} …")
    zp = tmp / f"MGSHDFix_{HDFIX_VERSION}.zip"
    fetch(HDFIX_URL, zp, log, sha256=HDFIX_SHA256)
    tx.install_archive(zp)
    tx.note_mod("MGSHDFix", HDFIX_VERSION)
    missing = [n for n in ("winhttp.dll", "wininet.dll")
               if not (tx.game_dir / n).is_file()]
    if missing or not (tx.game_dir / "plugins" / "MGSHDFix.asi").is_file():
        raise RuntimeError(
            "MGSHDFix extraction failed (missing: "
            f"{', '.join(missing) or 'plugins/MGSHDFix.asi'})")
    log("    ✓ winhttp.dll + wininet.dll + plugins/MGSHDFix.asi")


def install_better_audio(tx: InstallTxn, components: list[dict], log,
                         report=None) -> None:
    """Install ordered Better Audio components, each logged + recorded by name.

    `components` is the ordered output of order_audio_components(): base first,
    optional HQ Ending next, then the Update last. If `report` is given it's
    called as report(status_label, fraction 0..1) with genuine per-file
    extraction progress across all components.
    """
    n = len(components)
    for j, comp in enumerate(components):
        archive = Path(comp["path"])
        gb = archive.stat().st_size / 1024 ** 3
        log(f"  Installing {comp['log']} from {archive.name} "
            f"({gb:.2f} GB) …")

        op = None
        if report is not None:
            def op(frac, status=comp["status"], j=j):
                report(status, (j + frac) / n)     # this component's slice
        # install_archive stage-validates paths (no traversal/symlinks) and
        # moves every file into place, tracking it for rollback/uninstall.
        rels = tx.install_archive(archive, on_progress=op, component="audio")
        # Verify the payload actually landed — every file entry must exist.
        missing = [e for e in rels if not (tx.game_dir / e).is_file()]
        if missing:
            raise RuntimeError(
                f"{comp['log']} ('{archive.name}'): {len(missing)} file(s) "
                f"missing after extraction (e.g. {missing[0]}). The archive "
                "may be corrupt — re-download it and re-run this kit.")
        log(f"    ✓ {comp['log']}: all {len(rels)} files verified on disk")
        # Record each component separately in the manifest. The status name
        # already names the game, so it needs no prefix.
        tx.note_mod(comp["status"], comp["filename"])


def install_m2fix(tx: InstallTxn, tmp: Path, opts: dict, log) -> None:
    log(f"  Installing MGSM2Fix {M2FIX_VERSION} …")
    zp = tmp / f"MGSM2Fix_{M2FIX_VERSION}.zip"
    fetch(M2FIX_URL, zp, log, sha256=M2FIX_SHA256)
    tx.install_archive(zp)
    tx.note_mod("MGSM2Fix", M2FIX_VERSION)
    missing = [n for n in ("d3d11.dll", "dinput8.dll", "MGSM2Fix64.asi",
                           "MGSM2Fix.ini") if not (tx.game_dir / n).is_file()]
    if missing:
        raise RuntimeError(f"MGSM2Fix extraction failed (missing: "
                           f"{', '.join(missing)})")
    parser = parse_ini(tx.read_text_ours("MGSM2Fix.ini"))
    existing = opts.get("_existing_m2fix")
    if existing and not opts.get("_reset"):
        old = parse_ini(existing)
        for section in old.sections():
            if section not in parser:
                raise RuntimeError(f"Unsupported MGSM2Fix section: {section}")
            for key, value in old[section].items():
                if key not in parser[section]:
                    raise RuntimeError(f"Unsupported MGSM2Fix setting: {key}")
                parser[section][key] = value
    seen = set()
    for section in parser.sections():
        for key in parser[section]:
            if key in ("CheckForUpdates", "StartGame"):
                value = parser[section][key].casefold()
                if value not in ("true", "false"):
                    raise RuntimeError(f"MGSM2Fix {key} must be true or false")
                seen.add(key)
                if key == "CheckForUpdates":
                    parser[section][key] = "false"
                elif not existing or opts.get("_reset") or "skip_launcher" in opts.get("_changed", set()):
                    parser[section][key] = str(opts.get("skip_launcher", True)).lower()
    if seen != {"CheckForUpdates", "StartGame"}:
        raise RuntimeError("MGSM2Fix configuration is missing required options")
    tx.write_bytes("MGSM2Fix.ini", render_ini(parser, spaced=True).encode("utf-8"))
    log("    ✓ d3d11.dll + dinput8.dll + MGSM2Fix (vanilla-faithful "
        "shipped defaults; auto-boots your last-picked version)")


def install_bugfix(tx: InstallTxn, g: dict, tmp: Path, log) -> None:
    log(f"  Installing {g['short']} Community Bugfix Compilation "
        f"{g['bugfix_version']} (Base) …")
    zp = tmp / f"{g['short']}_bugfix_base.zip"
    fetch(g["bugfix_url"], zp, log, sha256=g.get("bugfix_sha256"))
    tx.install_archive(zp)
    tx.note_mod(f"{g['short']} Community Bugfix Compilation",
                g["bugfix_version"])
    if not (tx.game_dir / "plugins" / g["bugfix_asi"]).is_file():
        raise RuntimeError(f"Bugfix Compilation failed (plugins/"
                           f"{g['bugfix_asi']} missing)")
    log(f"    ✓ plugins/{g['bugfix_asi']}")


def parse_ini(body: str) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None, delimiters=("=",),
                                       strict=True, empty_lines_in_values=False)
    parser.optionxform = str
    parser.read_string(body.lstrip("\ufeff"))
    if parser.defaults():
        raise ValueError("DEFAULT sections are not supported")
    return parser


def validate_settings(body: str) -> configparser.ConfigParser:
    """Exact upstream key names and value types; ':' is part of some keys."""
    try:
        parser = parse_ini(body)
        if set(parser.sections()) != set(SETTINGS_SCHEMA):
            raise ValueError("section names do not match the pinned Config Tool")
        for section, fields in SETTINGS_SCHEMA.items():
            if set(parser[section]) != set(fields):
                raise ValueError(f"keys in [{section}] do not match the pinned Config Tool")
            for key, kind in fields.items():
                value = parser[section][key]
                if kind == "Bool" and value not in ("0", "1"):
                    raise ValueError(f"[{section}] {key} must be 0 or 1")
                if kind == "Int":
                    int(value)
                if kind == "Float" and not math.isfinite(float(value)):
                    raise ValueError(f"[{section}] {key} must be finite")
                if kind in ("Choice", "Hotkey", "Str") and not (
                        value.startswith('"') and value.endswith('"') and len(value) >= 2):
                    raise ValueError(f"[{section}] {key} must be quoted")
        for section, fields in SETTINGS_CONSTRAINTS.items():
            for key, constraint in fields.items():
                value = parser[section][key]
                if "choices" in constraint and value.strip('"') not in constraint["choices"]:
                    raise ValueError(f"Unsupported [{section}] {key}")
                if "range" in constraint:
                    low, high = constraint["range"]
                    if not low <= int(value) <= high:
                        raise ValueError(f"[{section}] {key} must be between {low} and {high}")
        if parser["Controller Settings"]["Button Icons"].strip('"') not in SAVED_BUTTON_ICONS:
            raise ValueError("Unsupported button icons")
        return parser
    except (configparser.Error, ValueError) as e:
        raise RuntimeError(f"Settings validation failed: {e}") from e


def render_ini(parser: configparser.ConfigParser, spaced=False) -> str:
    stream = io.StringIO()
    parser.write(stream, space_around_delimiters=spaced)
    return stream.getvalue()


# Only the complete historical kit schema may be migrated. Partial omissions
# remain errors. Defaults come from pinned 4.1.0 tab_data.cpp (150, 158, 226).
SETTINGS_MIGRATION_DEFAULTS = {
    "Enhancements and Tweaks": {"Correct Aspect Ratio to 4:3": "1", "Crop Overscan Area": "1"},
    "Launcher and Splashscreens": {"MSX Skip Launcher Game": '"Metal Gear (MSX)"'},
}


def migrate_settings(body: str) -> str:
    """Validate the old complete shape before adding only known missing fields."""
    body = body.replace('Show Pressure Level Overlay="Disabled"', 'Show Pressure Level Overlay=0')
    try:
        parser = parse_ini(body)
        legacy = {section: set(keys) - set(SETTINGS_MIGRATION_DEFAULTS.get(section, {}))
                  for section, keys in SETTINGS_SCHEMA.items()}
        if ({section: set(parser[section]) for section in parser.sections()} == legacy):
            for section, keys in SETTINGS_MIGRATION_DEFAULTS.items():
                for key, value in keys.items():
                    parser[section][key] = value
            body = render_ini(parser)
        validate_settings(body)
        return body
    except (configparser.Error, ValueError) as error:
        raise RuntimeError(f"Settings validation failed: {error}") from error


def write_settings(tx: InstallTxn, g: dict, opts: dict, log) -> None:
    body = SETTINGS_TEMPLATE
    for ph, val in (
        ("@BUTTON_ICONS@", opts["button_icons"]), ("@REGION@", g["region"]),
        ("@SKIP_LAUNCHER@", "1" if opts["skip_launcher"] else "0"),
        ("@SKIP_SPLASH@", "1" if opts["skip_splash"] else "0"),
        ("@AUDIO_MODE@", opts["audio_mode"]), ("@UPDATE_CHECK@", "0"),
    ):
        body = body.replace(ph, val)
    parser = validate_settings(body)
    existing = opts.get("_existing_settings")
    if existing and not opts.get("_reset"):
        # Refuse unsupported edits instead of silently discarding custom settings.
        old = validate_settings(migrate_settings(existing))
        for section in old.sections():
            for key, value in old[section].items():
                parser[section][key] = value
        changed = opts.get("_changed", set())
        for option, section, key, value in (
            ("button_icons", "Controller Settings", "Button Icons", '"' + opts["button_icons"] + '"'),
            ("audio_mode", "System Specific Fixes", "Audio Output Mode", '"' + opts["audio_mode"] + '"'),
            ("skip_launcher", "Launcher and Splashscreens", "Skip Launcher", str(int(opts["skip_launcher"]))),
            ("skip_splash", "Launcher and Splashscreens", "Skip In-Game Splashscreens", str(int(opts["skip_splash"]))),
            ("skip_splash", "Launcher and Splashscreens", "Skip Launcher Splashscreens", str(int(opts["skip_splash"]))),
        ):
            if option in changed:
                parser[section][key] = value
    # The kit controls version updates even when preserving manual edits.
    parser["Update Notifications"]["Check For MGSHDFix Updates"] = "0"
    body = render_ini(parser)
    validate_settings(body)
    tx.write_bytes("plugins/MGSHDFix.settings", body.replace("\n", "\r\n").encode("utf-8"))
    log("    ✓ plugins/MGSHDFix.settings (exact pinned schema validated)")


def steamid64s(steam_root: Path) -> list[int]:
    """Every Steam account on this machine, as steamid64."""
    out = []
    ud = steam_root / "userdata"
    if ud.is_dir():
        for d in ud.iterdir():
            if d.is_dir() and d.name.isdigit():
                out.append(int(d.name) + STEAMID64_BASE)
    return out


def _read_launcher_sv(path: Path) -> dict[str, str]:
    """Parse the launcher's save. Raises ValueError on anything unexpected.

    A hand-edited or corrupt save could hold non-lists or non-strings; a raw
    TypeError from zip() would escape the caller's handler and surface as a
    traceback, so shape problems are normalised to ValueError here.
    """
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("launcher save is not a JSON object")
    keys, vals = data.get("keyList"), data.get("valueList")
    if not isinstance(keys, list) or not isinstance(vals, list):
        raise ValueError("launcher save is missing its key/value lists")
    if len(keys) != len(vals):
        raise ValueError("launcher save has mismatched key/value lists")
    if not all(isinstance(k, str) for k in keys):
        raise ValueError("launcher save has non-text keys")
    # Values are written back as JSON strings; coerce simple scalars so a save
    # holding 1 instead of "1" doesn't abort the whole step.
    out: dict[str, str] = {}
    for k, v in zip(keys, vals):
        if isinstance(v, bool) or v is None:
            raise ValueError(f"launcher save has an unusable value for {k!r}")
        if isinstance(v, (int, float)):
            v = str(v)
        if not isinstance(v, str):
            raise ValueError(f"launcher save has an unusable value for {k!r}")
        out[k] = v
    return out


def _launcher_sv_bytes(keys: list[str], vals: list[str]) -> bytes:
    body = json.dumps({"keyList": keys, "valueList": vals},
                      separators=(",", ":"), ensure_ascii=False)
    # UTF-8 BOM + trailing CRLF, byte-for-byte as the launcher writes it.
    return b"\xef\xbb\xbf" + body.encode("utf-8") + b"\r\n"


def set_launcher_options(tx: InstallTxn, g: dict, steam_root: Path,
                          opts: dict, log) -> bool:
    """Apply the launcher's own options so the launcher can be skipped.

    Writes go through the transaction, so an existing launcher_sv is backed
    up before we patch it (uninstall restores it) and a freshly synthesised
    one is tracked for removal.
    """
    game_dir = tx.game_dir
    wanted = {
        "HiresoMovie": "1" if opts["hq_movies"] else "0",
        # MGSHDFix owns resolution/upscaling; the launcher must stay at
        # Default/Original or the two fight each other.
        "HiresoRender": "0",
        "HiresoUpScale": "0",
    }
    if g["key"] == "mgs3" and opts.get("device", "steam_deck") == "steam_deck":
        # Deck only: Konami's official high-res texture pack installs on the
        # Steam Deck but cannot be used in-game there, so the flag is forced
        # off to keep the launcher from dead-ending. On other hardware an
        # existing HiresoTexture choice (e.g. the DLC genuinely in use on a
        # desktop) is preserved; fresh installs still default to 0 via the
        # template below.
        wanted["HiresoTexture"] = "0"

    save_root = game_dir / f"{g['dirname'].lower()}_savedata_win"
    existing = sorted(save_root.glob("*/launcher/launcher_sv"))

    if existing:
        failures = 0
        for sv in existing:
            try:
                cur = _read_launcher_sv(sv)
            except (ValueError, KeyError, OSError) as e:
                log(f"    ⚠ couldn't parse {sv.name} ({e}); leaving it alone")
                failures += 1
                continue
            cur.update(wanted)
            tx.write_bytes(sv.relative_to(game_dir).as_posix(),
                           _launcher_sv_bytes(list(cur.keys()),
                                              list(cur.values())))
            log(f"    ✓ launcher options patched ({sv.parent.parent.name})")
        if failures:
            log(f"    ⚠ {failures} launcher save(s) were left unchanged")
        return failures == 0

    # Fresh install — the launcher has never run, so synthesise its save.
    keys, vals = LAUNCHER_TEMPLATES[g["key"]]
    keys, vals = list(keys), list(vals)
    for k, v in wanted.items():
        if k in keys:
            vals[keys.index(k)] = v
        else:
            keys.append(k)
            vals.append(v)
    ids = steamid64s(steam_root)
    if not ids:
        log("    ⚠ no Steam account found; skipping launcher options "
            "(set them in the launcher on first run)")
        return True
    for sid in ids:
        rel = f"{save_root.name}/{sid}/launcher/launcher_sv"
        tx.write_bytes(rel, _launcher_sv_bytes(keys, vals))
        log(f"    ✓ launcher options created ({sid})")
    return True


def verify_install(g: dict, game_dir: Path) -> list[str]:
    """Return a list of human-readable problems (empty == all good)."""
    if g.get("kind", "hdfix") == "m2fix":
        return [f"missing {rel}" for rel in
                ("d3d11.dll", "dinput8.dll", "MGSM2Fix64.asi", "MGSM2Fix.ini")
                if not (game_dir / rel).is_file()]
    problems = []
    for rel in ("winhttp.dll", "wininet.dll",
                "plugins/MGSHDFix.asi", "plugins/MGSHDFix.settings"):
        if not (game_dir / rel).is_file():
            problems.append(f"missing {rel}")
    if not (game_dir / "plugins" / g["bugfix_asi"]).is_file():
        problems.append(f"missing plugins/{g['bugfix_asi']}")
    return problems


def _validate_manifest(data: object, game_dir: Path, root: Path
                       ) -> tuple[list[str], list[dict]]:
    """Validate manifest paths before uninstall can touch the game folder."""
    if not isinstance(data, dict):
        raise ValueError("manifest is not a JSON object")
    if "added" not in data or "overwritten" not in data:
        raise ValueError("manifest is missing its file lists")
    added = data.get("added", [])
    overwritten = data.get("overwritten", [])
    if not isinstance(added, list) or not all(
            isinstance(rel, str) for rel in added):
        raise ValueError("manifest has an invalid added-file list")
    if not isinstance(overwritten, list):
        raise ValueError("manifest has an invalid overwritten-file list")

    for rel in added:
        _safe_game_path(game_dir, rel)
        if rel.replace("\\", "/").split("/")[0].casefold() == MODKIT_DIRNAME:
            raise ValueError("manifest points at its own records")

    for entry in overwritten:
        if not isinstance(entry, dict):
            raise ValueError("manifest has an invalid overwritten-file entry")
        rel = entry.get("path")
        _safe_game_path(game_dir, rel)
        if rel.replace("\\", "/").split("/")[0].casefold() == MODKIT_DIRNAME:
            raise ValueError("manifest points at its own records")
        backup = entry.get("backup")
        if backup is None:
            continue
        if not isinstance(backup, str):
            raise ValueError("manifest has an invalid backup path")
        backup = backup.replace("\\", "/")
        if (not backup.startswith("backups/")
                or _rel_is_unsafe(backup)
                or not _path_is_within(root / "backups", root / backup)
                or not _path_is_within(root, root / backup)):
            raise ValueError("manifest has an unsafe backup path")
    return added, overwritten


# ---------------------------------------------------------------------------
# Uninstall — reverse a previous install using its manifest.
#
# Removes every file the kit added (newest-first so directories empty out),
# restores any original it backed up, and clears the obsolete legacy
# MGSM2Fix.asi that upstream warns can clash with the unified 3.x release.
# Multi-GB assets the Better Audio Mod overwrote were recorded but not backed
# up (see BACKUP_MAX_BYTES); Steam's "Verify integrity of game files" restores
# those, and we say so.
# ---------------------------------------------------------------------------
LEGACY_M2FIX_FILES = ("MGSM2Fix.asi",)


def uninstall_game(game_dir: Path, log) -> tuple[list[str], bool]:
    try:
        with GameLock(game_dir):
            if (game_dir / MODKIT_DIRNAME).is_symlink():
                return ["The mgs-modkit folder is a symbolic link; left untouched."], False
            notes, ok = recover_interrupted(game_dir, log)
            if not ok:
                return notes, False
            return _uninstall_game(game_dir, log)
    except (OSError, RuntimeError) as e:
        return [str(e)], False


def _uninstall_game(game_dir: Path, log) -> tuple[list[str], bool]:
    """Reverse a kit install in `game_dir`.

    Returns (notes, ok). If any file couldn't be removed or restored, ok is
    False AND the manifest + backups are LEFT IN PLACE — never delete the
    recovery data while a restore is still outstanding, and never report
    success when files are still in a half-reverted state. Re-running can then
    retry, or the user can restore by hand.
    """
    notes: list[str] = []
    errors = False
    root = game_dir / MODKIT_DIRNAME
    manifest = root / MANIFEST_NAME

    if root.is_symlink():
        notes.append("the mgs-modkit folder is a symbolic link; left it "
                     "untouched for safety")
        return notes, False
    if (root / "backups").is_symlink():
        return ["The backups folder is linked; files were left in place."], False

    # Always clear the obsolete legacy unified .asi, manifest or not.
    for name in LEGACY_M2FIX_FILES:
        legacy = game_dir / name
        if legacy.is_file():
            try:
                legacy.unlink()
                notes.append(f"removed legacy {name}")
            except OSError as e:
                notes.append(f"couldn't remove legacy {name} ({e})")
                errors = True

    if not manifest.is_file():
        # No record — but backups may still be sitting there from a run whose
        # manifest was lost or damaged. Those are the user's original files, so
        # put them back rather than abandoning them.
        restored = 0
        backups_dir = root / "backups"
        if backups_dir.is_dir():
            for dirpath, _dn, filenames in os.walk(backups_dir):
                for fn in filenames:
                    src = Path(dirpath) / fn
                    rel = os.path.relpath(src, backups_dir).replace(os.sep, "/")
                    try:
                        if src.is_symlink():
                            raise RuntimeError(
                                f"backup source {rel} is a symbolic link")
                        dst = _safe_game_path(game_dir, rel)
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        atomic_copy(src, dst)
                        restored += 1
                    except (OSError, RuntimeError) as e:
                        notes.append(f"couldn't restore {rel} ({e})")
                        errors = True
        if restored:
            notes.append(f"no install record was found, but {restored} "
                         "backed-up original file(s) were put back")
            notes.append("Untracked mod files may remain. Inspect docs/TROUBLESHOOTING.md before removing them.")
        else:
            notes.append("no record of an install by this kit was found, so "
                         "there was nothing tracked to remove. Steam's Verify "
                         "integrity restores original files but does NOT "
                         "delete mod files — remove any left over by hand "
                         "(see the README's uninstall list)")
        unknown = has_untracked_mods(game_dir)
        return notes, not errors and not restored and not unknown and not root.exists()

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        added, overwritten = _validate_manifest(data, game_dir, root)
    except (ValueError, OSError, RuntimeError) as e:
        notes.append(f"couldn't read manifest ({e}); left files in place")
        return notes, False

    # Restore originals FIRST (before removing added files), so a file that is
    # both added-by-us and has a stock backup ends up as the stock original.
    restored, verify_hint = 0, False
    for o in overwritten:
        rel, backup = o.get("path"), o.get("backup")
        if backup:
            src = root / backup
            if src.is_file():
                try:
                    if src.is_symlink():
                        raise RuntimeError(
                            f"backup source {backup} is a symbolic link")
                    dst = _safe_game_path(game_dir, rel)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    atomic_copy(src, dst)
                    restored += 1
                except (OSError, RuntimeError) as e:
                    notes.append(f"couldn't restore {rel} ({e})")
                    errors = True
            else:
                notes.append(f"backup for {rel} is missing; can't restore it")
                errors = True
        else:
            dest = _safe_game_path(game_dir, rel)
            original_sha = o.get("original_sha256")
            if not original_sha or not dest.is_file() or sha256_file(dest) != original_sha:
                verify_hint = True

    removed = 0
    restored_paths = {o.get("path") for o in overwritten if o.get("backup")}
    for rel in reversed(added):
        if rel in restored_paths:
            continue  # a stock original was just put back here — keep it
        try:
            _safe_game_path(game_dir, rel).unlink(missing_ok=True)
            removed += 1
        except (OSError, RuntimeError) as e:
            notes.append(f"couldn't remove {rel} ({e})")
            errors = True
    if removed:
        notes.append(f"removed {removed} installed file(s)")
    if restored:
        notes.append(f"restored {restored} original file(s) from backup")
    if verify_hint:
        notes.append("some large originals (e.g. Better Audio assets) were "
                     "not backed up — run Steam → Verify integrity of game "
                     "files to restore them")

    _prune_empty_dirs(game_dir, added)
    if errors or verify_hint:
        notes.append("left the mgs-modkit backup/manifest folder in place so "
                     "you can retry — some files could not be reverted. Steam verification is required for any unbacked originals.")
        return notes, False

    try:
        shutil.rmtree(root)
    except OSError as e:
        notes.append(f"Originals were restored, but the recovery folder could not be removed: {e}")
        return notes, False
    notes.append("removed the mgs-modkit backup/manifest folder")
    return notes, True


# ---------------------------------------------------------------------------
# Better Audio Mod — independent component model.
#
# Every audio component is its own checklist item and is installed independently
# (real Steam Deck use showed Update 2.0 shouldn't be forced — you might already
# have the base from an earlier run and just want the patch). Nothing blocks on
# another component being present.
#
# When several MGS3 components ARE chosen, install order is fixed:
#     base  →  HQ Ending  →  Update 2.0 (last)
# defined by AUDIO_SPECS[game]["order"].
#
# The archives live on NexusMods (login-gated, no mirroring), so they can't be
# inspected here to hard-code exact per-file signatures. Role identification
# (classify_mgs3_role) therefore uses structural evidence — archive file count,
# size, and the version/mod-id parsed from the Nexus filename — and only claims
# a confident match when signals agree; otherwise the user confirms explicitly.
# ---------------------------------------------------------------------------
AUDIO_MODID = {"mgs2": 3, "mgs3": 4}

HQ_ENDING_DISCLAIMER = (
    "Higher-quality audio for the final two cutscenes. These scenes may pause "
    "at the end and require a button press to continue.")

UPDATE_NOTE = "Recommended patch for MGS3 Better Audio, but optional here."

# kdialog/zenity checklist rows do not wrap. Anything longer than this is
# ellipsized or widens the dialog past the Deck's 1280px screen, so notes go
# in the dialog's header text instead of the row label.
CHECKLIST_LABEL_MAX = 60

AUDIO_CHECKLIST_TEXT = (
    "Restores the PS3-quality audio this port compressed (and fixes an MGS2 "
    "cutscene crash).\n"
    "The files come from NexusMods — tick what you want, then pick each file.\n"
    "Each part installs on its own, so you can add the rest later.\n\n"
    "MGS2 offers a complete Full Version or a smaller Lite Version; either is "
    "accepted.\n"
    "HQ Ending Cutscenes: higher-quality audio for the final two cutscenes.\n"
    "Those scenes may pause at the end and need a button press to continue.")

AUDIO_SPECS = {
    "mgs2": {
        "order": ["base"],
        "roles": {
            "base": {
                "status": "MGS2 Better Audio",
                "short": "Better Audio",
                "checklist": "MGS2 — Better Audio",
                "nexus": ('the 2.0 "Full Version" (or the smaller 2.0 '
                          '"Lite Version")'),
                "log": "MGS2 Better Audio",
                "default": True,
            },
        },
    },
    "mgs3": {
        "order": ["base", "hq", "update"],       # HQ before Update; Update last
        "roles": {
            "base": {
                "status": "MGS3 Better Audio",
                "short": "Better Audio (main file)",
                "checklist": "MGS3 — Better Audio (main file)",
                "nexus": "the main file, shown as version 1.0",
                "log": "MGS3 Better Audio",
                "default": True,
            },
            "hq": {
                "status": "MGS3 HQ ending cutscenes",
                "short": "HQ ending cutscenes",
                "checklist": "MGS3 — HQ ending cutscenes (optional)",
                "nexus": 'the file called "HQ Ending Cutscenes"',
                "log": "MGS3 HQ ending cutscenes (optional)",
                "default": False,
                "note": HQ_ENDING_DISCLAIMER,
            },
            "update": {
                "status": "MGS3 Better Audio update",
                "short": "Audio update",
                "checklist": "MGS3 — Better Audio update (recommended)",
                "nexus": 'the small file called "Update 2.0" (about 25 MB)',
                "log": "MGS3 Better Audio update",
                "default": True,
                "note": UPDATE_NOTE,
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Payload signatures, read from the REAL NexusMods archives (August 2026):
#
#   MGS2 "Full Version"      3821 files  us/demo, us/demo2, us/movie,
#                                        us/movievr, us/vox (the smaller Lite
#                                        archive is identified by its Nexus id)
#   MGS3 main file           6053 files  us/demo, us/movie, us/vox
#   MGS3 "Update 2.0"           3 files  us/demo/_bp/ + us/vox/_bp/
#   MGS3 "HQ Ending Cutscenes"  2 files  us/demo/_bp/m680_*x.sdt only
#
# Two things fall out of that, and both beat guessing from file size:
#   • us/demo2/ and us/movievr/ exist ONLY in MGS2 (71 entries there, 0 in
#     MGS3), so the GAME can be proven from contents even when the file has
#     been renamed and carries no NexusMods id.
#   • a base pack is thousands of files; the patches are 2-3. So "is this the
#     main file or a patch" is a content question, not a size question.
# ---------------------------------------------------------------------------
MGS2_ONLY_DIRS = ("us/demo2/", "us/movievr/")
MGS3_BASE_DIRS = ("us/demo/", "us/movie/", "us/vox/")
AUDIO_BASE_MIN_FILES = 150      # a full pack; the real ones are 3821 / 6053
AUDIO_PATCH_MAX_FILES = 20      # a patch; the real ones are 2 and 3
# m680 is MGS3's ending chapter, which is exactly what the HQ pack replaces.
HQ_ENDING_SCENE = "m680"


def audio_version(path: Path) -> tuple[int, int] | None:
    """Parse (major, minor) from a NexusMods download filename."""
    m = NEXUS_SUFFIX.search(path.name)
    return (int(m.group(2)), int(m.group(3))) if m else None


def audio_modid(path: Path) -> int | None:
    """Parse the NexusMods mod id from a download filename."""
    m = NEXUS_SUFFIX.search(path.name)
    return int(m.group(1)) if m else None


AUDIO_EXTS = (".sdt", ".sdx", ".xxs")


def entries_look_like_audio(entries) -> bool:
    """True if these archive members look like an MGS audio payload.

    Matching is ANCHORED on purpose: a bare "us/" substring also matches
    "bonus/", and a bare ".sdt" matches any name merely containing it, so an
    unrelated archive could slip into the confirm-to-accept path.
    """
    for raw in entries:
        e = raw.strip().replace("\\", "/").lower()
        if not e:
            continue
        if e.startswith("us/") or "/us/" in e:
            return True
        if e.rstrip("/").endswith(AUDIO_EXTS):
            return True
    return False


def probe_audio_archive(path: Path) -> bool:
    """Cheap sanity check that this really is an MGS audio mod archive."""
    p = subprocess.run([tar_cmd(), "-tf", str(path)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return False
    return entries_look_like_audio(p.stdout.splitlines())


def open_url(url: str) -> bool:
    if IS_WINDOWS:
        try:
            os.startfile(url)          # noqa: S606 — opens the default browser
            return True
        except OSError:
            return False
    if not shutil.which("xdg-open"):
        return False
    try:
        subprocess.Popen(["xdg-open", url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def find_qdbus() -> str | None:
    """Locate a qdbus binary. Naming varies: Arch/SteamOS ships qdbus6."""
    for name in ("qdbus", "qdbus6", "qdbus-qt6", "qdbus-qt5"):
        p = shutil.which(name)
        if p:
            return p
    return None


def copy_to_clipboard(text: str) -> bool:
    """Put `text` on the clipboard: clip.exe on Windows, klipper D-Bus on KDE.

    Lets the user paste the launch options straight into Steam instead of
    transcribing them. Best-effort: returns False when no clipboard is
    reachable, and nothing else changes.
    """
    if IS_WINDOWS:
        try:
            r = subprocess.run(["clip"], input=text, text=True, timeout=10)
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    qdbus = find_qdbus()
    if not qdbus:
        return False
    try:
        r = subprocess.run(
            [qdbus, "org.kde.klipper", "/klipper",
             "org.kde.klipper.klipper.setClipboardContents", text],
            capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# -- role identification (unit-tested) --------------------------------------
def audio_archive_profile(path: Path) -> dict | None:
    """Structural profile of an archive, or None if unreadable/not an archive."""
    p = subprocess.run([tar_cmd(), "-tf", str(path)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return None
    entries = [ln for ln in p.stdout.splitlines() if ln and not ln.endswith("/")]
    norm = [e.strip().replace("\\", "/").lower() for e in entries]
    return {
        "entries": norm,
        "file_count": len(entries),
        "size": path.stat().st_size if path.is_file() else 0,
        "is_audio": entries_look_like_audio(entries),
        "modid": audio_modid(path),
        "version": audio_version(path),
        "name": path.name.lower(),
    }


def audio_game_from_entries(entries) -> str | None:
    """Which game this payload belongs to, from CONTENTS alone, or None.

    Content beats filenames: this identifies a renamed archive that carries no
    NexusMods id. Only returns a game when the evidence is positive — a small
    patch is too little content to prove anything, so it returns None and the
    caller falls back to the id in the filename (or asks).
    """
    if any(e.startswith(MGS2_ONLY_DIRS) for e in entries):
        return "mgs2"            # us/demo2 and us/movievr are MGS2-only
    if len(entries) >= AUDIO_BASE_MIN_FILES and all(
            any(e.startswith(d) for d in MGS3_BASE_DIRS) for e in entries):
        return "mgs3"            # a full pack with only MGS3's folders
    return None


def classify_mgs3_role(profile: dict) -> tuple[str | None, bool]:
    """(role, confident) for an MGS3 audio archive, from its contents.

    Matched against the real archives (see the signature notes above), so this
    works on renamed files. confident=False still means "ask the user" rather
    than guess, which is what happens for a patch we don't recognise.
    """
    entries = profile.get("entries") or []
    n = profile["file_count"]

    # A full pack is thousands of files; the patches are 2-3.
    if n >= AUDIO_BASE_MIN_FILES:
        return "base", True

    if n and n <= AUDIO_PATCH_MAX_FILES:
        touches_vox = any(e.startswith("us/vox/") for e in entries)
        touches_demo = any(e.startswith("us/demo/") for e in entries)
        ending_only = all(HQ_ENDING_SCENE in Path(e).name for e in entries)
        # The Update fixes lines in both the cutscene and codec trees.
        if touches_demo and touches_vox:
            return "update", True
        # The HQ pack replaces only the ending cutscenes (scene m680).
        if touches_demo and not touches_vox and ending_only:
            return "hq", True
        # Some other small patch — say so instead of inventing an answer.
        return None, False
    return None, False


def validate_audio_for_role(path: Path, game_key: str,
                            role: str) -> tuple[str, str]:
    """Classify a file against the role it's being selected for.

    Returns (verdict, message). verdict is one of:
      ok               — confidently matches; use it silently
      not_audio        — not an MGS audio archive at all  (REJECT outright)
      wrong_game       — the OTHER game's audio mod  (REJECT outright)
      unknown_mod      — some other Nexus mod id; ask (pages get re-uploaded)
      missing_identity — audio, but no Nexus mod-id to confirm the GAME; a
                         renamed file can't be size-guessed into a silent pass
      mismatch         — confidently looks like a DIFFERENT MGS3 component
      ambiguous        — right game, but the exact MGS3 component can't be proven

    not_audio and wrong_game are hard rejects. Everything else short of a
    confident match needs the user to confirm.

    The GAME is established from the payload where possible, so a renamed
    archive with no NexusMods id in its name is still accepted silently; the
    id is only a fallback when the contents can't prove it.
    """
    prof = audio_archive_profile(path)
    if prof is None or not prof["is_audio"]:
        return "not_audio", ("doesn't look like an MGS audio archive — no us/ "
                             "folder or .sdt/.sdx/.xxs files inside")
    other = "mgs3" if game_key == "mgs2" else "mgs2"
    exp_modid, other_modid = AUDIO_MODID[game_key], AUDIO_MODID[other]

    # 1. Contents are the strongest evidence of which game this is.
    by_content = audio_game_from_entries(prof["entries"])
    if by_content == other:
        return "wrong_game", (f"is the {other.upper()} audio mod — its files "
                              f"are {other.upper()}'s, not {game_key.upper()}'s")

    # 2. The NexusMods id in the filename, when the contents were inconclusive.
    if by_content is None:
        if prof["modid"] == other_modid:
            return "wrong_game", (f"is from the {other.upper()} audio mod page, "
                                  f"not {game_key.upper()}'s")
        if prof["modid"] is not None and prof["modid"] != exp_modid:
            # Nexus has reorganised these pages before, forcing authors to
            # re-upload under new ids — so ask rather than dead-end a valid file.
            return "unknown_mod", (f"comes from NexusMods mod #{prof['modid']}, "
                                   f"not the one expected for "
                                   f"{game_key.upper()} (#{exp_modid})")

    if game_key == "mgs2":
        if by_content == "mgs2" or prof["modid"] == exp_modid:
            return "ok", "ok"      # right game, and MGS2 has one component
        return "missing_identity", ("can't be confirmed as the MGS2 audio mod "
                                    "from its name or its contents")
    guess, confident = classify_mgs3_role(prof)
    if confident and guess == role:
        return "ok", "ok"
    if confident and guess is not None and guess != role:
        named = AUDIO_SPECS["mgs3"]["roles"][guess]["status"]
        return "mismatch", f"looks like {named}"
    return "ambiguous", "an MGS3 audio archive, but the exact component"


def order_audio_components(game_key: str, provided: dict) -> list[dict]:
    """Order the provided {role: Path} into install order for `game_key`."""
    spec = AUDIO_SPECS[game_key]
    out = []
    for role in spec["order"]:
        p = provided.get(role)
        if p is not None:
            r = spec["roles"][role]
            out.append({"game": game_key, "role": role, "log": r["log"],
                        "status": r["status"], "short": r["short"],
                        "path": p, "filename": Path(p).name})
    return out


def build_audio_checklist(hdfix_keys) -> list[tuple[str, str, bool]]:
    """Checklist of the audio components for the chosen games.

    Every component is its own independently-selectable item.
    """
    items: list[tuple[str, str, bool]] = []
    order = [("mgs2", "base"), ("mgs3", "base"), ("mgs3", "update"),
             ("mgs3", "hq")]
    for game, role in order:
        if game not in hdfix_keys:
            continue
        r = AUDIO_SPECS[game]["roles"][role]
        # Labels are written game-first and jargon-free in AUDIO_SPECS. Rows
        # must stay short: kdialog checklist rows do not wrap, so a long label
        # is ellipsized or pushes the dialog past the Deck's 1280px screen.
        # Longer explanations belong in the header — see AUDIO_CHECKLIST_TEXT.
        items.append((f"{game}:{role}", r["checklist"][:CHECKLIST_LABEL_MAX],
                      r["default"]))
    return items


def audio_status_text(audio: dict) -> str:
    """Per-game audio block (with chosen filenames) for the summary screen.

    Rows use the short role names, since the game is already the heading.
    """
    blocks = []
    for key in ("mgs2", "mgs3"):
        if key not in audio:
            continue
        spec = AUDIO_SPECS[key]
        by_role = {c["role"]: c for c in audio[key]}
        lines = [f"{key.upper()} audio"]
        for role in spec["order"]:
            r = spec["roles"][role]
            c = by_role.get(role)
            if c is None and not r["default"]:
                continue          # don't list opt-in extras nobody asked for
            lines.append(f"  {r['short']}: "
                         + (c["filename"] if c else "not chosen"))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def audio_recommendation_note(audio: dict) -> str:
    """One concise note if MGS3's main file goes in without its update."""
    comps = audio.get("mgs3", [])
    roles = {c["role"] for c in comps}
    if "base" in roles and "update" not in roles:
        return ("Note: the recommended MGS3 audio update wasn't chosen. You "
                "can add it later by running this again.")
    return ""


# -- interactive collection -------------------------------------------------
def request_audio_archive(ui: UI, game_key: str, role: str,
                          chosen: dict[str, tuple], accepted=None) -> Path | None:
    """Ask for ONE component's archive: Select file / Open Nexus / Skip.

    `chosen` maps already-picked resolved-path -> (game, role) so the same file
    can't be silently used for two components. Nexus is only opened when the
    user explicitly asks; it's never the default or a repeated prompt.
    """
    rspec = AUDIO_SPECS[game_key]["roles"][role]
    nexus = GAMES[game_key]["audio_page"]
    title = rspec["status"]                      # e.g. "MGS3 Better Audio update"
    # Straight to the file picker: ticking the box in the checklist already said
    # "yes, I want this". The menu is only shown if that picker is cancelled.
    sel = ui.pick_archive_file(f"Choose your {title} file")
    while True:
        if sel:
            p = Path(sel).resolve()
            verdict = _accept_audio_file(ui, p, game_key, role, chosen, rspec, accepted)
            if verdict is not None:
                return verdict
        choice = ui.menu(
            title,
            f"On NexusMods this is {rspec['nexus']}.\n\n"
            "What would you like to do?",
            [("select", "Choose the file…"),
             ("nexus", "Open the NexusMods page"),
             ("skip", f"Skip {title}")])
        if choice in (None, "skip"):
            return None
        if choice == "nexus":
            if not open_url(nexus):
                ui.info(f"Open this page to download it:\n{nexus}")
            else:
                ui.info("Once it has downloaded, choose “Choose the file…”.")
            sel = None
            continue
        sel = ui.pick_archive_file(f"Choose your {title} file")


def _accept_audio_file(ui: UI, p: Path, game_key: str, role: str,
                       chosen: dict[str, tuple], rspec: dict, accepted=None) -> Path | None:
    """Vet one chosen file. Returns it if usable, else None to re-ask.

    Files that are clearly not MGS audio, or belong to the other game, are
    rejected outright. Anything the payload can't prove is confirmed by the
    user rather than silently accepted.
    """
    name = rspec["status"]
    prior = chosen.get(str(p))
    if prior is not None:
        other = AUDIO_SPECS[prior[0]]["roles"][prior[1]]["status"]
        ui.info(f"{p.name}\n\nThat file is already being used for {other}. "
                "Please choose a different one.")
        return None
    # Bracket both classification and user confirmation with the same digest.
    # A path alone never proves which bytes the user selected or confirmed.
    try:
        if p.is_symlink() or not p.is_file():
            raise OSError("not a regular archive")
        digest = sha256_file(p)
        verdict, msg = validate_audio_for_role(p, game_key, role)
        if sha256_file(p) != digest:
            raise OSError("archive changed during classification")
        if verdict in ("not_audio", "wrong_game"):
            ui.info(f"{p.name}\n\nThis {msg}.\n\nPlease choose a different file.")
            return None
        if verdict != "ok":
            if verdict == "mismatch":
                text = f"This {msg}, not {name}."
            elif verdict == "ambiguous":
                text = f"This appears to be {msg} could not be confirmed."
            else:
                text = f"This {msg}."
            if not ui.yesno(f"{p.name}\n\n{text}\n\nUse it as your {name} file anyway?"):
                return None
        if p.is_symlink() or not p.is_file() or sha256_file(p) != digest:
            raise OSError("archive changed during confirmation")
    except OSError as e:
        ui.info(f"{p.name}\n\nFile could not be accepted: {e}. Please select it again.")
        return None
    if accepted is not None:
        accepted[str(p)] = AudioAcceptance(str(p.resolve()), digest, game_key,
                                           role, verdict, verdict != "ok")
    return p


def collect_audio_archives(ui: UI, hdfix_keys) -> dict[str, list[dict]]:
    """Drive Better Audio selection; returns {game: [ordered components]}.

    Every checked component is collected independently — no component blocks
    on another. Only the files for CHECKED items are requested.
    """
    items = build_audio_checklist(hdfix_keys)
    if not items:
        return {}
    picked = ui.checklist("Better Audio (optional)", AUDIO_CHECKLIST_TEXT,
                          items)
    if picked is None:
        # Cancel is ambiguous on this screen: it might mean "skip the audio"
        # or just a mis-tap that would silently discard the recommended packs.
        # One confirm — and deliberately no Nexus nagging in it.
        if not ui.yesno("Skip the Better Audio packs entirely?\n\n"
                        "They're recommended (the MGS2 one also fixes a "
                        "cutscene crash), and you can add them later by "
                        "running this again.\n\n"
                        "Yes = skip audio    No = go back"):
            picked = ui.checklist("Better Audio (optional)",
                                  AUDIO_CHECKLIST_TEXT, items)
    if not picked:            # skipped, or nothing ticked on purpose
        return {}
    picked = set(picked)
    chosen: dict[str, tuple] = {}
    accepted = {}
    audio: dict[str, list[dict]] = {}
    for game in ("mgs2", "mgs3"):
        if game not in hdfix_keys:
            continue
        provided: dict[str, Path] = {}
        for role in AUDIO_SPECS[game]["order"]:     # base, hq, update
            if f"{game}:{role}" in picked:
                p = request_audio_archive(ui, game, role, chosen, accepted)
                if p is not None:
                    provided[role] = p
                    chosen[str(p)] = (game, role)
        if provided:
            audio[game] = order_audio_components(game, provided)
            for component in audio[game]:
                component["acceptance"] = accepted[str(component["path"])]
    return audio


# ---------------------------------------------------------------------------
# Launch-options reference file (the one manual step, saved for copy-paste)
# ---------------------------------------------------------------------------
def launch_option_for(key: str) -> str:
    g = GAMES[key]
    return g["launch"] if g.get("kind") == "m2fix" else LAUNCH_OPTIONS


def build_launch_options_text(found_keys) -> str:
    """A copy-paste reference containing ONLY the games installed this run."""
    lines = [
        "MGS MASTER COLLECTION — STEAM LAUNCH OPTIONS",
        "=============================================",
        "",
        "In Steam, right-click each game:",
        "Properties → General → Launch Options",
        "",
    ]
    for key in ("mgs1", "mgs2", "mgs3"):        # stable, game-number order
        if key not in found_keys:
            continue
        short = GAMES[key]["short"]
        lines += [short, "-" * len(short), launch_option_for(key), ""]
    lines += ["These launch options are required for the installed fix mods "
              "to load.", ""]
    return "\n".join(lines)


def _windows_desktop_from_registry() -> Path | None:
    """The registry knows the true Desktop even when OneDrive has moved it.

    Split out so tests can stub it: on a real Windows box it succeeds, which
    would otherwise make the fallback branch untestable there.
    """
    try:
        import winreg
        key = (r"Software\Microsoft\Windows\CurrentVersion"
               r"\Explorer\User Shell Folders")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            raw = winreg.QueryValueEx(k, "Desktop")[0]
        d = Path(os.path.expandvars(raw))
        if d.is_dir():
            return d
    except (OSError, ImportError):
        pass
    return None


def resolve_desktop_dir() -> Path | None:
    """The user's real Desktop, honouring a relocated/redirected one."""
    if IS_WINDOWS:
        d = _windows_desktop_from_registry()
        if d is not None:
            return d
        d = Path.home() / "Desktop"
        return d if d.is_dir() else None
    if shutil.which("xdg-user-dir"):
        try:
            r = subprocess.run(["xdg-user-dir", "DESKTOP"],
                               capture_output=True, text=True)
            out = r.stdout.strip()
            # xdg-user-dir returns $HOME when Desktop is unset — reject that.
            if r.returncode == 0 and out and Path(out) != Path.home():
                p = Path(out)
                if p.is_dir():
                    return p
        except OSError:
            pass
    d = Path.home() / "Desktop"
    return d if d.is_dir() else None


def save_launch_options_file(ui: UI, found_keys, log,
                             timestamp: str | None = None) -> Path | None:
    """Write the launch-options reference to the Desktop (or a chosen folder).

    Resolves the real Desktop even if renamed/relocated; if none exists the
    user picks a folder. Never clobbers an existing file without consent —
    the user chooses overwrite, else a timestamped name is used.
    """
    text = build_launch_options_text(found_keys)
    dest_dir = resolve_desktop_dir()
    if dest_dir is None:
        chosen = ui.pick_dir("No Desktop folder found — choose where to save "
                             "'MGS Steam Launch Options.txt'")
        if not chosen:
            return None
        dest_dir = Path(chosen)

    path = dest_dir / "MGS Steam Launch Options.txt"
    if path.exists():
        # Our own file from a previous run. If what we'd write is identical
        # (the common case: a repair with the same games), keep it silently —
        # asking "overwrite?" on every re-run is pure nagging. Only genuinely
        # different content is worth a question.
        try:
            if path.read_text(encoding="utf-8") == text:
                log(f"  ✓ launch options already saved → {path}")
                return path
        except OSError:
            pass
        if not ui.yesno(f"'{path.name}' already exists in:\n{dest_dir}\n\n"
                        "Overwrite it?  (No = save with a timestamp instead)"):
            ts = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
            path = dest_dir / f"MGS Steam Launch Options {ts}.txt"
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as e:
        ui.error(f"Couldn't save the launch-options file:\n{e}")
        return None
    log(f"  ✓ saved launch options → {path}")
    return path


# ---------------------------------------------------------------------------
# Application icon.
#
# The .desktop shortcut is the only file the user downloads, and Icon= can only
# name a theme icon or an absolute path — the Desktop Entry spec has no way to
# carry image data, so a self-contained custom icon is impossible.
#
# The shortcut therefore ships with `package-x-generic`, the stock cardboard-box
# icon: on-theme for MGS, and guaranteed to render because every icon theme has
# it. On first run we install the nicer hand-drawn box below into the user's own
# icon theme and repoint the shortcut at it. Purely cosmetic — every failure
# here is ignored, and the stock icon is a perfectly good resting state.
# ---------------------------------------------------------------------------
APP_ICON_NAME = "mgs-mod-kit"
APP_ICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128" role="img" aria-label="MGS Master Collection Mod Kit">
  <defs>
    <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#17222d"/>
      <stop offset="1" stop-color="#090e13"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#4ade80"/>
      <stop offset="1" stop-color="#38bdf8"/>
    </linearGradient>
    <linearGradient id="topF" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e8b071"/>
      <stop offset="1" stop-color="#d29a58"/>
    </linearGradient>
    <linearGradient id="leftF" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#a97331"/>
      <stop offset="1" stop-color="#8a5a22"/>
    </linearGradient>
    <linearGradient id="rightF" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#c68a45"/>
      <stop offset="1" stop-color="#a56f2c"/>
    </linearGradient>
  </defs>

  <!-- tile -->
  <rect width="128" height="128" rx="27" fill="url(#tile)"/>
  <g stroke="#22323f" stroke-width="1" opacity="0.55">
    <path d="M32 10V118M64 10V118M96 10V118"/>
    <path d="M10 40H118M10 72H118M10 104H118"/>
  </g>
  <rect x="1.5" y="1.5" width="125" height="125" rx="25.5" fill="none"
        stroke="url(#accent)" stroke-width="3" opacity="0.55"/>

  <!-- isometric cardboard box -->
  <g stroke="#553613" stroke-width="3" stroke-linejoin="round">
    <path d="M64 30 L100 50 L64 70 L28 50 Z" fill="url(#topF)"/>
    <path d="M28 50 L64 70 L64 104 L28 84 Z" fill="url(#leftF)"/>
    <path d="M100 50 L64 70 L64 104 L100 84 Z" fill="url(#rightF)"/>
  </g>

  <!-- flap seam across the lid, and packing tape over it -->
  <path d="M28 50 L100 50" stroke="#6d451a" stroke-width="2.5" opacity="0.85"/>
  <path d="M46 40 L82 60" stroke="#f0d3a6" stroke-width="7" opacity="0.5"
        stroke-linecap="round"/>
  <!-- tape running down the front corner -->
  <path d="M64 70 L64 104" stroke="#6d451a" stroke-width="2.5" opacity="0.6"/>
</svg>
"""


def install_app_icon(log) -> bool:
    """Write the icon into ~/.local/share/icons and refresh the icon cache."""
    theme = Path.home() / ".local/share/icons/hicolor"
    dest = theme / "scalable/apps" / f"{APP_ICON_NAME}.svg"
    try:
        if dest.is_file() and dest.read_text(encoding="utf-8") == APP_ICON_SVG:
            return True                      # already current
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(APP_ICON_SVG, encoding="utf-8")
    except OSError:
        return False
    for cmd in (["gtk-update-icon-cache", "-qtf", str(theme)],
                ["kbuildsycoca6"], ["kbuildsycoca5"]):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, capture_output=True, timeout=30)
            except (OSError, subprocess.SubprocessError):
                pass
    log(f"    ✓ installed the app icon ({APP_ICON_NAME})")
    return True


def retheme_shortcuts(log) -> int:
    """Point OUR shortcuts at the installed icon. Returns how many changed.

    Only files whose Exec refers to this project are touched, so nothing else
    on the user's Desktop can be modified.
    """
    changed = 0
    seen: set[Path] = set()
    for d in (resolve_desktop_dir(), Path.home() / "Desktop",
              Path.home() / ".local/share/applications"):
        if d is None or not d.is_dir() or d in seen:
            continue
        seen.add(d)
        for f in sorted(d.glob("*.desktop")):
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            if not any(m in text for m in ("mgs-mc-modkit",
                                           "mgs-mc-deck-modkit")):
                continue                     # not ours — leave it alone
            if re.search(r"(?m)^Icon=%s$" % re.escape(APP_ICON_NAME), text):
                continue                     # already themed
            new = re.sub(r"(?m)^Icon=.*$", f"Icon={APP_ICON_NAME}", text)
            if new == text:
                continue
            try:
                f.write_text(new, encoding="utf-8")
                changed += 1
            except OSError:
                pass
    if changed:
        log(f"    ✓ updated {changed} shortcut icon(s)")
    return changed


def apply_branding(log) -> None:
    """Best-effort: install the icon and retheme our shortcuts. Never raises.

    Linux-only — Windows has no icon themes or .desktop files; its .cmd
    shortcut has no icon of its own to fix up.
    """
    if IS_WINDOWS:
        return
    try:
        if install_app_icon(log):
            retheme_shortcuts(log)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Entry mode
#
# The shortcut is the user's ONLY entry point, so it must never delete itself:
# repair, adding a component later, and uninstalling all need it. When a
# previous install is detected we ask what they want to do instead.
# ---------------------------------------------------------------------------
def already_modded(found: dict) -> list[str]:
    """Game keys that carry a record from a previous run of this kit."""
    return [k for k, (d, _r) in found.items()
            if (d / MODKIT_DIRNAME / MANIFEST_NAME).is_file()]


# Only these keys are restored from a previous run — anything else in a manifest
# is ignored, so a hand-edited or future-version record can't inject values.
# update_check is deliberately absent: it is no longer user-settable and must
# stay off, so a manifest written by an older version can never restore it.
SAVED_OPT_KEYS = ("button_icons", "audio_mode", "hq_movies", "skip_splash",
                  "skip_launcher")
SAVED_BUTTON_ICONS = (
    "Steam Deck", "Xbox One", "PlayStation 5", "PlayStation 2",
    "PlayStation 4", "Nintendo Switch", "Keyboard / Mouse")
SAVED_AUDIO_MODES = ("Stereo (2.0)", "Surround Sound (5.1)")


def load_saved_opts(found: dict) -> dict:
    """Settings chosen on a previous run, so re-runs don't re-ask everything.

    Reads the newest manifest that has a settings block. Unparseable records are
    ignored here (the install path raises on those, separately).
    """
    best: dict = {}
    best_stamp = ""
    for _k, (d, _r) in found.items():
        mf = d / MODKIT_DIRNAME / MANIFEST_NAME
        if not mf.is_file():
            continue
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            saved = data.get("settings")
            if not isinstance(saved, dict):
                continue
            stamp = str(data.get("installed_utc", ""))
        except (ValueError, OSError, UnicodeError):
            continue
        if stamp >= best_stamp:
            best_stamp = stamp
            best = saved
    out = {}
    for k in SAVED_OPT_KEYS:
        if k in best:
            v = best[k]
            if (k == "button_icons" and isinstance(v, str)
                    and v in SAVED_BUTTON_ICONS):
                out[k] = v
            elif (k == "audio_mode" and isinstance(v, str)
                  and v in SAVED_AUDIO_MODES):
                out[k] = v
            elif k in ("hq_movies", "skip_splash", "skip_launcher") and \
                    isinstance(v, bool):
                out[k] = v
    return out


def choose_mode(ui: UI, found: dict) -> str | None:
    """'install' | 'uninstall' | None(quit). Only asked when something exists."""
    modded = already_modded(found)
    if not modded:
        return "install"
    names = ", ".join(GAMES[k]["short"] for k in modded)
    return ui.menu(
        "MGS Mod Kit",
        f"{names} already set up by this installer.\n\nWhat would you like to "
        "do?",
        [("install", "Install or repair mods"),
         ("uninstall", "Remove the mods"),
         ("quit", "Quit")])


# ---------------------------------------------------------------------------
# Uninstall flow
# ---------------------------------------------------------------------------
def run_uninstall(ui: UI, log) -> int:
    found = find_games()
    if not found:
        manual = ui.pick_dir("Select the MGS game folder to un-mod")
        if not manual:
            ui.error("No install selected. Aborting.")
            return 1
        d = Path(manual)
        for key, g in GAMES.items():
            if (d / g["exe"]).is_file():
                found[key] = (d, Path.home())
        if not found:
            ui.error(f"No Master Collection game executable found in:\n{d}")
            return 1

    # Offer any game this kit touched. The whole mgs-modkit folder counts, not
    # just a readable manifest — if the record was lost or damaged, the backups
    # of the user's original files are still in there and must be recoverable.
    modded = {k: v for k, v in found.items()
              if (v[0] / MODKIT_DIRNAME).is_dir()
              or has_untracked_mods(v[0])}
    if not modded:
        ui.info("Nothing to remove — none of the games found on this machine "
                "was set up by this installer.")
        return 0

    if len(modded) > 1:
        picks = ui.checklist(
            "MGS Mod Kit — Uninstall",
            "Remove this kit's mods from:",
            [(k, f"{GAMES[k]['name']}  ({modded[k][0]})", True)
             for k in modded],
        )
        if not picks:
            ui.error("Nothing selected. Aborting.")
            return 1
        modded = {k: v for k, v in modded.items() if k in picks}

    names = ", ".join(GAMES[k]["short"] for k in modded)
    if not ui.yesno(
        f"Uninstall this kit's mods from {names}?\n\n"
        "Files this kit added will be removed and any originals it backed up "
        "restored. Your game saves are untouched.\n\n"
        "Make sure THE GAMES AND STEAM'S DOWNLOADS ARE CLOSED. Proceed?"
    ):
        return 0

    all_ok = True
    outcomes = []
    for key in modded:
        g, (game_dir, _) = GAMES[key], modded[key]
        log(f"\n=== Uninstalling {g['name']} ===")
        notes, ok = uninstall_game(game_dir, log)
        all_ok = all_ok and ok
        outcomes.append(f"{g['short']}: " + ("removed" if ok else "action required") + "\n" + "\n".join(notes))
        for note in notes:
            log(f"    • {note}")

    if not all_ok:
        ui.error("Removal needs attention:\n\n" + "\n\n".join(outcomes))
        return 1

    ui.info(
        f"✅ Mods removed from {names}.\n\n"
        + ("" if IS_WINDOWS else
           "One thing to tidy up in Steam yourself: right-click each game → "
           "Properties → Launch Options and clear the line you pasted in.\n\n")
        + "The mods leave behind a 'logs' folder and steam_appid.txt — delete "
          "those if you want the folder spotless.\n\n"
          "(Steam's Verify integrity restores original game files, but it "
          "will not delete leftover mod files.)")
    return 0


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------
def has_untracked_mods(game_dir: Path) -> bool:
    return any((game_dir / rel).exists() for rel in (
        "winhttp.dll", "wininet.dll", "plugins/MGSHDFix.asi",
        "d3d11.dll", "dinput8.dll", "MGSM2Fix64.asi", *LEGACY_M2FIX_FILES))


def start_session_log():
    try:
        directory = app_data_dir() / "logs"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8] + ".log")
        # Keep the 20 most recent sessions; game recovery records are separate.
        for old in sorted(directory.glob("*.log"))[:-19]:
            old.unlink(missing_ok=True)
        stream = path.open("w", encoding="utf-8", buffering=1)
        return path, stream
    except OSError:
        return None, None


def version_tuple(tag: str) -> tuple:
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    return tuple(map(int, match.groups())) if match else ()


def kit_update_notice(log) -> str:
    """Advisory only. Never download or execute a new installer automatically."""
    try:
        cache = app_data_dir() / "update-check.json"
        data = json.loads(cache.read_text()) if cache.exists() else {}
        if not isinstance(data, dict):
            data = {}
        if time.time() - float(data.get("checked", 0)) >= 86400:
            request = urllib.request.Request(
                "https://api.github.com/repos/cntrl-alt-lenny/mgs-mc-modkit/releases/latest",
                headers={"User-Agent": "MGS-Mod-Kit", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(request, timeout=3) as response:
                release = json.loads(response.read(256 * 1024))
            tag = release.get("tag_name", "")
            if not version_tuple(tag) or release.get("prerelease") or release.get("draft"):
                return ""
            data = {"checked": time.time(), "tag": tag}
            atomic_bytes(cache, json.dumps(data).encode())
        tag = str(data.get("tag", ""))
        if version_tuple(tag) > version_tuple(MODKIT_VERSION):
            return (f"A newer kit ({tag}) is available. Download its shortcut from "
                    "https://github.com/cntrl-alt-lenny/mgs-mc-modkit/releases/latest. "
                    f"This run still uses verified kit {MODKIT_VERSION}.")
    except (OSError, ValueError, TypeError, urllib.error.URLError, AttributeError) as e:
        log(f"Update notice unavailable ({e}); continuing with this pinned kit.")
    return ""


def run_with_progress(prog, operation):
    """Keep all UI calls on the creating thread while archive/network work runs."""
    # Non-GUI implementations used by integrations can run synchronously.
    if not hasattr(prog, "pump"):
        return operation()
    result, failure = [], []

    def worker():
        try:
            result.append(operation())
        except BaseException as e:
            failure.append(e)

    thread = threading.Thread(target=worker, name="mgs-install")
    thread.start()
    try:
        while thread.is_alive():
            prog.pump()
            thread.join(0.1)
        prog.pump()
    except BaseException:
        prog.cancel_event.set()
        while thread.is_alive():
            thread.join(0.1)
        raise
    if failure:
        raise failure[0]
    return result[0] if result else None


def options_for_game(key: str, location: tuple, defaults: dict, log) -> dict:
    game_dir, _ = location
    opts = dict(defaults)
    opts.update(load_saved_opts({key: location}))
    if (game_dir / MODKIT_DIRNAME / JOURNAL_NAME).exists():
        # The worker recovers under the lock before reading potentially interrupted files.
        return opts
    if GAMES[key].get("kind", "hdfix") == "hdfix":
        path = game_dir / "plugins/MGSHDFix.settings"
        if path.is_file():
            text = path.read_text(encoding="utf-8-sig")
            text = migrate_settings(text)
            parser = validate_settings(text)
            opts["_existing_settings"] = text
            opts["button_icons"] = parser["Controller Settings"]["Button Icons"].strip('"')
            opts["audio_mode"] = parser["System Specific Fixes"]["Audio Output Mode"].strip('"')
            opts["skip_launcher"] = parser["Launcher and Splashscreens"]["Skip Launcher"] == "1"
            opts["skip_splash"] = parser["Launcher and Splashscreens"]["Skip In-Game Splashscreens"] == "1"
        for path in sorted(game_dir.glob("*_savedata_win/*/launcher/launcher_sv")):
            try:
                value = _read_launcher_sv(path).get("HiresoMovie")
                if value in ("0", "1"):
                    opts["hq_movies"] = value == "1"
                    break
            except (ValueError, OSError):
                continue
    else:
        path = game_dir / "MGSM2Fix.ini"
        if path.is_file():
            text = path.read_text(encoding="utf-8-sig")
            parser = parse_ini(text)
            opts["_existing_m2fix"] = text
            for section in parser.sections():
                if "StartGame" in parser[section]:
                    value = parser[section]["StartGame"].casefold()
                    if value not in ("true", "false"):
                        raise RuntimeError("Existing MGSM2Fix StartGame must be true or false")
                    opts["skip_launcher"] = value == "true"
    opts["update_check"] = False
    return opts


# ---------------------------------------------------------------------------
# Current-recipe adapter: planning never changes pins or mod-specific writers.
# ---------------------------------------------------------------------------
def _plan_json(value):
    return json.dumps(value, sort_keys=True, default=lambda x: sorted(x))


def _plan_inputs(game_dir, steam_root):
    """Track directory membership, file identity and recipe configuration inputs.

    Game assets use stat identities; settings/recovery/launcher records also
    use content hashes. No save is copied or modified to collect this snapshot.
    """
    files = []
    for directory, dirs, names in os.walk(game_dir, followlinks=False):
        for name in sorted(dirs + names):
            path = Path(directory) / name
            stat = path.lstat()
            rel = path.relative_to(game_dir).as_posix()
            digest = None
            if path.is_symlink():
                digest = os.readlink(path)
            elif path.is_file() and (
                    rel.startswith(MODKIT_DIRNAME + "/") or
                    name in ("MGSHDFix.settings", "MGSM2Fix.ini", "launcher_sv")):
                # Recovery snapshots can include multi-GB audio: stat identity
                # is sufficient for those; records and config get exact hashes.
                if name in (MANIFEST_NAME, JOURNAL_NAME, "MGSHDFix.settings",
                            "MGSM2Fix.ini", "launcher_sv"):
                    digest = sha256_file(path)
            files.append((rel, stat.st_mode, stat.st_size, stat.st_mtime_ns,
                          stat.st_ctime_ns, stat.st_ino, digest))
    root_stat = game_dir.stat()
    return _plan_json((str(game_dir.resolve()), root_stat.st_dev, root_stat.st_ino,
                       sorted(files), sorted(steamid64s(steam_root))))


def _plan_packages(key, components):
    g = GAMES[key]
    if g.get("kind", "hdfix") == "m2fix":
        packages = [PlanPackage("MGSM2Fix", M2FIX_VERSION, M2FIX_URL, M2FIX_SHA256)]
    else:
        packages = [PlanPackage("MGSHDFix", HDFIX_VERSION, HDFIX_URL, HDFIX_SHA256)]
        for comp in components:
            path = Path(comp["path"])
            if path.is_symlink() or not path.is_file():
                raise ValueError("Supplied audio must be a regular archive")
            accepted = comp.get("acceptance")
            if (not isinstance(accepted, AudioAcceptance) or
                    (accepted.source, accepted.game, accepted.role) !=
                    (str(path.resolve()), key, comp["role"]) or
                    sha256_file(path) != accepted.sha256):
                raise ReplanRequired("Supplied audio acceptance changed; select and confirm again")
            packages.append(PlanPackage(comp["status"], comp["filename"],
                                        accepted.source, accepted.sha256,
                                        comp["role"], accepted))
        packages.append(PlanPackage(f"{g['short']} Community Bugfix Compilation",
                                    g["bugfix_version"], g["bugfix_url"],
                                    g["bugfix_sha256"]))
    return tuple(packages)


def build_install_plan(found, per_game, audio, expected_inputs=None):
    games = []
    for key, (game_dir, steam_root) in found.items():
        if key not in GAMES:
            raise ValueError("Unsupported game recipe")
        game_dir, steam_root = game_dir.resolve(), steam_root.resolve()
        if not (game_dir / GAMES[key]["exe"]).is_file():
            raise ValueError("Game executable is missing")
        if (game_dir / MODKIT_DIRNAME / JOURNAL_NAME).exists():
            raise ReplanRequired("Interrupted installation needs recovery before planning")
        components = audio.get(key, [])
        roles = [c["role"] for c in components]
        expected = [role for role in ("base", "hq", "update") if role in roles]
        incompatible = []
        if roles and (roles != expected or len(set(roles)) != len(roles)):
            incompatible.append("Audio roles must be unique and ordered base, HQ ending, then update")
        if key == "mgs1" and components:
            incompatible.append("This recipe does not support supplied audio")
        if key == "mgs2" and any(r != "base" for r in roles):
            incompatible.append("MGS2 supports only base audio")
        inputs = _plan_inputs(game_dir, steam_root)
        if expected_inputs is not None and inputs != expected_inputs[key]:
            raise ReplanRequired("Inputs changed while choosing options; restart to confirm a fresh plan")
        games.append(PlanGame(key, os.path.normcase(str(game_dir)), str(steam_root),
                              _plan_json(per_game[key]), _plan_packages(key, components),
                              inputs, tuple(incompatible)))
    plan = InstallPlan(tuple(games))
    plan.validate()
    return plan


def _plan_validate_record(game):
    live = Path(game.path)
    root = live / MODKIT_DIRNAME
    if root.is_symlink():
        raise CorruptManifestError("Linked recovery directory; nothing was changed")
    for directory in (root / "staging", root / "rollback", root / "backups"):
        if directory.is_symlink():
            raise CorruptManifestError("Linked transaction directory; backups kept")
    record = root / MANIFEST_NAME
    if record.exists():
        data = _read_record(record)
        _validate_manifest(data, live, root)
        if (data.get("game") != game.key or "added" not in data or
                "overwritten" not in data or not isinstance(data.get("mods", {}), dict)):
            raise CorruptManifestError("Invalid install record; backups kept")
    if (root / "backups").exists():
        for directory, dirs, names in os.walk(root / "backups"):
            if any((Path(directory) / name).is_symlink() for name in dirs + names):
                raise CorruptManifestError("Linked backup; backups kept")


class _PreparationTxn:
    """Run existing recipes in a private virtual game; record replay actions."""
    def __init__(self, game, directory, log):
        self.game_dir = directory / "virtual"
        self.game_dir.mkdir()
        self.game_key, self.log = game.key, log
        self.packages = game.packages
        self.directory = directory
        self.actions, self.identities, self.mods = [], [], {}
        self.destinations = []
        live = Path(game.path)
        for path in live.glob("*_savedata_win/*/launcher/launcher_sv"):
            rel = path.relative_to(live).as_posix()
            _safe_game_path(live, rel)
            dest = self.game_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)

    def install_archive(self, archive, on_progress=None, component=None):
        check_cancelled()
        copied = self.directory / f"payload-{len(self.actions)}{archive.suffix}"
        shutil.copyfile(archive, copied)
        digest = sha256_file(copied)
        package = self.packages[len(self.identities)]
        if digest != package.sha256:
            raise ReplanRequired("Payload differs from its confirmed checksum: " + package.name)
        stage = self.directory / f"stage-{len(self.actions)}"
        stage.mkdir()
        rels = staged_files(copied, stage, on_progress=on_progress)
        rels = validate_payload_paths(rels, self.game_key, component, self.log)
        for rel in rels:
            dest = _safe_game_path(self.game_dir, rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            self.destinations.append((rel, (stage / rel).stat().st_size))
            os.replace(stage / rel, dest)
        self.actions.append(("archive", str(copied), component))
        self.identities.append((str(copied), digest))
        shutil.rmtree(stage)
        return rels

    def write_bytes(self, rel, data):
        dest = _safe_game_path(self.game_dir, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        self.actions.append(("bytes", rel, data))
        self.destinations.append((rel, len(data)))

    def read_text_ours(self, rel, encoding="utf-8"):
        return _safe_game_path(self.game_dir, rel).read_text(encoding=encoding)

    def note_mod(self, name, version):
        self.mods[name] = version


class CurrentRecipeAdapter:
    def __init__(self, log, progress=None):
        self.log, self.progress = log, progress

    def check_cancelled(self):
        check_cancelled()

    def lock(self, game):
        return GameLock(Path(game.path))

    def recheck(self, plan):
        for game in plan.games:
            live = Path(game.path)
            if (live / MODKIT_DIRNAME / JOURNAL_NAME).exists():
                raise ReplanRequired("Recovery is pending; recover and confirm a fresh plan")
            if _plan_inputs(live, Path(game.steam_root)) != game.inputs:
                raise ReplanRequired("Game, settings, saves or recovery inputs changed; confirm a fresh plan")
            for package in game.packages:
                if package.role != "package":
                    path = Path(package.source)
                    if path.is_symlink() or not path.is_file() or sha256_file(path) != package.sha256:
                        raise ReplanRequired("Supplied archive changed; select and confirm again")
            supplied = [p for p in game.packages if p.role != "package"]
            current = _plan_packages(game.key, [])
            if tuple(p for p in game.packages if p.role == "package") != current:
                raise ReplanRequired("Package definitions changed; confirm a fresh plan")
            # Settings writers remain owned by the existing recipe.
            if supplied and GAMES[game.key].get("kind") == "m2fix":
                raise ValueError("Audio is incompatible with this recipe")

    def prepare(self, game, workspace, index):
        _plan_validate_record(game)
        directory = workspace / str(index)
        directory.mkdir()
        tmp = directory / "downloads"
        tmp.mkdir()
        tx = _PreparationTxn(game, directory, self.log)
        g, opts = GAMES[game.key], json.loads(game.settings)
        if self.progress:
            self.progress.update(f"{g['short']} — Preparing all selected payloads", 0)
        if g.get("kind", "hdfix") == "m2fix":
            install_m2fix(tx, tmp, opts, self.log)
        else:
            install_hdfix(tx, tmp, self.log)
            for package in game.packages:
                if package.role != "package":
                    status, reason = validate_audio_for_role(Path(package.source), game.key, package.role)
                    if status != package.acceptance.classification:
                        raise ReplanRequired("Supplied audio classification changed; select and confirm again")
                    # Existing audio recipe/record naming stays unchanged.
                    install_better_audio(tx, [{"path": package.source, "log": package.name,
                                               "status": package.name, "filename": package.version}], self.log)
            install_bugfix(tx, g, tmp, self.log)
            write_settings(tx, g, opts, self.log)
            if not set_launcher_options(tx, g, Path(game.steam_root), opts, self.log):
                raise RuntimeError("A launcher save could not be parsed safely")
        problems = verify_install(g, tx.game_dir)
        if problems:
            raise RuntimeError("Prepared payload verification failed: " + ", ".join(problems))
        # Validate every eventual destination before creating any transaction.
        size = 0
        for rel, payload_size in tx.destinations:
            dest = _safe_game_path(Path(game.path), rel)
            if dest.is_symlink() or (dest.exists() and not dest.is_file()):
                raise ValueError("Destination is not a regular file: " + rel)
            # Extraction + installed payload, original backup + rollback fallback.
            size += payload_size * 2 + (dest.stat().st_size * 3 if dest.exists() else 0)
        shutil.rmtree(tx.game_dir)
        return PreparedGame(game, tuple(tx.actions), tuple(tx.identities),
                            tuple(tx.mods.items()), size)

    def check_prepared(self, prepared):
        for game in prepared.games:
            for source, digest in game.identities:
                path = Path(source)
                if path.is_symlink() or not path.is_file() or sha256_file(path) != digest:
                    raise ReplanRequired("Prepared payload changed; prepare a fresh plan")

    def check_space(self, prepared):
        volumes = {}
        for game in prepared.games:
            path = Path(game.game.path)
            device = path.stat().st_dev
            needed, _ = volumes.get(device, (SPACE_MARGIN_BYTES, path))
            volumes[device] = (needed + game.required_bytes, path)
        for needed, path in volumes.values():
            if free_bytes(path) < needed:
                raise RuntimeError("Not enough free space for the complete prepared installation")

    def execute(self, prepared, index, outcomes):
        game = prepared.game
        tx = None
        try:
            tx = InstallTxn(Path(game.path), game.key, self.log)
            tx.settings = {k: v for k, v in json.loads(game.settings).items() if k in SAVED_OPT_KEYS}
            for number, (action, target, data) in enumerate(prepared.actions):
                check_cancelled()
                if self.progress:
                    self.progress.update(f"{GAMES[game.key]['short']} — Installing prepared files",
                                         (index + number / len(prepared.actions)) * 100 /
                                         len(outcomes))
                if action == "archive":
                    tx.install_archive(Path(target), component=data)
                else:
                    tx.write_bytes(target, data)
            for name, version in prepared.mods:
                tx.note_mod(name, version)
            problems = verify_install(GAMES[game.key], tx.game_dir)
            if problems:
                raise RuntimeError("Verification failed: " + ", ".join(problems))
            check_cancelled()
            tx.commit()
            outcomes[game.key] = "installed and verified"
            if self.progress:
                self.progress.update(f"{GAMES[game.key]['short']} — Complete",
                                     (index + 1) * 100 / len(outcomes))
        except BaseException:
            if tx is None:
                outcomes[game.key] = "not changed; inspect recovery record / lock"
            elif tx.committed:
                outcomes[game.key] = "installed and verified; recovery cleanup needs attention"
            else:
                restored = tx.rollback()
                outcomes[game.key] = "previous setup restored" if restored else "recovery incomplete; backups kept"
            raise


def _main(log, log_path=None) -> int:
    ui = UI()

    import argparse
    ap = argparse.ArgumentParser(add_help=False)
    # --desktop is still accepted so shortcuts from older releases keep working,
    # but it is no longer used: the installer never deletes itself now, because
    # the shortcut is also the way to repair, add components, and uninstall.
    ap.add_argument("--desktop", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--uninstall", action="store_true",
                    help="Reverse a previous install (restore backups, remove "
                         "added files) instead of installing.")
    cli, _ = ap.parse_known_args()

    # Cosmetic, and done first so the shortcut looks right from now on whatever
    # the user does next (including quitting straight away).
    apply_branding(log)

    if cli.uninstall:
        return run_uninstall(ui, log)

    global TAR
    TAR = find_tar()
    if TAR is None:
        ui.error("Your system is missing the archive tool this installer "
                 "needs (bsdtar).\n\n"
                 + ("It ships with Windows 10 and newer as tar.exe, so this "
                    "is unexpected — updating Windows should restore it."
                    if IS_WINDOWS else
                    "On a Steam Deck it's included as standard, so this is "
                    "unexpected — on other Linux systems, install the "
                    "'libarchive' package and run this again."))
        return 1

    # 1. Find the games -----------------------------------------------------
    found = find_games()
    if not found:
        ui.info("Couldn't auto-detect any Master Collection game "
                "(MGS1, MGS2 or MGS3).\n\n"
                "Next you'll be asked to point at a game folder manually "
                "(the one containing 'METAL GEAR SOLID.exe', "
                "'METAL GEAR SOLID2.exe' or 'METAL GEAR SOLID3.exe').")
        manual = ui.pick_dir("Select your MGS1, MGS2 or MGS3 folder")
        if not manual:
            ui.error("No install selected. Aborting.")
            return 1
        d = Path(manual)
        for key, g in GAMES.items():
            if (d / g["exe"]).is_file():
                found[key] = (d, next(iter(steam_roots()),
                                      Path.home() / ".local/share/Steam"))
        if not found:
            ui.error("No Master Collection game executable (METAL GEAR "
                     "SOLID.exe / SOLID2.exe / SOLID3.exe) was found in:\n"
                     f"{d}")
            return 1

    # 1b. Returning user? Offer repair/uninstall instead of assuming install.
    mode = choose_mode(ui, found)
    if mode is None or mode == "quit":
        return 0
    if mode == "uninstall":
        return run_uninstall(ui, log)

    # 2. Which games to process --------------------------------------------
    if len(found) > 1:
        picks = ui.checklist(
            "MGS Mod Kit — Choose Games",
            f"{len(found)} Master Collection games found. Set up mods for:\n\n"
            + "\n".join(f"{GAMES[k]['short']}:  {found[k][0]}" for k in found),
            # Row labels stay short (paths are listed above instead).
            [(k, GAMES[k]["name"][:CHECKLIST_LABEL_MAX], True) for k in found],
        )
        if not picks:
            ui.error("No games selected. Aborting.")
            return 1
        found = {k: v for k, v in found.items() if k in picks}

    # 3. Options -----------------------------------------------------------
    # skip_launcher / update_check apply to BOTH the MGSHDFix games and MGS1
    # (MGSM2Fix), so they're offered whenever any game is selected — an
    # MGS1-only install must not silently inherit the defaults with no say.
    hdfix_sel = [k for k in found if GAMES[k].get("kind", "hdfix") == "hdfix"]
    m2fix_sel = [k for k in found if GAMES[k].get("kind") == "m2fix"]
    device = detect_device()
    opts = {
        "device": device,
        "button_icons": "Steam Deck", "audio_mode": "Stereo (2.0)",
        "hq_movies": True, "skip_splash": True,
        "update_check": False, "skip_launcher": True,
    }
    # Defaults are the recommended answers for every one of these, so they are
    # NOT asked up front any more — the summary screen lists them and offers a
    # "Change settings" branch for anyone who wants something else.
    if device != "steam_deck":
        opts["button_icons"] = "Xbox One"
    # A previous run's choices win over the generic defaults, so someone who
    # picked 5.1 sound or PS2 buttons doesn't have to set them again.
    defaults = dict(opts)
    try:
        per_game, choice_inputs = {}, {}
        for key, (game_dir, sroot) in found.items():
            with GameLock(game_dir):
                if (game_dir / MODKIT_DIRNAME / JOURNAL_NAME).exists():
                    notes, ok = recover_interrupted(game_dir, log)
                    if not ok:
                        raise RuntimeError("Recovery incomplete; backups kept. " + "; ".join(notes))
                before = _plan_inputs(game_dir, sroot)
                per_game[key] = options_for_game(key, found[key], defaults, log)
                choice_inputs[key] = _plan_inputs(game_dir, sroot)
                if before != choice_inputs[key]:
                    raise ReplanRequired("Inputs changed while reading settings; restart planning")
    except (OSError, RuntimeError, configparser.Error) as e:
        ui.error(f"Existing settings could not be read safely: {e}.\n"
                 "Keep your settings file. Correct it with the pinned Config Tool before repairing.")
        return 1
    if len(found) == 1:
        opts.update(per_game[next(iter(found))])
    opts["_changed"] = set()
    notice = kit_update_notice(log)

    # 4. Better Audio Mod — one checklist, then explicit per-archive picking.
    audio_archives = collect_audio_archives(ui, hdfix_sel)

    # 5. One review screen. Settings are shown, not asked — "Change settings"
    #    is there for anyone who wants something other than the recommendation.
    while True:
        try:
            review_plan = build_install_plan(found, per_game, audio_archives, choice_inputs)
        except (ValueError, RuntimeError, OSError) as e:
            ui.error(f"Installation plan is invalid: {e}")
            return 1
        plan = []
        for key in found:
            g, (d, _) = GAMES[key], found[key]
            if g.get("kind", "hdfix") == "m2fix":
                bits = ["MGSM2Fix"]
            else:
                bits = ["MGSHDFix", "Community Bugfix pack", "tuned settings"]
                if key in audio_archives:
                    bits.insert(1, "Better Audio (" + ", ".join(
                        c["short"] for c in audio_archives[key]) + ")")
            plan.append(f"• {g['short']}:  {' + '.join(bits)}")

        target_dir = next(iter(found.values()))[0]
        settings = []
        for key in found:
            game_opts = per_game[key]
            settings.append(f"{GAMES[key]['short']}: Boot straight in: "
                            f"{'yes' if game_opts['skip_launcher'] else 'no'}")
            if key in hdfix_sel:
                settings.append(f"  Buttons: {game_opts['button_icons']} · Sound: {game_opts['audio_mode']} · "
                                f"HQ movies: {'on' if game_opts['hq_movies'] else 'off'} · "
                                f"Skip logos: {'yes' if game_opts['skip_splash'] else 'no'}")
        settings.append("Recommended defaults will replace custom settings." if any(
            o.get("_reset") for o in per_game.values()) else
            "Existing custom settings are preserved per game; reset is optional.")
        audio_block = audio_status_text(audio_archives)
        note = audio_recommendation_note(audio_archives)

        body = ((notice + "\n\n" if notice else "") + "Ready to go:\n\n" + "\n".join(plan) + "\n\n"
                + ("\n".join(settings) + "\n\n" if settings else "")
                + (audio_block + "\n\n" if audio_block
                   else ("Better Audio: not installing\n\n" if hdfix_sel else ""))
                + (note + "\n\n" if note else "")
                + f"Free space: {free_gb(target_dir):.0f} GB\n\n"
                + "Close the games and let any Steam downloads finish first.")

        choice = ui.menu("Ready to install", body,
                         [("go", "Install now"),
                          ("opts", "Change settings…"),
                          ("reset", "Reset to recommended settings"),
                          ("cancel", "Cancel")])
        if choice in (None, "cancel"):
            return 0
        if choice == "go":
            try:
                CurrentRecipeAdapter(log).recheck(review_plan)
                confirmed_plan = review_plan
            except (ValueError, RuntimeError, OSError) as e:
                ui.error(f"Installation plan is invalid: {e}")
                return 1
            break
        if choice == "reset":
            opts.update(defaults)
            for key in per_game:
                per_game[key].update(defaults)
                per_game[key]["_reset"] = True
        else:
            ask_options(ui, opts, hdfix_sel, m2fix_sel)
            for game_opts in per_game.values():
                for option in opts["_changed"]:
                    game_opts[option] = opts[option]
                game_opts["_changed"] = set(opts["_changed"])

    # Each game commits independently. Cancellation/failure keeps earlier successes.
    prog = ui.progress("Installing MGS mods", log)
    outcomes = {key: "not started" for key in found}
    global CANCEL_EVENT, TRANSFER_PROGRESS
    previous_cancel, previous_transfer = CANCEL_EVENT, TRANSFER_PROGRESS
    CANCEL_EVENT = getattr(prog, "cancel_event", threading.Event())

    def install_selected():
        global TRANSFER_PROGRESS

        def transfer(name, received, size):
            detail = f"{received / 1024**2:.1f} MB"
            if size:
                detail += f" / {size / 1024**2:.1f} MB"
            prog.update(f"Preparing — downloading {name}: {detail}", 0)

        TRANSFER_PROGRESS = transfer
        with tempfile.TemporaryDirectory(prefix="mgskit_plan_") as td:
            adapter = CurrentRecipeAdapter(log, prog)
            prepared = prepare_plan(confirmed_plan, adapter, Path(td))
            execute_plan(prepared, adapter, outcomes)

    try:
        run_with_progress(prog, install_selected)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, configparser.Error, KeyboardInterrupt) as e:
        log(traceback.format_exc())
        prog.close()
        label = "Installation cancelled" if isinstance(e, (CancelledInstall, KeyboardInterrupt)) else "Installation stopped"
        summary = "\n".join(f"{GAMES[k]['short']}: {outcomes[k]}" for k in found)
        ui.error(f"{label}: {e}\n\n{summary}\n\n" +
                 (f"Diagnostic log: {log_path}" if log_path else "Diagnostic log could not be saved."))
        return 1
    finally:
        CANCEL_EVENT, TRANSFER_PROGRESS = previous_cancel, previous_transfer
        prog.close()

    # 8. Final manual steps -------------------------------------------------
    names = ", ".join(GAMES[k]["short"] for k in found)

    tips = []
    if hdfix_sel:
        for key in hdfix_sel:
            game_opts = per_game[key]
            tips.append(f"• {GAMES[key]['short']}: " +
                        ("boots straight in" if game_opts["skip_launcher"] else "launcher appears; press Play") +
                        f"; high-quality cinematics {'on' if game_opts['hq_movies'] else 'off'}.")
        if not IS_WINDOWS:
            tips.append("• Playing on a TV and it looks soft? In Steam set Properties → Game Resolution to Native.")
    if any(GAMES[k].get("kind") == "m2fix" for k in found):
        tips.append("• MGS1 asks which version to play the first time: choose "
                    "METAL GEAR SOLID (US), Max resolution, 4:3.")
    keep_note = ("\n\nKeep the shortcut — run it again any time to repair the "
                 "mods, add the audio packs, or remove everything.")

    if IS_WINDOWS:
        # On Windows the mods load natively — there is genuinely nothing left
        # to do. No launch options, no reference file, no clipboard step.
        ui.info(
            f"✅ All done — {names} is modded and checked.\n\n"
            "Installed files verified; game boots are not checked by this installer.\n\n"
            "Nothing else to set up: just launch the games from Steam.\n\n"
            + "\n".join(tips) + keep_note)
        return 0

    # Linux/Steam Deck: Proton needs per-game launch options, and Steam
    # reverts config edits made while it runs — so this one step stays manual.
    lo_lines = [f"   {GAMES[key]['short']}:  {launch_option_for(key)}"
                for key in ("mgs1", "mgs2", "mgs3") if key in found]
    # Always write the reference file — it's tiny, it's the one step we can't
    # do for the user, and the old "save it? (recommended: yes)" prompt was a
    # question whose answer was never in doubt.
    saved_path = save_launch_options_file(ui, list(found.keys()), log)
    saved_note = (f"They're also saved in “{saved_path.name}” on your Desktop.\n"
                  if saved_path else "")

    ui.info(
        f"✅ All done — {names} is modded and checked.\n\n"
        "Installed files verified; game boots are not checked by this installer.\n\n"
        "ONE thing left, which only you can do in Steam:\n"
        "right-click each game → Properties → Launch Options, and paste its "
        "line.\n\n"
        + "\n".join(lo_lines) + "\n\n"
        + saved_note
        + "\n".join(tips) + keep_note
    )
    offer_clipboard_copy(ui, list(found.keys()))
    return 0


def main() -> int:
    path, stream = start_session_log()
    lock = threading.Lock()

    def log(message):
        with lock:
            print(message)
            if stream:
                try:
                    stream.write(str(message) + "\n")
                    stream.flush()
                except OSError:
                    pass

    log(f"MGS Mod Kit {MODKIT_VERSION}; platform={sys.platform}; Python={sys.version.split()[0]}")
    if path:
        log(f"Diagnostic log: {path}")
    try:
        return _main(log, path)
    except Exception:
        log(traceback.format_exc())
        raise
    finally:
        if stream:
            stream.close()


def ask_options(ui: UI, opts: dict, hdfix_sel, m2fix_sel) -> None:
    """The 'Change settings' branch — only reached if the user asks for it.

    Every option here already defaults to the recommended answer, which is why
    it is not on the main path.
    """
    opts.setdefault("_changed", set())
    if hdfix_sel:
        icon_items = [
            ("Steam Deck", "Steam Deck buttons"),
            ("Xbox One", "Xbox buttons"),
            ("PlayStation 5", "PlayStation 5 buttons"),
            ("PlayStation 2", "PlayStation 2 buttons (as the originals had)"),
            ("Keyboard / Mouse", "Keyboard and mouse"),
        ]
        if opts.get("device") != "steam_deck":
            icon_items.insert(0, icon_items.pop(1))    # Xbox first
        picked = ui.menu(
            "Button prompts",
            "Which controller buttons should the games show?",
            icon_items)
        if picked:
            opts["button_icons"] = picked
            opts["_changed"].add("button_icons")

        picked = ui.menu(
            "Sound",
            "How are you listening?",
            [("Stereo (2.0)", "Headphones, the Deck, or a TV (best for most)"),
             ("Surround Sound (5.1)", "A real 5.1 surround speaker setup")],
        )
        if picked:
            opts["audio_mode"] = picked
            opts["_changed"].add("audio_mode")

    extra_items: list[tuple[str, str, bool]] = []
    if hdfix_sel:
        extra_items += [
            ("hq_movies", "High-quality cutscenes", opts["hq_movies"]),
            ("skip_splash", "Skip the KONAMI intro logos", opts["skip_splash"]),
        ]
    if hdfix_sel or m2fix_sel:
        extra_items.append(
            ("skip_launcher", "Boot straight into the games",
             opts["skip_launcher"]))
    # NOTE: there is deliberately no "check for mod updates" option. The mod
    # versions here are pinned to match the settings file this kit writes, so a
    # mod updating itself can rename a settings key and make the game refuse to
    # start (MGSHDFix hard-aborts on an unknown key). Updates reach users via
    # new releases of this kit instead. See the pinned-version note up top.
    if extra_items:
        extras = ui.checklist("Extras", "Tick what you want:", extra_items)
        # Cancel keeps the current values rather than reading as "all off".
        if extras is not None:
            for tag, _, _ in extra_items:
                opts[tag] = tag in extras
                opts["_changed"].add(tag)


def offer_clipboard_copy(ui: UI, found_keys) -> None:
    """Let the user copy each game's launch-option line, ready to paste.

    Skipped silently when the clipboard isn't reachable (non-KDE session, no
    klipper), because the .txt file and the dialog already carry the text.
    """
    keys = [k for k in ("mgs1", "mgs2", "mgs3") if k in found_keys]
    if not keys or ui.kind == "term" or not find_qdbus():
        return
    while True:
        items = [(k, f"Copy the {GAMES[k]['short']} line") for k in keys]
        items.append(("done", "Nothing else, thanks"))
        choice = ui.menu(
            "Copy launch options",
            "Copy a line here, then paste it into Steam with Ctrl+V.",
            items)
        if choice in (None, "done"):
            return
        if choice in GAMES:
            if copy_to_clipboard(launch_option_for(choice)):
                ui.info(f"Copied the {GAMES[choice]['short']} line.\n\n"
                        "In Steam: right-click the game → Properties → "
                        "Launch Options → Ctrl+V.")
            else:
                ui.info("Couldn't reach the clipboard on this system — copy "
                        "the line from the text file on your Desktop instead.")
                return


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)
