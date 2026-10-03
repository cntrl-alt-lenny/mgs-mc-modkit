"""Independent upstream schema, manual edits, reset and per-game preferences."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import install
from test_transaction import DEFAULT_OPTS


def settings(tmp_path, opts=None):
    game = tmp_path / "game"
    game.mkdir(exist_ok=True)
    tx = install.InstallTxn(game, "mgs2", lambda m: None)
    install.write_settings(tx, install.GAMES["mgs2"], opts or DEFAULT_OPTS, lambda m: None)
    text = (game / "plugins/MGSHDFix.settings").read_text()
    tx.commit()
    return game, text


def test_schema_comes_from_pinned_upstream_definitions():
    captured = json.loads((Path(__file__).parent / "fixtures/hdfix-4.1.0-schema.json").read_text())
    assert captured["tag"] == install.HDFIX_VERSION
    assert captured["fields"] == install.SETTINGS_SCHEMA
    assert captured["constraints"] == install.SETTINGS_CONSTRAINTS
    assert len(captured["source_sha256"]) == 2
    template = install.parse_ini(install.SETTINGS_TEMPLATE)
    assert {s: set(template[s]) for s in template.sections()} == {
        s: set(keys) for s, keys in captured["fields"].items()}


@pytest.mark.parametrize("change", [
    lambda t: t.replace("Fix Film Grain=1", "Fix Film Gran=1"),  # unchanged counts
    lambda t: t.replace("Fix Film Grain=1", "Fix Film Grain=yes"),
    lambda t: t.replace('Fix  High  CPU  Usage="Full"', 'Fix  High  CPU  Usage="nonsense"'),
    lambda t: t.replace("Window Width=0", "Window Width=-5"),
    lambda t: t.replace("Custom Grass Distance Multiplier=1.0", "Custom Grass Distance Multiplier=nan"),
])
def test_exact_schema_and_values_reject_corrupt_edits(tmp_path, change):
    _, text = settings(tmp_path)
    with pytest.raises(RuntimeError, match="Settings validation"):
        install.validate_settings(change(text))


def test_preserve_language_render_hotkeys_and_manual_launcher_choice(tmp_path):
    game, text = settings(tmp_path)
    edited = text.replace('Game Language="en"', 'Game Language="fr"').replace(
        "Render Width=0", "Render Width=1920").replace('Return to Developer Menu="F8"',
                                                      'Return to Developer Menu="F9"').replace(
        "Skip Launcher=1", "Skip Launcher=0")
    (game / "plugins/MGSHDFix.settings").write_text(edited)
    opts = install.options_for_game("mgs2", (game, tmp_path), DEFAULT_OPTS, lambda m: None)
    assert opts["skip_launcher"] is False
    tx = install.InstallTxn(game, "mgs2", lambda m: None)
    install.write_settings(tx, install.GAMES["mgs2"], opts, lambda m: None)
    actual = tx.read_text_ours("plugins/MGSHDFix.settings")
    assert actual == edited
    tx.commit()


def test_explicit_change_preserves_other_custom_keys_and_reset_is_separate(tmp_path):
    game, text = settings(tmp_path)
    edited = text.replace('Game Language="en"', 'Game Language="fr"')
    opts = {**DEFAULT_OPTS, "button_icons": "PlayStation 2", "_changed": {"button_icons"},
            "_existing_settings": edited}
    tx = install.InstallTxn(game, "mgs2", lambda m: None)
    install.write_settings(tx, install.GAMES["mgs2"], opts, lambda m: None)
    actual = tx.read_text_ours("plugins/MGSHDFix.settings")
    assert 'Game Language="fr"' in actual and 'Button Icons="PlayStation 2"' in actual
    tx.commit()
    tx = install.InstallTxn(game, "mgs2", lambda m: None)
    install.write_settings(tx, install.GAMES["mgs2"], {**DEFAULT_OPTS, "_existing_settings": edited,
                                                    "_reset": True}, lambda m: None)
    assert tx.read_text_ours("plugins/MGSHDFix.settings") == text
    tx.commit()


def test_mgs1_preserves_custom_defaults_and_can_disable_launcher_skip(tmp_path, patch_download):
    game = tmp_path / "MGS1"
    game.mkdir()
    tx = install.InstallTxn(game, "mgs1", lambda m: None)
    install.install_m2fix(tx, tmp_path, DEFAULT_OPTS, lambda m: None)
    tx.commit()
    edited = (game / "MGSM2Fix.ini").read_text().replace("SkipIntro = true", "SkipIntro = false")
    (game / "MGSM2Fix.ini").write_text(edited)
    opts = {**DEFAULT_OPTS, "_existing_m2fix": edited, "skip_launcher": False,
            "_changed": {"skip_launcher"}}
    tx = install.InstallTxn(game, "mgs1", lambda m: None)
    install.install_m2fix(tx, tmp_path, opts, lambda m: None)
    actual = (game / "MGSM2Fix.ini").read_text()
    assert "StartGame = false" in actual and "SkipIntro = false" in actual
    assert "CheckForUpdates = false" in actual
    tx.commit()


def test_preferences_are_loaded_per_game(tmp_path):
    first, text = settings(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    (other / "plugins").mkdir()
    (other / "plugins/MGSHDFix.settings").write_text(text.replace('Button Icons="Steam Deck"',
                                                               'Button Icons="PlayStation 2"'))
    assert install.options_for_game("mgs2", (first, tmp_path), DEFAULT_OPTS, lambda m: None)["button_icons"] == "Steam Deck"
    assert install.options_for_game("mgs3", (other, tmp_path), DEFAULT_OPTS, lambda m: None)["button_icons"] == "PlayStation 2"


def test_known_old_template_value_is_migrated(tmp_path):
    game, text = settings(tmp_path)
    text = text.replace("Show Pressure Level Overlay=0", 'Show Pressure Level Overlay="Disabled"')
    (game / "plugins/MGSHDFix.settings").write_text(text)
    opts = install.options_for_game("mgs2", (game, tmp_path), DEFAULT_OPTS, lambda m: None)
    assert "Show Pressure Level Overlay=0" in opts["_existing_settings"]
