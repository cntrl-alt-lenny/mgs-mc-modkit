"""Transactional install: staging, backups, rollback, manifest, uninstall."""
from __future__ import annotations

import json
from pathlib import Path

import install
from conftest import build_audio_zip, build_base_audio_zip, make_steam_root

DEFAULT_OPTS = {
    "device": "steam_deck",
    "button_icons": "Steam Deck",
    "audio_mode": "Stereo (2.0)",
    "hq_movies": True,
    "skip_splash": True,
    "update_check": False,
    "skip_launcher": True,
}


def _noop(_msg):
    pass


def install_mgs2_full(game_dir: Path, steam_root: Path,
                      opts: dict | None = None) -> install.InstallTxn:
    """Mirror main()'s per-game MGS2 body inside one committed transaction."""
    opts = opts or DEFAULT_OPTS
    g = install.GAMES["mgs2"]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        install.install_hdfix(tx, tmp, _noop)
        install.install_bugfix(tx, g, tmp, _noop)
        install.write_settings(tx, g, opts, _noop)
        install.set_launcher_options(tx, g, steam_root, opts, _noop)
        tx.commit()
    return tx


# ---------------------------------------------------------------------------
def test_manifest_written_and_shaped(tmp_path, game_dir, patch_download):
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    manifest = game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    data = json.loads(manifest.read_text())
    assert data["game"] == "mgs2"
    assert data["modkit_version"] == install.MODKIT_VERSION
    assert "MGSHDFix" in data["mods"]
    assert "winhttp.dll" in data["added"]
    assert "plugins/MGSHDFix.settings" in data["added"]
    # verify_install agrees the install is complete.
    assert install.verify_install(install.GAMES["mgs2"], game_dir) == []


