"""Fault injection for durable pre-run recovery, including changed repairs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import install
from conftest import build_zip


def noop(message):
    pass


def test_failed_repair_restores_changed_mod_and_custom_file(game_dir):
    original = game_dir / "winhttp.dll"
    original.write_bytes(b"stock")
    first = install.InstallTxn(game_dir, "mgs2", noop)
    first.write_bytes("winhttp.dll", b"old-mod")
    first.write_bytes("plugins/custom.ini", b"my-settings")
    first.commit()
    manifest = (first.root / install.MANIFEST_NAME).read_bytes()
    repair = install.InstallTxn(game_dir, "mgs2", noop)
    repair.write_bytes("winhttp.dll", b"new-mod")
    repair.write_bytes("plugins/custom.ini", b"replacement-defaults")
    repair.write_bytes("new-file", b"added")
    assert repair.rollback()
    assert original.read_bytes() == b"old-mod"
    assert (game_dir / "plugins/custom.ini").read_bytes() == b"my-settings"
    assert (first.root / install.MANIFEST_NAME).read_bytes() == manifest
    assert not (game_dir / "new-file").exists()
    assert install.uninstall_game(game_dir, noop)[1]
    assert original.read_bytes() == b"stock"


@pytest.mark.parametrize("point", ["before_journal", "after_journal", "after_write"])
def test_process_death_preserves_original(game_dir, point):
    """Real process exits, including the old dangerous backup/intent interval."""
    (game_dir / "winhttp.dll").write_bytes(b"STOCK")
    code = """
import os, sys
from pathlib import Path
import install
t=install.InstallTxn(Path(sys.argv[1]), 'mgs2', lambda x: None)
if sys.argv[2]=='before_journal':
    t._prepare_dest('winhttp.dll')
elif sys.argv[2]=='after_journal':
    t._journal_planned(['winhttp.dll'])
else:
    t.write_bytes('winhttp.dll', b'NEW-MOD')
