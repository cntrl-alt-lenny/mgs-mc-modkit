"""Steam library discovery and hardware detection."""
from __future__ import annotations

from pathlib import Path

import install


def _make_game(lib: Path, key: str):
    g = install.GAMES[key]
    d = lib / "steamapps" / "common" / g["dirname"]
    d.mkdir(parents=True)
    (d / g["exe"]).write_bytes(b"exe")
    return d


def test_library_paths_includes_secondary(tmp_path):
    root = tmp_path / "steam"
    (root / "steamapps").mkdir(parents=True)
    sd = tmp_path / "microsd"
    sd.mkdir()
    (root / "steamapps" / "libraryfolders.vdf").write_text(
        '"libraryfolders"\n{\n'
        '  "0" { "path" "%s" }\n'
        '  "1" { "path" "%s" }\n}\n' % (root, sd))

    libs = install.library_paths(root)
    assert root in libs
    assert sd in libs


def test_find_games_across_libraries(tmp_path, monkeypatch):
    root = tmp_path / "steam"
    (root / "steamapps").mkdir(parents=True)
    sd = tmp_path / "microsd"
    (sd / "steamapps").mkdir(parents=True)
    (root / "steamapps" / "libraryfolders.vdf").write_text(
        '"libraryfolders"\n{\n  "1" { "path" "%s" }\n}\n' % sd)

    _make_game(root, "mgs2")     # internal
    _make_game(sd, "mgs3")       # microSD

    monkeypatch.setattr(install, "steam_roots", lambda: [root])
    found = install.find_games()
    assert set(found) == {"mgs2", "mgs3"}
    assert found["mgs2"][0].name == "MGS2"
    assert found["mgs3"][0].name == "MGS3"


def test_detect_device_env(monkeypatch):
    assert install.detect_device(env={"SteamDeck": "1"}) == "steam_deck"
    monkeypatch.setattr(install, "IS_WINDOWS", False)
    assert install.detect_device(env={}, dmi_bases=()) == "generic_linux"


def test_detect_device_windows(monkeypatch):
    monkeypatch.setattr(install, "IS_WINDOWS", True)
    assert install.detect_device(env={}, dmi_bases=()) == "windows"
    # The env override still wins (a Deck is a Deck).
    assert install.detect_device(env={"SteamDeck": "1"}) == "steam_deck"


def test_detect_device_dmi(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "IS_WINDOWS", False)
    base = tmp_path / "dmi"
    base.mkdir()
    (base / "sys_vendor").write_text("Valve\n")
    (base / "product_name").write_text("Galileo\n")
    assert install.detect_device(env={}, dmi_bases=(str(base),)) == "steam_deck"

    (base / "sys_vendor").write_text("Dell Inc.\n")
    (base / "product_name").write_text("XPS 13\n")
    assert install.detect_device(env={}, dmi_bases=(str(base),)) == "generic_linux"
