"""Better Audio component model, validation, and interactive selection."""
from __future__ import annotations

from pathlib import Path

import install
from conftest import FakeUI, build_audio_zip, build_zip


# -- pure component logic ---------------------------------------------------
def test_mgs3_incomplete_without_update(tmp_path):
    base = build_audio_zip(tmp_path / "base.zip")
    ok, missing = install.audio_selection_complete("mgs3", {"base": base})
    assert ok is False
    assert missing == ["Required Update 2.0"]

    upd = build_audio_zip(tmp_path / "upd.zip")
    ok2, missing2 = install.audio_selection_complete(
        "mgs3", {"base": base, "update": upd})
    assert ok2 is True
    assert missing2 == []


def test_mgs2_complete_with_base_only(tmp_path):
    base = build_audio_zip(tmp_path / "base.zip")
    ok, missing = install.audio_selection_complete("mgs2", {"base": base})
    assert ok is True and missing == []


def test_order_base_update_update_last(tmp_path):
    b, u = tmp_path / "b.zip", tmp_path / "u.zip"
    comps = install.order_audio_components("mgs3", {"base": b, "update": u})
    assert [c["role"] for c in comps] == ["base", "update"]


def test_order_base_hq_update_update_last(tmp_path):
    b, h, u = tmp_path / "b.zip", tmp_path / "h.zip", tmp_path / "u.zip"
    comps = install.order_audio_components(
        "mgs3", {"update": u, "hq": h, "base": b})   # provided out of order
    assert [c["role"] for c in comps] == ["base", "hq", "update"]  # update last


def test_hq_ending_always_offered_in_checklist():
    items = install.build_audio_checklist(["mgs3"])
    tags = {t for t, _, _ in items}
    assert "mgs3:base" in tags
    assert "mgs3:hq" in tags                       # offered regardless of detection
    hq = next(i for i in items if i[0] == "mgs3:hq")
    assert hq[2] is False                          # default off
    assert "pause" in hq[1].lower()                # carries the author's warning


def test_checklist_only_relevant_games():
    assert {t for t, _, _ in install.build_audio_checklist(["mgs2"])} == {
        "mgs2:base"}
    assert install.build_audio_checklist([]) == []


# -- validation (arbitrary dirs, renamed files, wrong game) -----------------
def test_validate_renamed_archive_in_arbitrary_dir(tmp_path):
    weird = tmp_path / "somewhere" / "else"
    weird.mkdir(parents=True)
    p = build_audio_zip(weird / "my-backup-copy.zip")   # no Nexus suffix
    ok, reason = install.validate_audio_archive(p, expect_modid=4)
    assert ok is True, reason


def test_validate_wrong_game_rejected(tmp_path):
    # Filename modid says mod #3 (MGS2), but we expect #4 (MGS3).
    p = build_audio_zip(tmp_path / "audio-3-2-0-1700000000.zip")
    ok, reason = install.validate_audio_archive(p, expect_modid=4)
    assert ok is False
    assert "wrong game" in reason


def test_validate_non_audio_rejected(tmp_path):
    p = build_zip(tmp_path / "notes.zip", {"readme.txt": b"hi"})
    ok, reason = install.validate_audio_archive(p, expect_modid=4)
    assert ok is False
    assert "MGS audio" in reason


# -- interactive picker -----------------------------------------------------
def test_decline_nexus_does_not_repeat(monkeypatch):
    calls = []
    monkeypatch.setattr(install, "open_url", lambda u: calls.append(u) or True)
    ui = FakeUI(menu=["nexus", "skip"])          # open Nexus once, then skip
    role = install.AUDIO_SPECS["mgs3"]["roles"]["base"]
    result = install.request_audio_archive(ui, role, "http://nexus", 4)
    assert result is None
    assert len(calls) == 1                        # opened exactly once, no loop


def test_picker_returns_validated_file(tmp_path):
    p = build_audio_zip(tmp_path / "a.zip")
    ui = FakeUI(menu=["select"], files=[str(p)])
    role = install.AUDIO_SPECS["mgs3"]["roles"]["base"]
    got = install.request_audio_archive(ui, role, "http://nexus", 4)
    assert got == p
    assert ui.last_dir == tmp_path                # remembers the folder


def test_picker_invalid_then_override(tmp_path):
    bad = build_zip(tmp_path / "bad.zip", {"x.txt": b"no"})
    ui = FakeUI(menu=["select"], files=[str(bad)], yesno=[True])
    role = install.AUDIO_SPECS["mgs3"]["roles"]["base"]
    got = install.request_audio_archive(ui, role, "http://nexus", 4)
    assert got == bad                             # user chose "use it anyway"


# -- full collection: MGS3 completeness enforcement -------------------------
def test_collect_mgs3_dropped_without_update(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "open_url", lambda u: True)
    base = build_audio_zip(tmp_path / "base.zip")
    # checklist picks base; base selected; update SKIPPED; required-loop -> drop
    ui = FakeUI(checklist=[["mgs3:base"]],
                menu=["select", "skip", "drop"],
                files=[str(base)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert "mgs3" not in audio                     # never installed base-only


def test_collect_mgs3_complete_ordered(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "open_url", lambda u: True)
    base = build_audio_zip(tmp_path / "base.zip")
    upd = build_audio_zip(tmp_path / "update.zip")
    ui = FakeUI(checklist=[["mgs3:base"]],
                menu=["select", "select"],        # base, then update
                files=[str(base), str(upd)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base", "update"]


def test_collect_mgs3_with_hq_ordered(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "open_url", lambda u: True)
    base = build_audio_zip(tmp_path / "base.zip")
    hq = build_audio_zip(tmp_path / "hq.zip")
    upd = build_audio_zip(tmp_path / "update.zip")
    ui = FakeUI(checklist=[["mgs3:base", "mgs3:hq"]],
                menu=["select", "select", "select"],   # base, hq, update
                files=[str(base), str(hq), str(upd)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base", "hq", "update"]


def test_collect_cancel_skips_all():
    ui = FakeUI(checklist=[None])                 # cancelled the checklist
    assert install.collect_audio_archives(ui, ["mgs2", "mgs3"]) == {}


# -- manifest records each component separately -----------------------------
def test_manifest_records_each_audio_component(tmp_path):
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    provided = {
        "base": build_audio_zip(tmp_path / "base.zip"),
        "hq": build_audio_zip(tmp_path / "hq.zip"),
        "update": build_audio_zip(tmp_path / "update.zip"),
    }
    comps = install.order_audio_components("mgs3", provided)
    tx = install.InstallTxn(game_dir, "mgs3", lambda m: None)
    install.install_better_audio(tx, comps, lambda m: None)
    tx.commit()
    keys = set(tx.mods)
    assert "Better Audio — Base 1.0" in keys
    assert "Better Audio — HQ Ending" in keys
    assert "Better Audio — Required Update 2.0" in keys
