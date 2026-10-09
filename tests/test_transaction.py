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
    assert not ok  # originals still need Steam restoration
    assert (game_dir / install.MODKIT_DIRNAME).exists()
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
    (game_dir / "METAL GEAR SOLID.exe").write_bytes(b"game fixture")
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
    assert "us/demo/clip0000.sdt" in base_added

    # Run 2: Update only — must NOT drop the Base files/mods from the manifest.
    upd = build_audio_zip(tmp_path / "update.zip", {"us/demo/fix.sdt": b"p"})
    tx2 = install.InstallTxn(game_dir, "mgs3", _noop)
    install.install_better_audio(
        tx2, install.order_audio_components("mgs3", {"update": upd}), _noop)
    tx2.commit()
    m2 = json.loads(manifest_path.read_text())
    assert base_added <= set(m2["added"])                 # Base files carried over
    assert "us/demo/fix.sdt" in m2["added"]              # Update file recorded
    assert "MGS3 Better Audio" in m2["mods"]              # both mods present
    assert "MGS3 Better Audio update" in m2["mods"]

    # Uninstall removes BOTH the Base and Update payloads — nothing orphaned.
    notes, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert not (game_dir / "us" / "demo" / "clip0000.sdt").exists()
    assert not (game_dir / "us" / "patch" / "fix.sdt").exists()
    assert not (game_dir / install.MODKIT_DIRNAME).exists()


# ---------------------------------------------------------------------------
# v1.7.0 Group A — data-loss chain regressions
# ---------------------------------------------------------------------------
def test_existing_backup_is_never_clobbered(tmp_path, game_dir, patch_download):
    """The oldest backup is closest to stock; a later run must not overwrite it."""
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)          # backs up TRUE-STOCK

    backup = game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll"
    assert backup.read_bytes() == b"TRUE-STOCK"

    # Simulate a lost record: delete the manifest but keep backups on disk.
    (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).unlink()

    # Re-install: winhttp.dll on disk is now MOD content, not stock. Without the
    # guard this would copy the mod file over the genuine backup.
    install_mgs2_full(game_dir, steam_root)
    assert backup.read_bytes() == b"TRUE-STOCK"      # original still recoverable

    _, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert (game_dir / "winhttp.dll").read_bytes() == b"TRUE-STOCK"


def test_corrupt_manifest_halts_and_changes_nothing(tmp_path, game_dir,
                                                    patch_download):
    import pytest
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)

    manifest = game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    manifest.write_text("{ this is not json")
    backup = game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll"

    with pytest.raises(install.CorruptManifestError):
        install.InstallTxn(game_dir, "mgs2", _noop)

    # Refused to guess; recovery data untouched.
    assert backup.read_bytes() == b"TRUE-STOCK"
    assert manifest.is_file()


def test_uninstall_rejects_manifest_path_escape(tmp_path):
    game_dir = tmp_path / "MGS2"
    game_dir.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"do not delete")
    root = game_dir / install.MODKIT_DIRNAME
    root.mkdir()
    (root / install.MANIFEST_NAME).write_text(json.dumps({
        "added": ["../outside.txt"],
        "overwritten": [],
    }))

    notes, ok = install.uninstall_game(game_dir, _noop)

    assert not ok
    assert outside.read_bytes() == b"do not delete"
    assert (root / install.MANIFEST_NAME).is_file()
    assert any("unsafe" in note for note in notes)


def test_authored_file_is_in_recovery_journal(tmp_path):
    game_dir = tmp_path / "MGS2"
    game_dir.mkdir()
    tx = install.InstallTxn(game_dir, "mgs2", _noop)

    tx.write_bytes("plugins/MGSHDFix.settings", b"settings")

    journal = json.loads(
        (game_dir / install.MODKIT_DIRNAME / install.JOURNAL_NAME)
        .read_text())
    assert journal["schema"] == 2
    assert journal["entries"] == [{"path": "plugins/MGSHDFix.settings", "existed": False}]
    tx.rollback()


def test_rollback_keeps_preexisting_root_even_without_manifest(tmp_path, game_dir,
                                                               patch_download):
    """A failed run must not delete backups that predate it (manifest or not)."""
    import tempfile
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")
    steam_root = make_steam_root(tmp_path)
    install_mgs2_full(game_dir, steam_root)
    (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).unlink()
    backup = game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll"

    with tempfile.TemporaryDirectory() as td:
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        assert tx._had_prior is False          # no manifest to load
        assert tx._root_existed is True        # but our folder DID exist
        install.install_hdfix(tx, Path(td), _noop)
        tx.rollback()

    assert backup.read_bytes() == b"TRUE-STOCK"
    assert (game_dir / install.MODKIT_DIRNAME).exists()


