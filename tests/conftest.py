"""Shared fixtures for the MGS Mod Kit test-suite.

Everything here is offline: no network, no NexusMods, no real Steam. Mod
archives are tiny hand-built zips that mimic the real release layout, and the
network `download()` is monkeypatched to drop those zips where the installer
expects them. bsdtar is the only external dependency (as in production).
"""
from __future__ import annotations

import io
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import install  # noqa: E402


# ---------------------------------------------------------------------------
# Archive builders
# ---------------------------------------------------------------------------
def build_zip(path: Path, files: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return path


def build_tar(path: Path,
              regular: dict[str, bytes] | None = None,
              symlinks: dict[str, str] | None = None) -> Path:
    """Build a tar; symlinks map member-name -> link target (for hostile cases)."""
    with tarfile.open(path, "w") as t:
        for name, data in (regular or {}).items():
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
        for name, target in (symlinks or {}).items():
            ti = tarfile.TarInfo(name)
            ti.type = tarfile.SYMTYPE
            ti.linkname = target
            t.addfile(ti)
    return path


# Contents that satisfy each installer's post-extraction assertions.
MGSM2FIX_INI = (
    "[Main]\n"
    "StartGame = false\n"
    "SkipIntro = true\n"
    "\n"
    "[Network]\n"
    "CheckForUpdates = true\n"
).encode("utf-8")

MOD_LAYOUTS = {
    "MGSHDFix": {
        "winhttp.dll": b"stub",
        "wininet.dll": b"stub",
        "plugins/MGSHDFix.asi": b"stub",
        "plugins/MGSHDFix Config Tool.exe": b"stub",
        "UltimateASILoader_LICENSE.md": b"license",
    },
    "MGS2-Community-Bugfix": {
        "plugins/MGS2-Community-Bugfix-Compilation.asi": b"stub",
        "plugins/MGS2-Community-Bugfix-Compilation.ini": b"cfg",
        "assets/gcx/eu/_bp/scenerio.gcx": b"asset",
    },
    "MGS3-Community-Bugfix": {
        "plugins/MGS3-Community-Bugfix-Compilation.asi": b"stub",
        "assets/gcx/us/_bp/scenerio.gcx": b"asset",
    },
    "MGSM2Fix": {
        "d3d11.dll": b"stub",
        "dinput8.dll": b"stub",
        "MGSM2Fix64.asi": b"stub",
        "MGSM2Fix32.asi": b"stub",
        "MGSM2Fix.ini": MGSM2FIX_INI,
    },
}


@pytest.fixture
def mod_zips(tmp_path: Path) -> dict[str, Path]:
    """A fixture zip per mod, keyed by the URL substring that identifies it."""
    out = {}
    d = tmp_path / "_mod_fixtures"
    d.mkdir()
    for key, files in MOD_LAYOUTS.items():
        out[key] = build_zip(d / f"{key}.zip", files)
    return out


@pytest.fixture
def patch_download(monkeypatch, mod_zips):
    """Replace network download() with a copy from the matching fixture zip.

    Also exercises the real behaviour that a pinned sha256 is *passed* — we
    just don't enforce it here, since fixture bytes won't match the pinned
    production hash (checksum enforcement is tested separately).
    """
    calls = []

    def fake(url, dest, log, sha256=None):
        calls.append((url, sha256))
        for key, src in mod_zips.items():
            if key in url:
                shutil.copy(src, dest)
                return
        raise AssertionError(f"unexpected download URL: {url}")

    monkeypatch.setattr(install, "download", fake)
    return calls


@pytest.fixture
def game_dir(tmp_path: Path) -> Path:
    g = tmp_path / "game" / "MGS2"
    g.mkdir(parents=True)
    (g / "METAL GEAR SOLID2.exe").write_bytes(b"exe")
    return g


def make_steam_root(tmp_path: Path, account_id: str = "12345678") -> Path:
    root = tmp_path / "steam"
    (root / "userdata" / account_id).mkdir(parents=True)
    return root


# ---------------------------------------------------------------------------
# Better Audio archive fixtures + a scripted fake UI
# ---------------------------------------------------------------------------
# These shapes mirror the REAL NexusMods archives, inspected July 2026:
#   MGS2 Full Version      3821 files  us/demo us/demo2 us/movie us/movievr us/vox
#   MGS3 main file         6053 files  us/demo us/movie us/vox
#   MGS3 Update 2.0           3 files  us/demo/_bp/ + us/vox/_bp/
#   MGS3 HQ Ending            2 files  us/demo/_bp/m680_*x.sdt
AUDIO_PAYLOAD = {
    "us/demo/m010_050_p030.sdt": b"audio-data",
    "us/vox/rm2s001_01.sdt": b"audio-data",
}


def build_audio_zip(path: Path, extra: dict[str, bytes] | None = None) -> Path:
    """A small, generic MGS-audio-shaped archive (role deliberately unclear)."""
    files = dict(AUDIO_PAYLOAD)
    if extra:
        files.update(extra)
    return build_zip(path, files)


def build_mgs3_base_zip(path: Path, n: int = 180) -> Path:
    """MGS3's main pack: many files, and only MGS3's folders."""
    files = {}
    for i in range(n):
        d = ("demo", "movie", "vox")[i % 3]
        files[f"us/{d}/clip{i:04d}.sdt"] = b"audio"
    return build_zip(path, files)


def build_mgs2_base_zip(path: Path, n: int = 180) -> Path:
    """MGS2's pack: identifiable by us/demo2/ and us/movievr/, MGS2-only."""
    files = {}
    for i in range(n):
        d = ("demo", "demo2", "movie", "movievr", "vox")[i % 5]
        files[f"us/{d}/clip{i:04d}.sdt"] = b"audio"
    return build_zip(path, files)


def build_mgs3_update_zip(path: Path) -> Path:
    """MGS3 Update 2.0: a tiny patch touching both cutscene and codec trees."""
    return build_zip(path, {
        "us/demo/_bp/m570_010_p010.sdt": b"a",
        "us/demo/_bp/v020_010_p0.sdt": b"a",
        "us/vox/_bp/rm2s151_01.sdt": b"a",
    })


def build_mgs3_hq_zip(path: Path) -> Path:
    """MGS3 HQ Ending: two files, ending scene (m680) cutscenes only."""
    return build_zip(path, {
        "us/demo/_bp/m680_050_04x.sdt": b"a",
        "us/demo/_bp/m680_060_05x.sdt": b"a",
    })


# Back-compat alias used by the transaction tests.
def build_base_audio_zip(path: Path, n: int = 180) -> Path:
    return build_mgs3_base_zip(path, n)


class FakeUI:
    """Scripts UI responses so the interactive flows can be unit-tested.

    Each queue is consumed in order; popping an empty queue raises IndexError,
    which is a useful signal that the flow asked for more input than expected.
    """
    kind = "term"

    def __init__(self, *, menu=None, checklist=None, yesno=None,
                 files=None, dirs=None):
        self._menu = list(menu or [])
        self._checklist = list(checklist or [])
        self._yesno = list(yesno or [])
        self._files = list(files or [])
        self._dirs = list(dirs or [])
        self.last_dir = Path.home()
        self.infos: list = []
        self.errors: list = []

    def menu(self, *a, **k):
        return self._menu.pop(0)

    def checklist(self, *a, **k):
        return self._checklist.pop(0)

    def yesno(self, *a, **k):
        return self._yesno.pop(0)

    def pick_archive_file(self, *a, **k):
        v = self._files.pop(0)
        if v:
            self.last_dir = Path(v).parent
        return v

    def pick_file(self, *a, **k):
        return self._files.pop(0)

    def pick_dir(self, *a, **k):
        return self._dirs.pop(0)

    def info(self, *a, **k):
        self.infos.append(a)

    def error(self, *a, **k):
        self.errors.append(a)

    def progress(self, title, log):
        # A real (terminal-mode) Progress, so main() can be driven end to end.
        return install.Progress("term", title, log)
