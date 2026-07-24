"""Better Audio: independent components, role validation, selection flow."""
from __future__ import annotations

from pathlib import Path

import install
from conftest import (FakeUI, build_audio_zip, build_base_audio_zip,
                      build_zip)


# -- checklist / ordering ---------------------------------------------------
def test_checklist_four_independent_items():
    tags = [t for t, _, _ in install.build_audio_checklist(["mgs2", "mgs3"])]
    assert tags == ["mgs2:base", "mgs3:base", "mgs3:update", "mgs3:hq"]


def test_checklist_defaults_and_disclaimer():
    items = {t: (label, default)
             for t, label, default in install.build_audio_checklist(["mgs3"])}
    assert items["mgs3:base"][1] is True
    assert items["mgs3:update"][1] is True          # recommended, on by default
    assert items["mgs3:hq"][1] is False             # off by default
    assert "optional" in items["mgs3:update"][0].lower()
    assert "pause" in items["mgs3:hq"][0].lower()   # disclaimer present


def test_order_always_base_hq_update(tmp_path):
    b, h, u = (tmp_path / "b.zip", tmp_path / "h.zip", tmp_path / "u.zip")
    comps = install.order_audio_components(
        "mgs3", {"update": u, "hq": h, "base": b})
    assert [c["role"] for c in comps] == ["base", "hq", "update"]


def test_order_subsets(tmp_path):
    u = tmp_path / "u.zip"
    assert [c["role"] for c in
            install.order_audio_components("mgs3", {"update": u})] == ["update"]
    b, u = tmp_path / "b.zip", tmp_path / "u.zip"
    assert [c["role"] for c in
            install.order_audio_components("mgs3", {"base": b, "update": u})] \
        == ["base", "update"]


# -- role classification / validation ---------------------------------------
def test_role_signatures_distinguished(tmp_path):
    base = build_base_audio_zip(tmp_path / "base.zip")           # many files
    upd = build_audio_zip(tmp_path / "audio-4-2-0-1700000000.zip")  # v2 tag
    hq = build_audio_zip(tmp_path / "HQ Ending Cutscenes.zip")   # name hint

    assert install.validate_audio_for_role(base, "mgs3", "base")[0] == "ok"
    assert install.validate_audio_for_role(upd, "mgs3", "update")[0] == "ok"
    assert install.validate_audio_for_role(hq, "mgs3", "hq")[0] == "ok"
    # base offered as the update -> confidently a mismatch
    assert install.validate_audio_for_role(base, "mgs3", "update")[0] == "mismatch"


def test_renamed_base_still_identified(tmp_path):
    weird = tmp_path / "backups"
    weird.mkdir()
    renamed = build_base_audio_zip(weird / "my-drive-copy-final.zip")
    assert install.validate_audio_for_role(renamed, "mgs3", "base")[0] == "ok"


def test_ambiguous_when_unprovable(tmp_path):
    # Small, generic name, no v2 tag, no "ending" — role can't be proven.
    amb = build_audio_zip(tmp_path / "audio-files.zip")
    assert install.validate_audio_for_role(amb, "mgs3", "update")[0] == "ambiguous"
    assert install.validate_audio_for_role(amb, "mgs3", "hq")[0] == "ambiguous"


def test_wrong_game_rejected(tmp_path):
    p = build_audio_zip(tmp_path / "audio-3-2-0-1700000000.zip")   # mod #3 = MGS2
    verdict, _ = install.validate_audio_for_role(p, "mgs3", "base")
    assert verdict == "wrong_game"


def test_non_audio_rejected(tmp_path):
    p = build_zip(tmp_path / "notes.zip", {"readme.txt": b"hi"})
    assert install.validate_audio_for_role(p, "mgs3", "base")[0] == "not_audio"


def test_mgs2_single_role_always_ok(tmp_path):
    p = build_audio_zip(tmp_path / "audio.zip")
    assert install.validate_audio_for_role(p, "mgs2", "base")[0] == "ok"


# -- interactive picker -----------------------------------------------------
def test_ambiguous_requires_explicit_confirmation(tmp_path):
    amb = build_audio_zip(tmp_path / "audio-files.zip")
    # Decline the confirmation -> back to menu -> skip -> None
    ui = FakeUI(menu=["select", "skip"], files=[str(amb)], yesno=[False])
    assert install.request_audio_archive(ui, "mgs3", "update", {}) is None
    # Accept the confirmation -> returned
    ui2 = FakeUI(menu=["select"], files=[str(amb)], yesno=[True])
    assert install.request_audio_archive(ui2, "mgs3", "update", {}) == amb.resolve()


