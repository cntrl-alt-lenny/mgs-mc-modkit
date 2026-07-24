"""Launch-options reference text + file saving."""
from __future__ import annotations

from pathlib import Path

import install
from conftest import FakeUI


def test_text_only_installed_games_correct_commands():
    text = install.build_launch_options_text(["mgs1", "mgs3"])
    assert "MGS1" in text and "MGS3" in text
    assert "MGS2" not in text                       # not installed this run
    assert 'dinput8=n,b;d3d11=n,b' in text          # MGS1 command
    assert '"wininet,winhttp=n,b"' in text          # MGS3 command
    # MGS1 listed before MGS3 (stable game-number order).
    assert text.index("MGS1") < text.index("MGS3")


def test_text_mgs2_only():
    text = install.build_launch_options_text(["mgs2"])
    assert "MGS2" in text
    assert "MGS1" not in text and "MGS3" not in text
    assert '"wininet,winhttp=n,b"' in text
    assert "dinput8" not in text


def test_save_to_desktop(tmp_path, monkeypatch):
    desk = tmp_path / "Desktop"
    desk.mkdir()
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: desk)
    ui = FakeUI()
    path = install.save_launch_options_file(ui, ["mgs2", "mgs3"], lambda m: None)
    assert path == desk / "MGS Steam Launch Options.txt"
    assert "MGS2" in path.read_text() and "MGS3" in path.read_text()


def test_existing_file_not_clobbered_without_consent(tmp_path, monkeypatch):
    desk = tmp_path / "Desktop"
    desk.mkdir()
    existing = desk / "MGS Steam Launch Options.txt"
    existing.write_text("KEEP ME")
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: desk)
    # yesno=[False] -> decline overwrite -> timestamped filename used instead.
    ui = FakeUI(yesno=[False])
    path = install.save_launch_options_file(
        ui, ["mgs2"], lambda m: None, timestamp="20260724-120000")
    assert path == desk / "MGS Steam Launch Options 20260724-120000.txt"
    assert existing.read_text() == "KEEP ME"        # original untouched


def test_existing_file_overwrite_when_confirmed(tmp_path, monkeypatch):
    desk = tmp_path / "Desktop"
    desk.mkdir()
    existing = desk / "MGS Steam Launch Options.txt"
    existing.write_text("OLD")
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: desk)
    ui = FakeUI(yesno=[True])                       # confirm overwrite
    path = install.save_launch_options_file(ui, ["mgs2"], lambda m: None)
    assert path == existing
    assert "OLD" not in path.read_text()


def test_desktop_fallback_asks_for_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: None)
    target = tmp_path / "chosen"
    target.mkdir()
    ui = FakeUI(dirs=[str(target)])                 # user picks a folder
    path = install.save_launch_options_file(ui, ["mgs2"], lambda m: None)
    assert path == target / "MGS Steam Launch Options.txt"
    assert path.is_file()


def test_desktop_fallback_cancelled_returns_none(monkeypatch):
    monkeypatch.setattr(install, "resolve_desktop_dir", lambda: None)
    ui = FakeUI(dirs=[None])                         # user cancels the folder pick
    assert install.save_launch_options_file(ui, ["mgs2"], lambda m: None) is None


# -- progress window (term fallback is the tested path) ---------------------
def test_progress_term_fallback_never_raises():
    logs = []
    p = install.Progress("term", "Installing", logs.append)
    p.update("Preparing", 5)
    p.update("Extracting", 40)
    p.update("Verifying", 95)
    p.update("Complete", 100)
    p.close()
    p.close()                                       # idempotent
    assert any("Preparing" in m for m in logs)
    assert any("100%" in m for m in logs)


def test_progress_clamps_percent():
    logs = []
    p = install.Progress("term", "x", logs.append)
    p.update("a", -20)
    p.update("b", 250)
    assert any("(0%)" in m for m in logs)
    assert any("(100%)" in m for m in logs)
