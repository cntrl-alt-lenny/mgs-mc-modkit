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
# probe_audio_archive() accepts an archive if it contains a us/ folder or any
# .sdt/.sdx/.xxs file — mimic that real payload shape.
AUDIO_PAYLOAD = {
    "us/stage/demo.sdt": b"audio-data",
    "us/sound/vox.sdx": b"audio-data",
}


def build_audio_zip(path: Path, extra: dict[str, bytes] | None = None) -> Path:
    files = dict(AUDIO_PAYLOAD)
    if extra:
        files.update(extra)
    return build_zip(path, files)


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
