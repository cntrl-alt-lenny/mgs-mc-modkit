"""Malicious / corrupt archive handling — the security-critical path."""
from __future__ import annotations

from pathlib import Path

import sys

import pytest

import install

needs_symlinks = pytest.mark.skipif(
    sys.platform == "win32",
    reason="creating symlinks on Windows needs privileges bsdtar won't have")
from conftest import build_tar, build_zip


def test_rel_is_unsafe():
    assert install._rel_is_unsafe("/etc/passwd")
    assert install._rel_is_unsafe("../../evil")
    assert install._rel_is_unsafe("a/../../evil")
    assert install._rel_is_unsafe("\\windows\\system32")
    assert install._rel_is_unsafe("")
    assert not install._rel_is_unsafe("plugins/MGSHDFix.asi")
    assert not install._rel_is_unsafe("a/b/c.dll")


def test_normal_zip_extracts_cleanly(tmp_path: Path):
    arc = build_zip(tmp_path / "ok.zip",
                    {"plugins/x.asi": b"a", "winhttp.dll": b"b"})
    rels = install.staged_files(arc, tmp_path / "stage")
    assert set(rels) == {"plugins/x.asi", "winhttp.dll"}


def test_traversal_member_rejected(tmp_path: Path):
    arc = build_tar(tmp_path / "evil.tar",
                    regular={"../escape.txt": b"pwn", "ok.txt": b"fine"})
    with pytest.raises(install.UnsafeArchiveError):
        install.staged_files(arc, tmp_path / "stage")
    # Nothing escaped the staging parent.
    assert not (tmp_path / "escape.txt").exists()


@needs_symlinks
def test_symlink_member_rejected(tmp_path: Path):
    arc = build_tar(tmp_path / "link.tar",
                    regular={"readme.txt": b"hi"},
                    symlinks={"pwn": "/etc/passwd"})
    with pytest.raises(install.UnsafeArchiveError):
        install.staged_files(arc, tmp_path / "stage")


@needs_symlinks
def test_symlinked_dir_rejected(tmp_path: Path):
    arc = build_tar(tmp_path / "linkdir.tar",
                    regular={"safe/inner.txt": b"hi"},
                    symlinks={"out": "/tmp"})
    with pytest.raises(install.UnsafeArchiveError):
        install.staged_files(arc, tmp_path / "stage")


def test_install_archive_rejects_traversal(tmp_path: Path, game_dir: Path):
    tx = install.InstallTxn(game_dir, "mgs2", lambda m: None)
    arc = build_tar(tmp_path / "evil.tar", regular={"../escape.txt": b"pwn"})
    with pytest.raises(install.UnsafeArchiveError):
        tx.install_archive(arc)
    assert tx.added == []
    assert not (game_dir.parent / "escape.txt").exists()