def test_cancel_file_pick_no_nexus_nag(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(install, "open_url", lambda u: calls.append(u) or True)
    # select -> cancel file dialog (None) -> back to menu -> skip
    ui = FakeUI(menu=["select", "skip"], files=[None])
    assert install.request_audio_archive(ui, "mgs3", "base", {}) is None
    assert calls == []                              # Nexus never opened


def test_same_archive_two_roles_rejected(tmp_path):
    base = build_base_audio_zip(tmp_path / "base.zip")
    chosen = {str(base.resolve()): ("mgs3", "base")}
    # Try to reuse it for the update role: info shown, back to menu, then skip.
    ui = FakeUI(menu=["select", "skip"], files=[str(base)])
    got = install.request_audio_archive(ui, "mgs3", "update", chosen)
    assert got is None
    assert ui.infos                                 # told it's already used


# -- full collection: independence ------------------------------------------
def test_collect_base_only(tmp_path):
    base = build_base_audio_zip(tmp_path / "base.zip")
    ui = FakeUI(checklist=[["mgs3:base"]], menu=["select"], files=[str(base)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base"]


def test_collect_update_only(tmp_path):
    upd = build_audio_zip(tmp_path / "audio-4-2-0-1700000000.zip")
    ui = FakeUI(checklist=[["mgs3:update"]], menu=["select"], files=[str(upd)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["update"]


def test_collect_hq_only(tmp_path):
    hq = build_audio_zip(tmp_path / "HQ Ending.zip")
    ui = FakeUI(checklist=[["mgs3:hq"]], menu=["select"], files=[str(hq)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["hq"]


def test_collect_only_checked_request_files(tmp_path):
    # Only update is checked, so only ONE file is requested. If the flow asked
    # for base/hq too, the files/menu queues would underflow (IndexError).
    upd = build_audio_zip(tmp_path / "audio-4-2-0-1700000000.zip")
    ui = FakeUI(checklist=[["mgs3:update"]], menu=["select"], files=[str(upd)])
    install.collect_audio_archives(ui, ["mgs3"])
    assert ui._menu == [] and ui._files == []       # exactly one request made


def test_collect_all_ordered(tmp_path):
    base = build_base_audio_zip(tmp_path / "base.zip")
    hq = build_audio_zip(tmp_path / "HQ Ending.zip")
    upd = build_audio_zip(tmp_path / "audio-4-2-0-1700000000.zip")
    ui = FakeUI(checklist=[["mgs3:base", "mgs3:hq", "mgs3:update"]],
                menu=["select", "select", "select"],
                files=[str(base), str(hq), str(upd)])   # requested base, hq, update
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base", "hq", "update"]


def test_collect_cancel_skips_all():
    ui = FakeUI(checklist=[None])
    assert install.collect_audio_archives(ui, ["mgs2", "mgs3"]) == {}


def test_recommendation_note_base_without_update(tmp_path):
    audio = {"mgs3": install.order_audio_components(
        "mgs3", {"base": tmp_path / "b.zip"})}
    assert "Update 2.0" in install.audio_recommendation_note(audio)
    audio2 = {"mgs3": install.order_audio_components(
        "mgs3", {"base": tmp_path / "b.zip", "update": tmp_path / "u.zip"})}
    assert install.audio_recommendation_note(audio2) == ""


# -- manifest records each independently-installed component -----------------
def test_manifest_update_only(tmp_path):
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    comps = install.order_audio_components(
        "mgs3", {"update": build_audio_zip(tmp_path / "u.zip")})
    tx = install.InstallTxn(game_dir, "mgs3", lambda m: None)
    install.install_better_audio(tx, comps, lambda m: None)
    tx.commit()
    assert "Better Audio — Update 2.0" in tx.mods
    assert "Better Audio — Base 1.0" not in tx.mods


def test_manifest_records_each_component(tmp_path):
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
    assert {"Better Audio — Base 1.0", "Better Audio — HQ Ending",
            "Better Audio — Update 2.0"} <= set(tx.mods)