os._exit(23)
"""
    result = subprocess.run([sys.executable, "-c", code, str(game_dir), point],
                            cwd=Path(install.__file__).parent)
    assert result.returncode == 23
    next_run = install.InstallTxn(game_dir, "mgs2", noop)
    assert (game_dir / "winhttp.dll").read_bytes() == b"STOCK"
    next_run.write_bytes("winhttp.dll", b"MOD")
    next_run.commit()
    assert install.uninstall_game(game_dir, noop)[1]
    assert (game_dir / "winhttp.dll").read_bytes() == b"STOCK"


def test_failed_restore_keeps_record_and_can_retry(game_dir, monkeypatch):
    (game_dir / "audio.sdt").write_bytes(b"before")
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("audio.sdt", b"after")
    restore = install.restore_snapshot

    def denied(*args):
        raise PermissionError("sharing violation")

    monkeypatch.setattr(install, "restore_snapshot", denied)
    assert not tx.rollback()
    assert tx.journal.is_file()
    assert (tx.rollback_dir / "audio.sdt").read_bytes() == b"before"
    monkeypatch.setattr(install, "restore_snapshot", restore)
    assert tx.rollback()
    assert (game_dir / "audio.sdt").read_bytes() == b"before"


def test_large_file_rollback_uses_snapshot_without_full_copy(game_dir, monkeypatch):
    monkeypatch.setattr(install, "BACKUP_MAX_BYTES", 2)
    (game_dir / "audio.sdt").write_bytes(b"LARGE-ORIGINAL")
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("audio.sdt", b"new-audio")
    assert (tx.rollback_dir / "audio.sdt").read_bytes() == b"LARGE-ORIGINAL"
    monkeypatch.setattr(install, "atomic_copy", lambda *a: pytest.fail("unnecessary large copy"))
    assert tx.rollback()
    assert (game_dir / "audio.sdt").read_bytes() == b"LARGE-ORIGINAL"


def test_snapshot_copy_fallback_and_space_failure_leave_original(game_dir, monkeypatch):
    (game_dir / "payload").write_bytes(b"original")
    monkeypatch.setattr(install.os, "link", lambda *a: (_ for _ in ()).throw(OSError("unsupported")))
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("payload", b"replacement")
    assert tx.rollback()
    assert (game_dir / "payload").read_bytes() == b"original"
    monkeypatch.setattr(install, "free_bytes", lambda p: 0)
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    with pytest.raises(RuntimeError, match="safely preserve"):
        tx.write_bytes("payload", b"replacement")
    assert (game_dir / "payload").read_bytes() == b"original"
    assert tx.rollback()


def test_committed_journal_is_cleanup_only(game_dir, monkeypatch):
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("payload", b"accepted")
    unlink = Path.unlink

    def fail_journal(path, *a, **kw):
        if path == tx.journal:
            raise PermissionError("busy journal")
        return unlink(path, *a, **kw)

    monkeypatch.setattr(Path, "unlink", fail_journal)
    tx.commit()
    assert tx.committed and tx.journal.exists()
    monkeypatch.setattr(Path, "unlink", unlink)
    install.InstallTxn(game_dir, "mgs2", noop)
    assert (game_dir / "payload").read_bytes() == b"accepted"
    assert not tx.journal.exists()


def test_verification_failure_cannot_publish_manifest(game_dir):
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("payload", b"expected")
    (game_dir / "payload").write_bytes(b"altered!")  # same length: hashing matters
    with pytest.raises(RuntimeError, match="does not match"):
        tx.commit()
    assert not (tx.root / install.MANIFEST_NAME).exists()
    assert tx.rollback()


def test_unbacked_original_can_finish_removal_after_steam_restore(game_dir, monkeypatch):
    monkeypatch.setattr(install, "BACKUP_MAX_BYTES", 2)
    (game_dir / "audio.sdt").write_bytes(b"original-audio")
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    tx.write_bytes("audio.sdt", b"mod-audio")
    tx.commit()
    notes, ok = install.uninstall_game(game_dir, noop)
    assert not ok and any("Verify integrity" in n for n in notes)
    assert (tx.root / install.MANIFEST_NAME).exists()
    (game_dir / "audio.sdt").write_bytes(b"original-audio")  # Steam restored it
    assert install.uninstall_game(game_dir, noop)[1]
    assert not tx.root.exists()


@pytest.mark.parametrize("rel", ["mgs-modkit/backups/stock", "MGS-MODKIT/manifest.json",
                                  "mgs2_savedata_win/123/save", "METAL GEAR SOLID2.exe",
                                  "us/demo/innocent.sdt:stream", "aux.txt"])
def test_protected_paths_never_reach_game(game_dir, tmp_path, rel):
    archive = build_zip(tmp_path / "bad.zip", {"us/demo/a.sdt": b"audio", rel: b"bad"})
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    with pytest.raises(install.UnsafeArchiveError):
        tx.install_archive(archive, component="audio")
    assert not (game_dir / "us/demo/a.sdt").exists()
    assert tx.rollback()


def test_audio_skips_docs_but_rejects_unrelated_payload(game_dir, tmp_path):
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    archive = build_zip(tmp_path / "good.zip", {"us/demo/a.sdt": b"audio", "README.md": b"notes"})
    assert tx.install_archive(archive, component="audio") == ["us/demo/a.sdt"]
    assert not (game_dir / "README.md").exists()
    assert tx.rollback()
    archive = build_zip(tmp_path / "bad.zip", {"us/demo/a.sdt": b"audio", "plugins/evil.asi": b"code"})
    tx = install.InstallTxn(game_dir, "mgs2", noop)
    with pytest.raises(install.UnsafeArchiveError):
        tx.install_archive(archive, component="audio")
    assert tx.rollback()


def test_lock_rejects_another_process_and_releases_after_exit(game_dir):
    code = """
import sys
from pathlib import Path
import install
try:
    with install.GameLock(Path(sys.argv[1])): pass
except RuntimeError:
    sys.exit(9)
"""
    appdir = str(install.app_data_dir())
    code = code.replace("try:", f"install.app_data_dir=lambda: Path({appdir!r})\ntry:")
    with install.GameLock(game_dir):
        assert subprocess.run([sys.executable, "-c", code, str(game_dir)],
                              cwd=Path(install.__file__).parent).returncode == 9
    assert subprocess.run([sys.executable, "-c", code, str(game_dir)],
                          cwd=Path(install.__file__).parent).returncode == 0


@pytest.mark.parametrize("record", [[], {"schema": 2, "entries": []}, {"added": ["../stock"]}])
def test_invalid_records_fail_closed(game_dir, record):
    root = game_dir / install.MODKIT_DIRNAME
    root.mkdir()
    manifest = root / install.MANIFEST_NAME
    manifest.write_text(json.dumps(record))
    with pytest.raises(install.CorruptManifestError):
        install.InstallTxn(game_dir, "mgs2", noop)
    assert manifest.exists()
