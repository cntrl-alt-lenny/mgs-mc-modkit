"""Dialog cancellation semantics — the options-screen bug fix."""
from __future__ import annotations

import builtins

import install

ITEMS = [
    ("hq_movies", "High-quality cinematics", True),
    ("skip_splash", "Skip logos", True),
    ("update_check", "Update checks", False),
]


def _term_ui(monkeypatch, answer: str):
    ui = install.UI()
    ui.kind = "term"
    monkeypatch.setattr(builtins, "input", lambda *a, **k: answer)
    return ui


def test_cancel_returns_none(monkeypatch):
    ui = _term_ui(monkeypatch, "c")
    assert ui.checklist("t", "x", ITEMS) is None


def test_blank_keeps_defaults(monkeypatch):
    ui = _term_ui(monkeypatch, "")
    result = ui.checklist("t", "x", ITEMS)
    assert set(result) == {"hq_movies", "skip_splash"}


def test_toggle_off_yields_empty_not_none(monkeypatch):
    # Toggle both defaults off -> a *deliberate* empty selection, not a cancel.
    ui = _term_ui(monkeypatch, "0 1")
    result = ui.checklist("t", "x", ITEMS)
    assert result == []
    assert result is not None


def test_cancel_preserves_opts_defaults(monkeypatch):
    """Regression: a cancelled extras dialog must NOT flip every option off."""
    opts = {"hq_movies": True, "skip_splash": True, "update_check": False,
            "skip_launcher": True}
    ui = _term_ui(monkeypatch, "c")
    extras = ui.checklist("t", "x", ITEMS)
    if extras is not None:                       # this branch must not run
        for tag, _, _ in ITEMS:
            opts[tag] = tag in extras
    assert opts["hq_movies"] is True
    assert opts["skip_launcher"] is True


# ---------------------------------------------------------------------------
# Tier 2 — settings persistence, no-display fallback, clipboard, filters
# ---------------------------------------------------------------------------
import json
from pathlib import Path


def test_no_display_falls_back_to_terminal(monkeypatch):
    """SSH into a Deck: dialogs would be invisible and yesno would read 'No'."""
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setattr(install.shutil, "which", lambda n: f"/usr/bin/{n}")
    assert install.UI().kind == "term"


