"""The full user journey, end to end, through the REAL main().

This is the 'imagine you're a user' review made executable: every dialog the
user would see is scripted in order, and if the flow ever shows one more (or
one fewer) screen than expected, the scripted queues under/overflow and the
test fails. Covers: fresh install of MGS1+MGS2 → re-run offering repair →
uninstall back to stock.
"""
from __future__ import annotations

import sys
from pathlib import Path

import install
from conftest import FakeUI, make_steam_root


def _fake_world(tmp_path, monkeypatch, patch_download):
    """A machine with MGS1 + MGS2 installed and a Desktop, nothing modded."""
    g1 = tmp_path / "lib" / "steamapps" / "common" / "MGS1"
    g2 = tmp_path / "lib" / "steamapps" / "common" / "MGS2"
    for g, exe in ((g1, "METAL GEAR SOLID.exe"), (g2, "METAL GEAR SOLID2.exe")):
        g.mkdir(parents=True)
        (g / exe).write_bytes(b"exe")
    (g2 / "winhttp.dll").write_bytes(b"TRUE-STOCK")     # a real file to overwrite
    root = make_steam_root(tmp_path)
    desk = tmp_path / "Desktop"
    desk.mkdir()

    found = {"mgs1": (g1, root), "mgs2": (g2, root)}
    monkeypatch.setattr(install, "find_games", lambda: dict(found))
    monkeypatch.setattr(install, "detect_device", lambda *a, **k: "steam_deck")
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: desk)
    monkeypatch.setattr(install, "apply_branding", lambda log: None)
    monkeypatch.setattr(install, "IS_WINDOWS", False)
    monkeypatch.setattr(sys, "argv", ["install.py"])
    return g1, g2, desk


def test_full_journey_install_rerun_uninstall(tmp_path, monkeypatch,
                                              patch_download, capsys):
    g1, g2, desk = _fake_world(tmp_path, monkeypatch, patch_download)

    # ---- Day 1: fresh install. The user should see exactly:
    #   1. games checklist  2. audio checklist  3. review menu  4. done info
    ui = FakeUI(checklist=[["mgs1", "mgs2"],     # both games, pre-ticked
                           []],                  # deliberately skip audio
                menu=["go"])                     # review screen -> Install now
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 0

    # queues fully consumed: not one dialog more or fewer than promised
    assert ui._checklist == [] and ui._menu == [] and ui._yesno == []
    assert not ui.errors

    # both games really modded
    assert install.verify_install(install.GAMES["mgs1"], g1) == []
    assert install.verify_install(install.GAMES["mgs2"], g2) == []
    assert (g2 / install.MODKIT_DIRNAME / install.MANIFEST_NAME).is_file()

    # the one manual step is written down, for exactly the installed games
    txt = (desk / "MGS Steam Launch Options.txt").read_text()
    assert "MGS1" in txt and "MGS2" in txt and "MGS3" not in txt
    assert 'dinput8=n,b;d3d11=n,b' in txt         # MGS1's line
    assert '"wininet,winhttp=n,b"' in txt         # MGS2's line

    # ...and the done screen says so too
    done = str(ui.infos[-1])
    assert "ONE thing left" in done
    assert "Keep the shortcut" in done

    # ---- Day 30: run it again. Now a mode menu appears first.
    ui2 = FakeUI(menu=["uninstall"],              # what would you like to do?
                 checklist=[["mgs1", "mgs2"]],    # remove from both
                 yesno=[True])                    # confirm removal
    monkeypatch.setattr(install, "UI", lambda: ui2)
    assert install.main() == 0
    assert ui2._menu == [] and ui2._checklist == [] and ui2._yesno == []
    assert not ui2.errors

    # back to stock: originals restored, mod files and records gone
    assert (g2 / "winhttp.dll").read_bytes() == b"TRUE-STOCK"
    assert not (g2 / "plugins").exists()
    assert not (g1 / "MGSM2Fix64.asi").exists()
    assert not (g1 / install.MODKIT_DIRNAME).exists()
    assert not (g2 / install.MODKIT_DIRNAME).exists()
    assert (g1 / "METAL GEAR SOLID.exe").exists()  # the games themselves: untouched
    assert (g2 / "METAL GEAR SOLID2.exe").exists()


def test_journey_settings_survive_to_the_second_run(tmp_path, monkeypatch,
                                                    patch_download):
    g1, g2, desk = _fake_world(tmp_path, monkeypatch, patch_download)

    # First run: open Change settings and pick PS2 buttons + 5.1.
    ui = FakeUI(checklist=[["mgs1", "mgs2"], [],           # games, no audio
                           ["hq_movies", "skip_splash", "skip_launcher"]],
                menu=["opts",                              # Change settings…
                      "PlayStation 2", "Surround Sound (5.1)",
                      "go"])                               # back to review -> go
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 0
    assert ui._menu == [] and ui._checklist == []

    # Second run (repair): the saved choices come back without being asked.
    logs = []
    real_txn = install.InstallTxn

    class SpyTxn(real_txn):
        def commit(self):
            logs.append(dict(self.settings))
            super().commit()
    monkeypatch.setattr(install, "InstallTxn", SpyTxn)
    ui2 = FakeUI(menu=["install", "go"],          # mode menu, then review
                 checklist=[["mgs1", "mgs2"], []])
    monkeypatch.setattr(install, "UI", lambda: ui2)
    assert install.main() == 0
    assert all(s.get("button_icons") == "PlayStation 2" for s in logs)
    assert all(s.get("audio_mode") == "Surround Sound (5.1)" for s in logs)


def test_journey_windows_needs_no_manual_step(tmp_path, monkeypatch,
                                              patch_download):
    """The Windows promise: after install there is genuinely nothing to do."""
    g1, g2, desk = _fake_world(tmp_path, monkeypatch, patch_download)
    monkeypatch.setattr(install, "IS_WINDOWS", True)

    ui = FakeUI(checklist=[["mgs1", "mgs2"], []], menu=["go"])
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 0
    assert not ui.errors

    done = str(ui.infos[-1])
    assert "Nothing else to set up" in done
    assert "Launch Options" not in done            # never mentioned on Windows
    # ...and no launch-options file is dropped on the Desktop either
    assert not (desk / "MGS Steam Launch Options.txt").exists()
