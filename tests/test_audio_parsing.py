"""NexusMods filename parsing + settings-template integrity."""
from __future__ import annotations

from pathlib import Path

import install


def test_audio_version_and_modid():
    main = Path("MGS3 Better Audio Mod-4-1-0-1700000000.zip")
    assert install.audio_modid(main) == 4
    assert install.audio_version(main) == (1, 0)

    update = Path("Update 2.0-4-2-0-1700000001.zip")   # generic name, right mod
    assert install.audio_modid(update) == 4
    assert install.audio_version(update) == (2, 0)


def test_audio_parsing_ignores_non_nexus_names():
    p = Path("some-random-file.zip")
    assert install.audio_modid(p) is None
    assert install.audio_version(p) is None


def test_settings_template_counts_match_constants():
    import re
    body = install.SETTINGS_TEMPLATE
    sections = len(re.findall(r"^\[", body, re.M))
    keys = len(re.findall(r"^[^\[\r\n][^\r\n]*=", body, re.M))
    assert sections == install.SETTINGS_EXPECTED_SECTIONS
    assert keys == install.SETTINGS_EXPECTED_KEYS


def test_write_settings_produces_crlf_and_region(tmp_path):
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    tx = install.InstallTxn(game_dir, "mgs3", lambda m: None)
    opts = {
        "button_icons": "Steam Deck", "audio_mode": "Stereo (2.0)",
        "skip_launcher": True, "skip_splash": True, "update_check": False,
    }
    install.write_settings(tx, install.GAMES["mgs3"], opts, lambda m: None)
    raw = (game_dir / "plugins" / "MGSHDFix.settings").read_bytes()
    assert b"\r\n" in raw
    assert b'Game Region="us"' in raw
    assert b"@" not in raw          # every placeholder substituted


# ---------------------------------------------------------------------------
# The settings template is COUPLED to a specific MGSHDFix release.
# ---------------------------------------------------------------------------
def test_settings_template_matches_the_pinned_mgshdfix():
    """MGSHDFix hard-aborts on a missing key, and its schema changes between
    major releases (4.0.2 renamed 9 sections and added 10). So the template
    must match the Config Tool schema of the version we pin.

    If this fails after a version bump, the settings file needs regenerating —
    see docs/UPGRADING.md. Do NOT just edit the constant.
    """
    assert install.SETTINGS_CAPTURED_FROM == install.HDFIX_VERSION, (
        f"SETTINGS_TEMPLATE is for MGSHDFix "
        f"{install.SETTINGS_CAPTURED_FROM}, but this kit now installs "
        f"{install.HDFIX_VERSION}. Regenerate it with "
        f"{install.HDFIX_VERSION}'s Config Tool before releasing.")