def test_display_present_uses_kdialog(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(install.shutil, "which",
                        lambda n: "/usr/bin/kdialog" if n == "kdialog" else None)
    assert install.UI().kind == "kdialog"


def test_saved_settings_round_trip(tmp_path):
    game = tmp_path / "MGS2"
    (game / install.MODKIT_DIRNAME).mkdir(parents=True)
    (game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).write_text(json.dumps({
        "installed_utc": "2026-07-25T10:00:00+00:00",
        "settings": {"button_icons": "PlayStation 2",
                     "audio_mode": "Surround Sound (5.1)",
                     "skip_splash": False},
    }))
    saved = install.load_saved_opts({"mgs2": (game, tmp_path)})
    assert saved["button_icons"] == "PlayStation 2"
    assert saved["audio_mode"] == "Surround Sound (5.1)"
    assert saved["skip_splash"] is False


def test_saved_settings_ignores_unknown_and_bad_values(tmp_path):
    game = tmp_path / "MGS2"
    (game / install.MODKIT_DIRNAME).mkdir(parents=True)
    (game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).write_text(json.dumps({
        "settings": {"button_icons": "Xbox One", "evil_key": "rm -rf",
                     "audio_mode": {"nested": "junk"}},
    }))
    saved = install.load_saved_opts({"mgs2": (game, tmp_path)})
    assert saved == {"button_icons": "Xbox One"}     # unknown/non-scalar dropped


def test_saved_settings_absent_or_corrupt_is_empty(tmp_path):
    game = tmp_path / "MGS2"
    (game / install.MODKIT_DIRNAME).mkdir(parents=True)
    assert install.load_saved_opts({"mgs2": (game, tmp_path)}) == {}
    (game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).write_text("{oops")
    assert install.load_saved_opts({"mgs2": (game, tmp_path)}) == {}


def test_options_branch_only_when_asked(monkeypatch):
    """Defaults are shown, not asked: ask_options runs only on request."""
    from conftest import FakeUI
    opts = {"device": "steam_deck", "button_icons": "Steam Deck",
            "audio_mode": "Stereo (2.0)", "hq_movies": True,
            "skip_splash": True, "skip_launcher": True, "update_check": False}
    ui = FakeUI(menu=["PlayStation 2", "Surround Sound (5.1)"],
                checklist=[["hq_movies"]])
    install.ask_options(ui, opts, ["mgs2"], [])
    assert opts["button_icons"] == "PlayStation 2"
    assert opts["audio_mode"] == "Surround Sound (5.1)"
    assert opts["hq_movies"] is True
    assert opts["skip_splash"] is False              # deliberately unticked


def test_options_cancel_keeps_current_values():
    from conftest import FakeUI
    opts = {"device": "steam_deck", "button_icons": "Steam Deck",
            "audio_mode": "Stereo (2.0)", "hq_movies": True,
            "skip_splash": True, "skip_launcher": True, "update_check": False}
    ui = FakeUI(menu=[None, None], checklist=[None])   # cancel everything
    install.ask_options(ui, opts, ["mgs2"], [])
    assert opts["button_icons"] == "Steam Deck"
    assert opts["hq_movies"] is True and opts["skip_splash"] is True


def test_update_check_is_not_offered_and_stays_off():
    """Removed on purpose: turning it on can stop the games launching, because
    the pinned mod versions are matched to the settings file this kit writes."""
    from conftest import FakeUI
    opts = {"device": "steam_deck", "button_icons": "Steam Deck",
            "audio_mode": "Stereo (2.0)", "hq_movies": True,
            "skip_splash": True, "skip_launcher": True, "update_check": False}
    seen = {}

    class Rec(FakeUI):
        def checklist(self, title, text, items):
            seen["tags"] = [t for t, _, _ in items]
            return None
    install.ask_options(Rec(menu=[None, None]), opts, ["mgs2"], [])
    assert "update_check" not in seen["tags"]
    assert opts["update_check"] is False


def test_saved_settings_cannot_re_enable_update_check(tmp_path):
    """An older manifest (or a hand-edit) must not turn it back on."""
    game = tmp_path / "MGS2"
    (game / install.MODKIT_DIRNAME).mkdir(parents=True)
    (game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).write_text(json.dumps({
        "settings": {"update_check": True, "button_icons": "Xbox One"},
    }))
    saved = install.load_saved_opts({"mgs2": (game, tmp_path)})
    assert "update_check" not in saved
    assert saved["button_icons"] == "Xbox One"


def test_clipboard_uses_klipper_dbus(monkeypatch):
    calls = []

    class R:
        returncode = 0
    monkeypatch.setattr(install.shutil, "which",
                        lambda n: "/usr/bin/qdbus6" if n == "qdbus6" else None)
    monkeypatch.setattr(install.subprocess, "run",
                        lambda a, **k: calls.append(a) or R())
    assert install.copy_to_clipboard("WINEDLLOVERRIDES=x %command%") is True
    assert "org.kde.klipper" in calls[0]
    assert "org.kde.klipper.klipper.setClipboardContents" in calls[0]
    assert "WINEDLLOVERRIDES=x %command%" in calls[0]


def test_clipboard_degrades_without_qdbus(monkeypatch):
    monkeypatch.setattr(install.shutil, "which", lambda n: None)
    assert install.copy_to_clipboard("x") is False


def test_file_filter_uses_described_form(monkeypatch):
    """KF5 kdialog ignored bare globs (KDE bug 467868)."""
    captured = {}
    ui = install.UI.__new__(install.UI)
    ui.kind = "kdialog"
    ui.last_dir = Path("/tmp")
    monkeypatch.setattr(ui, "_run",
                        lambda args: (captured.setdefault("a", args), (0, "/x.zip"))[1])
    ui.pick_file("pick", start=Path("/tmp"))
    assert any("Mod archives (*.zip *.7z *.rar)" in a for a in captured["a"])


def test_detailed_error_used_when_details_given(monkeypatch):
    captured = {}
    ui = install.UI.__new__(install.UI)
    ui.kind = "kdialog"
    monkeypatch.setattr(ui, "_run",
                        lambda args: (captured.setdefault("a", args), (0, ""))[1])
    ui.error("Short headline", details="long technical detail")
    assert "--detailederror" in captured["a"]
