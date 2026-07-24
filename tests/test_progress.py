"""Progress window — exercises the KDialog/D-Bus path, not just the terminal.

The real dialog needs a Deck/KDE session to render, but its command
construction and defensive fallback are unit-testable by faking `which` and
`subprocess.run`.
"""
from __future__ import annotations

import subprocess

import install


class FakeRun:
    """Records subprocess.run calls; fakes kdialog's D-Bus handle output."""
    def __init__(self, raise_on_qdbus=False):
        self.calls = []
        self.raise_on_qdbus = raise_on_qdbus

    def __call__(self, args, **kw):
        self.calls.append(list(args))
        if self.raise_on_qdbus and "qdbus" in args[0]:
            raise OSError("dbus down")

        class R:
            returncode = 0
            stdout = ""
        r = R()
        if args and "kdialog" in args[0]:
            r.stdout = "org.kde.kdialog-1234 /ProgressDialog\n"
        return r

    def qdbus_calls(self):
        return [c for c in self.calls if "qdbus" in c[0]]


def _fake_which(present):
    return lambda name: (f"/usr/bin/{name}" if name in present else None)


def test_kdialog_progress_drives_dbus(monkeypatch):
    fake = FakeRun()
    monkeypatch.setattr(install.shutil, "which",
                        _fake_which({"kdialog", "qdbus"}))
    monkeypatch.setattr(install.subprocess, "run", fake)

    p = install.Progress("kdialog", "Installing", lambda m: None)
    assert p._backend == "kdialog"
    assert p._dbus == ("org.kde.kdialog-1234", "/ProgressDialog")

    p.update("Extracting Base audio", 42)
    p.close()

    joined = [" ".join(map(str, c)) for c in fake.qdbus_calls()]
    assert any("setLabelText" in s and "Extracting Base audio" in s for s in joined)
    assert any("value" in s and "42" in s for s in joined)
    assert any(s.endswith("close") for s in joined)


def test_kdialog_without_qdbus_falls_back_to_term(monkeypatch):
    fake = FakeRun()
    monkeypatch.setattr(install.shutil, "which", _fake_which({"kdialog"}))
    monkeypatch.setattr(install.subprocess, "run", fake)

    logs = []
    p = install.Progress("kdialog", "Installing", logs.append)
    assert p._backend == "term"           # no qdbus -> no GUI progressbar
    p.update("Extracting", 50)            # still logs
    p.close()
    assert any("50%" in m for m in logs)
    assert fake.qdbus_calls() == []


def test_kdialog_dbus_failure_degrades_without_crashing(monkeypatch):
    fake = FakeRun(raise_on_qdbus=True)
    monkeypatch.setattr(install.shutil, "which",
                        _fake_which({"kdialog", "qdbus"}))
    monkeypatch.setattr(install.subprocess, "run", fake)

    logs = []
    p = install.Progress("kdialog", "Installing", logs.append)
    assert p._backend == "kdialog"
    p.update("Extracting", 30)            # first qdbus call raises -> degrade
    assert p._backend == "term"           # degraded, did not raise
    p.close()                             # safe after degrade
    assert any("30%" in m for m in logs)


def test_zenity_progress_pipe(monkeypatch):
    class FakePopen:
        def __init__(self, *a, **k):
            import io
            self.stdin = io.StringIO()
            self.returncode = 0

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(install.shutil, "which", _fake_which({"zenity"}))
    monkeypatch.setattr(install.subprocess, "Popen", FakePopen)
    p = install.Progress("zenity", "Installing", lambda m: None)
    assert p._backend == "zenity"
    p.update("Extracting", 60)
    written = p._proc.stdin.getvalue()
    assert "60" in written and "# Extracting" in written
    p.close()
