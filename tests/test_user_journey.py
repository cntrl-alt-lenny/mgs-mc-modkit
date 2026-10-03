"""The full user journey, end to end, through the REAL main().

This is the 'imagine you're a user' review made executable: every dialog the
user would see is scripted in order, and if the flow ever shows one more (or
one fewer) screen than expected, the scripted queues under/overflow and the
test fails. Covers: fresh install of MGS1+MGS2 → re-run offering repair →
uninstall back to stock.
"""
from __future__ import annotations

import sys
import json
import threading

import pytest

from test_progress import BrokenZenity

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
    assert logs[1]["button_icons"] == "PlayStation 2"
    assert logs[1]["audio_mode"] == "Surround Sound (5.1)"


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


@pytest.mark.parametrize("change_before_reset", [False, True])
def test_reset_then_choices_match_review_manifest_and_files(
        tmp_path, monkeypatch, patch_download, change_before_reset):
    g1, g2, _ = _fake_world(tmp_path, monkeypatch, patch_download)
    g3 = g2.parent / "MGS3"
    g3.mkdir()
    (g3 / "METAL GEAR SOLID3.exe").write_bytes(b"exe")
    root = tmp_path / "steam"
    found = {"mgs1": (g1, root), "mgs2": (g2, root), "mgs3": (g3, root)}
    monkeypatch.setattr(install, "find_games", lambda: dict(found))

    class ReviewUI(FakeUI):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.reviews = []

        def menu(self, title, body, items):
            if title == "Ready to install":
                self.reviews.append(body)
            return super().menu(title, body, items)

    # Start with an actual installation so reset must discard custom values.
    ui = ReviewUI(checklist=[list(found), [], []],
                  menu=["opts", "Xbox One", "Stereo (2.0)", "go"])
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 0
    for game_dir in (g2, g3):
        path = game_dir / "plugins/MGSHDFix.settings"
        path.write_text(path.read_text().replace('Game Language="en"', 'Game Language="fr"'))
        assert 'Game Language="fr"' in path.read_text()
    ini = g1 / "MGSM2Fix.ini"
    ini.write_text(ini.read_text().replace("SkipIntro = true", "SkipIntro = false"))

    # Also exercise Change -> Reset -> Change: only post-reset choices win.
    menus = ["install"]
    checklists = [list(found), []]
    if change_before_reset:
        menus += ["opts", "PlayStation 5", "Stereo (2.0)"]
        checklists += [["hq_movies", "skip_splash", "skip_launcher"]]
    menus += ["reset", "opts", "PlayStation 2", "Surround Sound (5.1)", "go"]
    checklists += [[]]  # explicitly turn off HQ movies, logos skip and auto-boot
    ui = ReviewUI(checklist=checklists, menu=menus)
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 0
    assert not ui.errors and not ui._menu and not ui._checklist
    review = ui.reviews[-1]
    for key, game_dir in (("mgs1", g1), ("mgs2", g2), ("mgs3", g3)):
        saved = json.loads((game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())["settings"]
        assert saved["skip_launcher"] is False
        assert f"{install.GAMES[key]['short']}: Boot straight in: no" in review
        if key == "mgs1":
            parser = install.parse_ini(ini.read_text())
            assert parser["Main"]["StartGame"] == "false"
            assert parser["Main"]["SkipIntro"] == "true"  # shipped reset default
        else:
            assert saved["button_icons"] == "PlayStation 2"
            assert saved["audio_mode"] == "Surround Sound (5.1)"
            assert saved["hq_movies"] is False and saved["skip_splash"] is False
            parser = install.validate_settings((game_dir / "plugins/MGSHDFix.settings").read_text())
            assert parser["Controller Settings"]["Button Icons"] == '"PlayStation 2"'
            assert parser["System Specific Fixes"]["Audio Output Mode"] == '"Surround Sound (5.1)"'
            assert parser["Launcher and Splashscreens"]["Skip Launcher"] == "0"
            assert parser["Launcher and Splashscreens"]["Skip In-Game Splashscreens"] == "0"
            assert parser["Launcher and Splashscreens"]["Skip Launcher Splashscreens"] == "0"
            assert parser["Language Settings"]["Game Language"] == '"en"'
            saves = list(game_dir.glob("*_savedata_win/*/launcher/launcher_sv"))
            assert len(saves) == 1
            assert install._read_launcher_sv(saves[0])["HiresoMovie"] == "0"
    assert review.count("Buttons: PlayStation 2 · Sound: Surround Sound (5.1) · HQ movies: off · Skip logos: no") == 2


def test_zenity_queued_cancel_restores_install_and_reports_cancellation(
        tmp_path, monkeypatch, patch_download):
    _, game_dir, _ = _fake_world(tmp_path, monkeypatch, patch_download)
    root = tmp_path / "steam"
    monkeypatch.setattr(install, "find_games", lambda: {"mgs2": (game_dir, root)})
    before = {p.relative_to(game_dir): p.read_bytes() for p in game_dir.rglob("*") if p.is_file()}
    ready = threading.Event()
    real_install_hdfix = install.install_hdfix

    def install_then_wait(tx, tmp, log):
        real_install_hdfix(tx, tmp, log)
        assert (game_dir / "winhttp.dll").read_bytes() != before[install.Path("winhttp.dll")]
        ready.set()
        assert install.CANCEL_EVENT.wait(5), "UI pump did not detect Zenity cancellation"
        install.check_cancelled()

    monkeypatch.setattr(install, "install_hdfix", install_then_wait)

    class CancelUI(FakeUI):
        def progress(self, title, log):
            class CancelProgress(install.Progress):
                def pump(self):
                    if not ready.is_set():
                        return
                    if not getattr(self, "cancel_injected", False):
                        self.cancel_injected = True
                        self._backend = "zenity"
                        self._proc = BrokenZenity(1)
                        assert not self._pending.empty()
                    super().pump()
            return CancelProgress("term", title, log)

    ui = CancelUI(checklist=[["mgs2"], []], menu=["go"])
    monkeypatch.setattr(install, "UI", lambda: ui)
    assert install.main() == 1
    assert "Installation cancelled" in str(ui.errors)
    assert "previous setup restored" in str(ui.errors)
    assert not ui.infos
    after = {p.relative_to(game_dir): p.read_bytes() for p in game_dir.rglob("*") if p.is_file()}
    assert after == before