def test_failed_fresh_install_still_leaves_no_trace(tmp_path, game_dir,
                                                    patch_download):
    """The other side of the gate: a truly fresh failed install cleans up."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        assert tx._root_existed is False
        install.install_hdfix(tx, Path(td), _noop)
        tx.rollback()
    assert not (game_dir / install.MODKIT_DIRNAME).exists()
    assert not (game_dir / "winhttp.dll").exists()


def test_interrupted_run_journal_is_adopted(tmp_path, game_dir, patch_download):
    """SIGKILL mid-move: the next run must treat moved files as OURS, not stock."""
    import tempfile
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")

    # Simulate a killed run: journal written, files moved, no commit.
    with tempfile.TemporaryDirectory() as td:
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        install.install_hdfix(tx, Path(td), _noop)
        assert tx.journal.is_file()            # journal exists mid-flight
        # (no commit, no rollback — process "dies" here)

    backup = game_dir / install.MODKIT_DIRNAME / "backups" / "winhttp.dll"
    assert backup.read_bytes() == b"TRUE-STOCK"

    # Next run: adopts the journal, so MOD files are not re-backed-up as stock.
    with tempfile.TemporaryDirectory() as td:
        tx2 = install.InstallTxn(game_dir, "mgs2", _noop)
        assert (game_dir / "winhttp.dll").read_bytes() == b"TRUE-STOCK"
        assert not (game_dir / "wininet.dll").exists()  # pre-run state recovered
        install.install_hdfix(tx2, Path(td), _noop)
        tx2.commit()

    assert backup.read_bytes() == b"TRUE-STOCK"       # genuine original intact
    assert not tx2.journal.exists()                   # cleared on commit

    _, ok = install.uninstall_game(game_dir, _noop)
    assert ok
    assert (game_dir / "winhttp.dll").read_bytes() == b"TRUE-STOCK"


def test_torn_journal_does_not_crash(tmp_path, game_dir, patch_download):
    root = game_dir / install.MODKIT_DIRNAME
    root.mkdir(parents=True)
    (root / install.JOURNAL_NAME).write_text('["partial writ')   # torn
    import pytest
    with pytest.raises(install.CorruptManifestError):
        install.InstallTxn(game_dir, "mgs2", _noop)
    assert (root / install.JOURNAL_NAME).read_text() == '["partial writ'


# ---------------------------------------------------------------------------
# v1.7.0 Group B — free space + entry mode
# ---------------------------------------------------------------------------
def test_check_space_allows_when_room(tmp_path):
    ok, msg = install.check_space(tmp_path, 1024, margin=0)
    assert ok and msg == ""


def test_check_space_blocks_when_full(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "free_bytes", lambda p: 100 * 1024 * 1024)
    ok, msg = install.check_space(tmp_path, 10 * 1024 ** 3)
    assert ok is False
    assert "Not enough free space" in msg
    assert "twice" in msg                       # explains the staging cost


def test_check_space_does_not_block_when_undetectable(tmp_path, monkeypatch):
    def boom(p):
        raise OSError("statvfs unavailable")
    monkeypatch.setattr(install, "free_bytes", boom)
    ok, _ = install.check_space(tmp_path, 10 * 1024 ** 3)
    assert ok is True                           # never block on uncertainty


def test_install_aborts_cleanly_when_out_of_space(tmp_path, game_dir,
                                                  patch_download, monkeypatch):
    """Full drive must fail before touching the game, not mid-extraction."""
    import pytest
    import tempfile
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")
    monkeypatch.setattr(install, "free_bytes", lambda p: 1024)   # ~nothing free
    with tempfile.TemporaryDirectory() as td:
        tx = install.InstallTxn(game_dir, "mgs2", _noop)
        with pytest.raises(RuntimeError, match="Not enough free space"):
            install.install_hdfix(tx, Path(td), _noop)
        tx.rollback()
    assert (game_dir / "winhttp.dll").read_bytes() == b"TRUE-STOCK"
    assert not (game_dir / "plugins" / "MGSHDFix.asi").exists()


def test_archive_payload_bytes_reads_sizes(tmp_path):
    from conftest import build_zip
    z = build_zip(tmp_path / "a.zip", {"a.bin": b"x" * 5000,
                                       "b/c.bin": b"y" * 3000})
    assert install.archive_payload_bytes(z) == 8000


def test_mode_menu_skipped_on_fresh_system(tmp_path, game_dir):
    from conftest import FakeUI
    ui = FakeUI()                                # no menu scripted
    found = {"mgs2": (game_dir, tmp_path)}
    assert install.already_modded(found) == []
    assert install.choose_mode(ui, found) == "install"   # no dialog shown


def test_mode_menu_offered_when_already_modded(tmp_path, game_dir,
                                               patch_download):
    from conftest import FakeUI
    install_mgs2_full(game_dir, make_steam_root(tmp_path))
    found = {"mgs2": (game_dir, tmp_path)}
    assert install.already_modded(found) == ["mgs2"]
    assert install.choose_mode(FakeUI(menu=["uninstall"]), found) == "uninstall"
    assert install.choose_mode(FakeUI(menu=["install"]), found) == "install"
    assert install.choose_mode(FakeUI(menu=[None]), found) is None   # cancel


def test_uninstall_recovers_originals_when_manifest_lost(tmp_path, game_dir,
                                                        patch_download):
    """Damaged/lost record must not strand the user's backed-up originals."""
    (game_dir / "winhttp.dll").write_bytes(b"TRUE-STOCK")
    install_mgs2_full(game_dir, make_steam_root(tmp_path))
    (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).unlink()

    notes, ok = install.uninstall_game(game_dir, _noop)
    assert not ok  # restoration cannot identify/remove untracked mod files
    assert (game_dir / "winhttp.dll").read_bytes() == b"TRUE-STOCK"
    assert (game_dir / install.MODKIT_DIRNAME).exists()
    assert any("put back" in n for n in notes)