def test_overwrite_backs_up_original(tmp_path, game_dir, patch_download):
    # A stock file the mod will overwrite.
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    manifest = json.loads(
        (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
    over = {o["path"]: o for o in manifest["overwritten"]}
    assert "winhttp.dll" in over
    backup = game_dir / install.MODKIT_DIRNAME / over["winhttp.dll"]["backup"]
    assert backup.read_bytes() == b"ORIGINAL-STOCK"
    # The live file is now the mod's version, not the original.
    assert (game_dir / "winhttp.dll").read_bytes() != b"ORIGINAL-STOCK"


def test_rollback_restores_everything(tmp_path, game_dir, patch_download):
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    g = install.GAMES["mgs2"]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        install.install_hdfix(tx, tmp, _noop)
        install.install_bugfix(tx, g, tmp, _noop)
        tx.rollback()

    # Added files gone, original restored, no modkit dir left behind.
    assert (game_dir / "winhttp.dll").read_bytes() == b"ORIGINAL-STOCK"
    assert not (game_dir / "plugins" / "MGSHDFix.asi").exists()
    assert not (game_dir / install.MODKIT_DIRNAME).exists()
    # The game's own file is untouched.
    assert (game_dir / "METAL GEAR SOLID2.exe").exists()


def test_failed_install_rolls_back(tmp_path, game_dir, patch_download, monkeypatch):
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    g = install.GAMES["mgs2"]

    def boom(tx, gg, tmp, log):
        raise RuntimeError("simulated bugfix failure")

    monkeypatch.setattr(install, "install_bugfix", boom)

    import tempfile
    import pytest
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        with pytest.raises(RuntimeError):
            try:
                install.install_hdfix(tx, tmp, _noop)
                install.install_bugfix(tx, g, tmp, _noop)
            except BaseException:
                tx.rollback()
                raise
    assert (game_dir / "winhttp.dll").read_bytes() == b"ORIGINAL-STOCK"
    assert not (game_dir / install.MODKIT_DIRNAME).exists()


def test_uninstall_reverses_install(tmp_path, game_dir, patch_download):
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    notes, ok = install.uninstall_game(game_dir, _noop)

    assert ok
    assert (game_dir / "winhttp.dll").read_bytes() == b"ORIGINAL-STOCK"
    assert not (game_dir / "plugins" / "MGSHDFix.asi").exists()
    assert not (game_dir / "plugins" / "MGSHDFix.settings").exists()
    assert not (game_dir / install.MODKIT_DIRNAME).exists()
    assert (game_dir / "METAL GEAR SOLID2.exe").exists()
    assert any("restored" in n for n in notes)


def test_idempotent_reinstall(tmp_path, game_dir, patch_download):
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)
    # Second run must NOT treat our own files as stock originals to back up.
    install_mgs2_full(game_dir, steam_root)

    manifest = json.loads(
        (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
    over = {o["path"] for o in manifest["overwritten"]}
    # winhttp was the only genuine stock file; our own files aren't re-backed.
    assert "plugins/MGSHDFix.asi" not in over
    assert install.verify_install(install.GAMES["mgs2"], game_dir) == []

    # A clean uninstall still returns to stock after a double install.
    _, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert (game_dir / "winhttp.dll").read_bytes() == b"ORIGINAL-STOCK"
    assert not (game_dir / install.MODKIT_DIRNAME).exists()


def test_large_overwrite_not_backed_up(tmp_path, game_dir, patch_download,
                                       monkeypatch):
    monkeypatch.setattr(install, "BACKUP_MAX_BYTES", 4)  # tiny threshold
    (game_dir / "winhttp.dll").write_bytes(b"BIG-ORIGINAL-CONTENT")  # > 4 bytes
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    manifest = json.loads(
        (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
    over = {o["path"]: o for o in manifest["overwritten"]}
    assert over["winhttp.dll"]["backup"] is None

    notes, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert any("Verify integrity" in n for n in notes)


def test_m2fix_ini_patched_and_tracked(tmp_path, patch_download):
    game_dir = tmp_path / "MGS1"
    game_dir.mkdir()
    import tempfile
    opts = {"update_check": False, "skip_launcher": True}
    with tempfile.TemporaryDirectory() as td:
        tx = install.InstallTxn(game_dir, "mgs1", _noop)
        install.install_m2fix(tx, Path(td), opts, _noop)
        tx.commit()

    ini = (game_dir / "MGSM2Fix.ini").read_text()
    assert "StartGame = true" in ini
    assert "CheckForUpdates = false" in ini

    _, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert not (game_dir / "MGSM2Fix.ini").exists()
    assert not (game_dir / "MGSM2Fix64.asi").exists()


def test_uninstall_removes_legacy_asi(tmp_path):
    game_dir = tmp_path / "MGS1"
    game_dir.mkdir()
    (game_dir / "MGSM2Fix.asi").write_bytes(b"legacy-unified-asi")

    notes, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert not (game_dir / "MGSM2Fix.asi").exists()
    assert any("legacy" in n for n in notes)


def test_failed_reinstall_preserves_previous_install(tmp_path, game_dir,
                                                     patch_download, monkeypatch):
    """A re-install that fails must fall back to the previous working install,
    not orphan files or destroy its manifest/backups."""
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)           # run 1: succeeds

    manifest_path = game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    m1 = manifest_path.read_text()
    asi = (game_dir / "plugins" / "MGSHDFix.asi").read_bytes()

    # run 2: fails at the bugfix step, after HDFix has been re-applied.
    g = install.GAMES["mgs2"]
    import tempfile
    import pytest
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        with pytest.raises(RuntimeError):
            try:
                install.install_hdfix(tx, tmp, _noop)
                raise RuntimeError("simulated failure during re-install")
            except BaseException:
                tx.rollback()
                raise

    # Previous install is intact: manifest + backups preserved, files present,
    # true stock backup NOT clobbered, still a complete install.
    assert manifest_path.read_text() == m1
    assert (game_dir / "plugins" / "MGSHDFix.asi").read_bytes() == asi
    backup = game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll"
    assert backup.read_bytes() == b"ORIGINAL-STOCK"
    assert install.verify_install(g, game_dir) == []

    # And it can still be cleanly uninstalled back to stock.
    _, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert (game_dir / "winhttp.dll").read_bytes() == b"ORIGINAL-STOCK"
    assert not (game_dir / install.MODKIT_DIRNAME).exists()


def test_uninstall_keeps_recovery_data_on_error(tmp_path, game_dir,
                                                patch_download, monkeypatch):
    """If a restore fails, the manifest/backups must survive and ok must be
    False — never report success while files are half-reverted."""
    (game_dir / "winhttp.dll").write_bytes(b"ORIGINAL-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    # Make one restore fail by deleting a backup out from under the uninstaller.
    (game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll").unlink()

    notes, ok = install.uninstall_game(game_dir, _noop)
    assert ok is False
    # Recovery data kept for a retry.
    assert (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).is_file()
    assert any("could not be reverted" in n for n in notes)


# -- incremental (partial) re-install must keep the earlier install's record --
def test_incremental_install_merges_manifest(tmp_path):
    """Install MGS3 Base, then later install ONLY the Update: the Base files
    must remain in the manifest so uninstall removes everything (regression)."""
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    manifest_path = game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME

    # Run 1: Base only (many unique files like us/stage/clip0000.sdt).
    base = build_base_audio_zip(tmp_path / "base.zip", n=30)
    tx1 = install.InstallTxn(game_dir, "mgs3", _noop)
    install.install_better_audio(
        tx1, install.order_audio_components("mgs3", {"base": base}), _noop)
    tx1.commit()
    base_added = set(json.loads(manifest_path.read_text())["added"])
    assert "us/stage/clip0000.sdt" in base_added

    # Run 2: Update only — must NOT drop the Base files/mods from the manifest.
    upd = build_audio_zip(tmp_path / "update.zip", {"us/patch/fix.sdt": b"p"})
    tx2 = install.InstallTxn(game_dir, "mgs3", _noop)
    install.install_better_audio(
        tx2, install.order_audio_components("mgs3", {"update": upd}), _noop)
    tx2.commit()
    m2 = json.loads(manifest_path.read_text())
    assert base_added <= set(m2["added"])                 # Base files carried over
    assert "us/patch/fix.sdt" in m2["added"]              # Update file recorded
    assert "Better Audio — Base 1.0" in m2["mods"]        # both mods present
    assert "Better Audio — Update 2.0" in m2["mods"]

    # Uninstall removes BOTH the Base and Update payloads — nothing orphaned.
    notes, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert not (game_dir / "us" / "stage" / "clip0000.sdt").exists()
    assert not (game_dir / "us" / "patch" / "fix.sdt").exists()
    assert not (game_dir / install.MODKIT_DIRNAME).exists()
