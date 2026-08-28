"""Konami launcher_sv handling: fresh synth, in-place patch, edge cases."""
from __future__ import annotations

import install
from conftest import make_steam_root

OPTS = {"hq_movies": True, "device": "steam_deck"}


def _noop(_m):
    pass


def _tx(game_dir):
    return install.InstallTxn(game_dir, "mgs2", _noop)


def _save_path(game_dir, dirname, account):
    return (game_dir / f"{dirname.lower()}_savedata_win" / account
            / "launcher" / "launcher_sv")


def test_fresh_save_synthesised(tmp_path):
    game_dir = tmp_path / "MGS2"
    game_dir.mkdir()
    steam_root = make_steam_root(tmp_path, "111")
    tx = _tx(game_dir)
    install.set_launcher_options(tx, install.GAMES["mgs2"], steam_root, OPTS,
                                 _noop)

    sid = str(111 + install.STEAMID64_BASE)
    sv = _save_path(game_dir, "MGS2", sid)
    assert sv.is_file()
    data = install._read_launcher_sv(sv)
    assert data["HiresoMovie"] == "1"
    assert data["HiresoRender"] == "0"
    assert data["HiresoUpScale"] == "0"
    # Byte-for-byte format: UTF-8 BOM + trailing CRLF.
    raw = sv.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert raw.endswith(b"\r\n")


def test_existing_save_patched_preserving_other_keys(tmp_path):
    game_dir = tmp_path / "MGS2"
    sv = _save_path(game_dir, "MGS2", "acct")
    sv.parent.mkdir(parents=True)
    sv.write_bytes(install._launcher_sv_bytes(
        ["languageLauncher", "HiresoMovie", "launcherMasterVolume"],
        ["3", "0", "7"]))

    tx = _tx(game_dir)
    install.set_launcher_options(tx, install.GAMES["mgs2"],
                                 make_steam_root(tmp_path), OPTS, _noop)

    data = install._read_launcher_sv(sv)
    assert data["HiresoMovie"] == "1"          # patched
    assert data["languageLauncher"] == "3"     # preserved
    assert data["launcherMasterVolume"] == "7"  # preserved
    # The original was backed up so uninstall can restore it.
    assert tx.overwritten


def test_mismatched_array_lengths_do_not_crash(tmp_path):
    game_dir = tmp_path / "MGS2"
    sv = _save_path(game_dir, "MGS2", "acct")
    sv.parent.mkdir(parents=True)
    # keyList longer than valueList — a corrupt/hand-edited save.
    sv.write_bytes(install._launcher_sv_bytes(
        ["languageLauncher", "HiresoMovie", "orphanKey"], ["3", "0"]))

    tx = _tx(game_dir)
    before = sv.read_bytes()
    assert not install.set_launcher_options(
        tx, install.GAMES["mgs2"], make_steam_root(tmp_path), OPTS, _noop)
    assert sv.read_bytes() == before       # malformed save was not rewritten


def test_unparseable_save_left_alone(tmp_path):
    game_dir = tmp_path / "MGS2"
    sv = _save_path(game_dir, "MGS2", "acct")
    sv.parent.mkdir(parents=True)
    sv.write_bytes(b"\xef\xbb\xbfnot json at all")

    tx = _tx(game_dir)
    assert not install.set_launcher_options(
        tx, install.GAMES["mgs2"], make_steam_root(tmp_path), OPTS, _noop)
    # Untouched — still the garbage we wrote, nothing tracked.
    assert sv.read_bytes() == b"\xef\xbb\xbfnot json at all"
    assert tx.added == []


def test_mgs3_deck_forces_hiresotexture_off(tmp_path):
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    steam_root = make_steam_root(tmp_path, "222")
    tx = install.InstallTxn(game_dir, "mgs3", _noop)
    install.set_launcher_options(tx, install.GAMES["mgs3"], steam_root,
                                 {"hq_movies": True, "device": "steam_deck"},
                                 _noop)
    sid = str(222 + install.STEAMID64_BASE)
    data = install._read_launcher_sv(_save_path(game_dir, "MGS3", sid))
    assert data["HiresoTexture"] == "0"


def test_mgs3_non_deck_preserves_existing_texture(tmp_path):
    game_dir = tmp_path / "MGS3"
    sv = _save_path(game_dir, "MGS3", "acct")
    sv.parent.mkdir(parents=True)
    sv.write_bytes(install._launcher_sv_bytes(
        ["HiresoMovie", "HiresoTexture"], ["0", "1"]))

    tx = install.InstallTxn(game_dir, "mgs3", _noop)
    install.set_launcher_options(tx, install.GAMES["mgs3"],
                                 make_steam_root(tmp_path),
                                 {"hq_movies": True, "device": "generic_linux"},
                                 _noop)
    data = install._read_launcher_sv(sv)
    assert data["HiresoTexture"] == "1"        # user's choice preserved