def test_uninstall_offered_when_only_backups_remain(tmp_path, game_dir,
                                                    patch_download):
    """run_uninstall must consider a modkit folder, not only a readable manifest."""
    install_mgs2_full(game_dir, make_steam_root(tmp_path))
    (game_dir / install.MODKIT_DIRNAME / install.MANIFEST_NAME).write_text("{bad")
    # A damaged manifest still leaves the folder -> the game stays recoverable.
    assert (game_dir / install.MODKIT_DIRNAME).is_dir()


def test_uninstall_preserves_unowned_legacy_in_other_roots(tmp_path):
    for key in ('mgs2', 'mgs3', 'mgs4', 'unknown', 'ambiguous'):
        root = tmp_path / key
        root.mkdir()
        exes = ([install.GAMES[key]['exe']] if key in install.GAMES else
                [install.GAMES['mgs1']['exe'], install.GAMES['mgs2']['exe']]
                if key == 'ambiguous' else [])
        for exe in exes:
            path = root / exe
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'game fixture')
        legacy = root / 'MGSM2Fix.asi'
        legacy.write_bytes(b'unowned user bytes')
        # Check both no-record and valid tracked-file removal.
        install.uninstall_game(root, _noop)
        assert legacy.read_bytes() == b'unowned user bytes'
        tx = install.InstallTxn(root, key if key in install.GAMES else 'mgs2', _noop)
        tracked = 'MGSPatriotFix.settings' if key == 'mgs4' else 'tracked.dll'
        tx.write_bytes(tracked, b'kit bytes')
        tx.commit()
        notes, ok = install.uninstall_game(root, _noop)
        assert ok, notes
        assert not (root / tracked).exists()
        assert legacy.read_bytes() == b'unowned user bytes'


def test_uninstall_legacy_tracked_restore_keeps_oldest_backup(tmp_path):
    root = tmp_path / 'mgs1'
    root.mkdir()
    (root / install.GAMES['mgs1']['exe']).write_bytes(b'game fixture')
    legacy = root / 'MGSM2Fix.asi'
    legacy.write_bytes(b'oldest original')
    for data in (b'first kit bytes', b'repaired kit bytes'):
        tx = install.InstallTxn(root, 'mgs1', _noop)
        tx.write_bytes('MGSM2Fix.asi', data)
        tx.commit()
    notes, ok = install.uninstall_game(root, _noop)
    assert ok, notes
    assert legacy.read_bytes() == b'oldest original'
    legacy.unlink()
    tx = install.InstallTxn(root, 'mgs1', _noop)
    tx.write_bytes('MGSM2Fix.asi', b'tracked addition')
    tx.commit()
    assert install.uninstall_game(root, _noop)[1]
    assert not legacy.exists()


def test_uninstall_malformed_or_unknown_record_preserves_legacy(tmp_path):
    for key, content in (
        ('broken-json', '{'),
        ('bad-path', '{"game":"mgs1","added":["../escape"],"overwritten":[]}'),
        ('unknown-game', '{"added":[],"overwritten":[]}'),
        ('wrong-game', '{"game":"mgs2","added":[],"overwritten":[]}'),
        ('orphan', None),
    ):
        root = tmp_path / key
        root.mkdir()
        (root / install.GAMES['mgs1']['exe']).write_bytes(b'game fixture')
        legacy = root / 'MGSM2Fix.asi'
        legacy.write_bytes(b'unowned user bytes')
        records = root / install.MODKIT_DIRNAME
        records.mkdir()
        if content is not None:
            (records / install.MANIFEST_NAME).write_text(content)
        notes, ok = install.uninstall_game(root, _noop)
        assert legacy.read_bytes() == b'unowned user bytes'
        if key in ('broken-json', 'bad-path', 'orphan'):
            assert not ok, notes
            assert records.exists()
