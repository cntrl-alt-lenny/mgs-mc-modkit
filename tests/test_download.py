"""Checksum enforcement in download()."""
from __future__ import annotations

import hashlib
import io

import pytest

import install

PAYLOAD = b"the quick brown fox" * 5000
GOOD = hashlib.sha256(PAYLOAD).hexdigest()


class FakeResp:
    def __init__(self, data: bytes):
        self.buf = io.BytesIO(data)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self.buf.read(n)


@pytest.fixture
def fake_net(monkeypatch):
    monkeypatch.setattr(install.urllib.request, "urlopen",
                        lambda req, timeout=0: FakeResp(PAYLOAD))


def test_good_checksum_passes(fake_net, tmp_path):
    dest = tmp_path / "a.zip"
    install.download("http://x/a.zip", dest, lambda m: None, sha256=GOOD)
    assert dest.read_bytes() == PAYLOAD


def test_bad_checksum_raises_and_deletes(fake_net, tmp_path):
    dest = tmp_path / "a.zip"
    with pytest.raises(RuntimeError, match="didn't arrive intact"):
        install.download("http://x/a.zip", dest, lambda m: None,
                         sha256="00" * 32)
    assert not dest.exists()          # partial file cleaned up


def test_no_checksum_skips_verification(fake_net, tmp_path):
    dest = tmp_path / "a.zip"
    install.download("http://x/a.zip", dest, lambda m: None, sha256=None)
    assert dest.read_bytes() == PAYLOAD


def test_empty_download_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(install.urllib.request, "urlopen",
                        lambda req, timeout=0: FakeResp(b""))
    dest = tmp_path / "a.zip"
    with pytest.raises(RuntimeError, match="arrived empty"):
        install.download("http://x/a.zip", dest, lambda m: None)
    assert not dest.exists()


def test_pinned_hashes_are_lowercase_hex():
    for h in (install.HDFIX_SHA256, install.M2FIX_SHA256,
              install.GAMES["mgs2"]["bugfix_sha256"],
              install.GAMES["mgs3"]["bugfix_sha256"]):
        assert len(h) == 64
        assert h == h.lower()
        int(h, 16)                    # valid hex


def test_checksum_error_keeps_digests_out_of_the_message(fake_net, tmp_path):
    """A tired user shouldn't be shown two 64-char hashes; the log gets them."""
    import pytest
    logs = []
    dest = tmp_path / "a.zip"
    with pytest.raises(RuntimeError) as ei:
        install.download("http://x/a.zip", dest, logs.append, sha256="00" * 32)
    msg = str(ei.value)
    assert "00" * 32 not in msg                  # no digest in the dialog text
    assert "run the installer again" in msg      # tells them what to do
    assert any("00" * 32 in m for m in logs)     # but it IS in the log
