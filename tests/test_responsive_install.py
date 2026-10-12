"""Worker/UI ownership, cancellation, transfer retries and truthful results."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import threading
import urllib.error

import pytest

import install
from conftest import FakeUI
from test_user_journey import _fake_world

REAL_NOTICE = install.kit_update_notice


def test_worker_keeps_ui_on_owner_thread_and_cancellation_rolls_back(game_dir, monkeypatch):
    owner = threading.get_ident()
    (game_dir / "payload").write_bytes(b"before")
    event = threading.Event()
    ready = threading.Event()
    monkeypatch.setattr(install, "CANCEL_EVENT", event)

    class Progress:
        cancel_event = event

        def pump(self):
            assert threading.get_ident() == owner
            if ready.is_set():
                event.set()

    def operation():
        assert threading.get_ident() != owner
        tx = install.InstallTxn(game_dir, "mgs2", lambda m: None)
        try:
            tx.write_bytes("payload", b"after")
            ready.set()
            event.wait(2)
            install.check_cancelled()
        except install.CancelledInstall:
            assert tx.rollback()
            raise

    with pytest.raises(install.CancelledInstall):
        install.run_with_progress(Progress(), operation)
    assert (game_dir / "payload").read_bytes() == b"before"


def test_cancel_silent_archive_process(monkeypatch):
    event = threading.Event()
    monkeypatch.setattr(install, "CANCEL_EVENT", event)
    timer = threading.Timer(0.1, event.set)
    timer.start()
    try:
        with pytest.raises(install.CancelledInstall):
            install.archive_command([sys.executable, "-c", "import time;time.sleep(30)"])
    finally:
        timer.cancel()


def test_extraction_progress_arrives_before_completion():
    reports = []
    command = "import sys,time; print('x first',file=sys.stderr,flush=True); time.sleep(.35); print('x second',file=sys.stderr,flush=True)"
    install.archive_command([sys.executable, "-c", command], on_progress=reports.append, total=2)
    assert any(0 < value < 1 for value in reports)
    assert reports[-1] == 1


def test_download_retries_transient_error_and_reports_bytes(tmp_path, monkeypatch):
    calls, reports = [], []
    payload = b"verified payload"

    def open_url(*args, **kw):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.URLError("temporary outage")
        stream = io.BytesIO(payload)
        stream.headers = {"Content-Length": str(len(payload))}
        return stream

    monkeypatch.setattr(install.urllib.request, "urlopen", open_url)
    monkeypatch.setattr(install.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(install, "TRANSFER_PROGRESS", lambda *args: reports.append(args))
    dest = tmp_path / "download.zip"
    install.download("https://example.test/mod.zip", dest, lambda m: None,
                     hashlib.sha256(payload).hexdigest())
    assert len(calls) == 2 and dest.read_bytes() == payload
    assert reports[-1] == ("mod.zip", len(payload), len(payload))


def test_bad_checksum_is_not_retried(tmp_path, monkeypatch):
    calls = []

    def open_url(*args, **kw):
        calls.append(1)
        return io.BytesIO(b"wrong")

    monkeypatch.setattr(install.urllib.request, "urlopen", open_url)
    dest = tmp_path / "download.zip"
    with pytest.raises(RuntimeError, match="intact"):
        install.download("https://example.test/mod.zip", dest, lambda m: None, "0" * 64)
    assert len(calls) == 1 and not dest.exists()


def test_partial_install_reports_each_game(tmp_path, monkeypatch, patch_download):
    g1, g2, desk = _fake_world(tmp_path, monkeypatch, patch_download)
    ui = FakeUI(checklist=[["mgs1", "mgs2"], []], menu=["go"])
    monkeypatch.setattr(install, "UI", lambda: ui)

    real_archive = install.InstallTxn.install_archive

    def broken(tx, archive, *args, **kw):
        if tx.game_key == "mgs2":
            raise RuntimeError("bugfix unavailable")
        return real_archive(tx, archive, *args, **kw)

    monkeypatch.setattr(install.InstallTxn, "install_archive", broken)
    assert install.main() == 1
    message = str(ui.errors[-1])
    assert "MGS1: installed and verified" in message
    assert "MGS2: previous setup restored" in message
    assert "Diagnostic log:" in message
    assert (g1 / "MGSM2Fix64.asi").exists()
    assert (g2 / "winhttp.dll").read_bytes() == b"TRUE-STOCK"
    assert not ui.infos
    logs = list((install.app_data_dir() / "logs").glob("*.log"))
    assert "bugfix unavailable" in logs[0].read_text()


def test_summary_includes_mgs1_launcher_choice(tmp_path, monkeypatch, patch_download):
    g1, _, _ = _fake_world(tmp_path, monkeypatch, patch_download)
    monkeypatch.setattr(install, "find_games", lambda: {"mgs1": (g1, tmp_path)})
    captured = []

    class UI(FakeUI):
        def menu(self, title, body, *args):
            captured.append(body)
            return "cancel"

    monkeypatch.setattr(install, "UI", lambda: UI())
    assert install.main() == 0
    assert "MGS1: Boot straight in: yes" in captured[0]


def test_update_notice_is_cached_advisory_and_never_executes(tmp_path, monkeypatch):
    calls = []

    def open_url(*a, **kw):
        calls.append(kw)
        return io.BytesIO(json.dumps({"tag_name": "v99.0.0", "draft": False,
                                     "prerelease": False}).encode())

    monkeypatch.setattr(install.urllib.request, "urlopen", open_url)
    before = install.MODKIT_VERSION
    assert "newer kit (v99.0.0)" in REAL_NOTICE(lambda m: None)
    assert "newer kit (v99.0.0)" in REAL_NOTICE(lambda m: None)
    assert len(calls) == 1 and calls[0]["timeout"] == 3
    assert install.MODKIT_VERSION == before


def test_update_notice_network_error_does_not_block(monkeypatch):
    def error(*args, **kw):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(install.urllib.request, "urlopen", error)
    assert REAL_NOTICE(lambda m: None) == ""


def test_archive_timeout_is_bounded():
    with pytest.raises(RuntimeError, match="too long"):
        install.archive_command([sys.executable, "-c", "import time;time.sleep(10)"], timeout=0.05)


def test_uninstall_warning_reaches_dialog(tmp_path, monkeypatch, patch_download):
    g1, g2, _ = _fake_world(tmp_path, monkeypatch, patch_download)
    monkeypatch.setattr(install, "find_games", lambda: {"mgs2": (g2, tmp_path)})
    (g2 / install.MODKIT_DIRNAME).mkdir()
    monkeypatch.setattr(install, "uninstall_game", lambda *a: (
        ["Run Steam → Verify integrity to restore large originals"], False))
    ui = FakeUI(yesno=[True])
    assert install.run_uninstall(ui, lambda m: None) == 1
    assert "Verify integrity" in str(ui.errors[-1]) and not ui.infos
