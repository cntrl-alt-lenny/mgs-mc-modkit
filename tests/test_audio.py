"""Better Audio: independent components, role validation, selection flow."""
from __future__ import annotations

from pathlib import Path

import install
from conftest import (FakeUI, build_audio_zip, build_base_audio_zip,
                      build_mgs2_base_zip, build_mgs3_base_zip,
                      build_mgs3_hq_zip, build_mgs3_update_zip, build_zip)


# Nexus-style names carry the mod-id/version the validator uses as evidence:
#   -<modid>-<major>-<minor>-<timestamp>
MGS3_BASE_NAME = "MGS3 Better Audio-4-1-0-1700000000.zip"
MGS3_UPDATE_NAME = "Update 2.0-4-2-0-1700000001.zip"
MGS3_HQ_NAME = "HQ Ending Cutscenes-4-1-0-1700000002.zip"
MGS3_AMBIG_NAME = "mgs3 audio-4-1-0-1700000003.zip"     # mod #4, small, no role tag
MGS2_BASE_NAME = "MGS2 Better Audio-3-2-0-1700000004.zip"


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
    assert "recommended" in items["mgs3:update"][0].lower()
    assert "optional" in items["mgs3:hq"][0].lower()
    # The HQ pause disclaimer moved into the dialog header (rows don't wrap).
    assert "pause" in install.AUDIO_CHECKLIST_TEXT.lower()
    assert "button press" in install.AUDIO_CHECKLIST_TEXT.lower()


def test_checklist_rows_fit_the_deck_screen():
    """kdialog rows don't wrap; long labels ellipsize or overflow 1280px."""
    for game_set in (["mgs2"], ["mgs3"], ["mgs2", "mgs3"]):
        for _tag, label, _d in install.build_audio_checklist(game_set):
            assert len(label) <= install.CHECKLIST_LABEL_MAX, label


def test_order_always_base_hq_update(tmp_path):
    b, h, u = (tmp_path / "b.zip", tmp_path / "h.zip", tmp_path / "u.zip")
    comps = install.order_audio_components(
        "mgs3", {"update": u, "hq": h, "base": b})
    assert [c["role"] for c in comps] == ["base", "hq", "update"]


def test_order_subsets(tmp_path):
    u = tmp_path / "u.zip"
    assert [c["role"] for c in
            install.order_audio_components("mgs3", {"update": u})] == ["update"]


# -- role classification / validation ---------------------------------------
def test_role_signatures_distinguished(tmp_path):
    """Roles are told apart by CONTENTS, matching the real archives."""
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    upd = build_mgs3_update_zip(tmp_path / MGS3_UPDATE_NAME)
    hq = build_mgs3_hq_zip(tmp_path / MGS3_HQ_NAME)

    assert install.validate_audio_for_role(base, "mgs3", "base")[0] == "ok"
    assert install.validate_audio_for_role(upd, "mgs3", "update")[0] == "ok"
    assert install.validate_audio_for_role(hq, "mgs3", "hq")[0] == "ok"
    # Every wrong pairing between the three is caught.
    assert install.validate_audio_for_role(base, "mgs3", "update")[0] == "mismatch"
    assert install.validate_audio_for_role(upd, "mgs3", "hq")[0] == "mismatch"
    assert install.validate_audio_for_role(hq, "mgs3", "update")[0] == "mismatch"


def test_renamed_files_are_recognised_by_contents(tmp_path):
    """A Google-Drive copy with the Nexus name lost still works: the payload
    itself identifies the game and the component."""
    for builder, role in ((build_mgs3_base_zip, "base"),
                          (build_mgs3_update_zip, "update"),
                          (build_mgs3_hq_zip, "hq")):
        p = builder(tmp_path / f"my copy {role}.zip")
        assert install.validate_audio_for_role(p, "mgs3", role)[0] == "ok", role
    p = build_mgs2_base_zip(tmp_path / "audio backup final.zip")
    assert install.validate_audio_for_role(p, "mgs2", "base")[0] == "ok"


def test_renamed_mgs2_still_rejected_for_mgs3(tmp_path):
    """The danger case: a renamed MGS2 pack offered as MGS3's. Its contents
    give it away (us/demo2 and us/movievr are MGS2-only), so no name needed."""
    renamed_mgs2 = build_mgs2_base_zip(tmp_path / "audio-backup.zip")
    verdict, msg = install.validate_audio_for_role(renamed_mgs2, "mgs3", "base")
    assert verdict == "wrong_game"
    assert "MGS2" in msg


def test_ambiguous_when_component_unprovable(tmp_path):
    """A small patch that matches no known signature is not guessed at."""
    amb = build_zip(tmp_path / MGS3_AMBIG_NAME,
                    {"us/movie/something.sdt": b"a"})   # right game, odd shape
    assert install.validate_audio_for_role(amb, "mgs3", "update")[0] == "ambiguous"
    assert install.validate_audio_for_role(amb, "mgs3", "hq")[0] == "ambiguous"


def test_wrong_game_rejected(tmp_path):
    p = build_audio_zip(tmp_path / MGS2_BASE_NAME)      # mod #3 = MGS2
    assert install.validate_audio_for_role(p, "mgs3", "base")[0] == "wrong_game"


def test_non_audio_rejected(tmp_path):
    p = build_zip(tmp_path / "notes.zip", {"readme.txt": b"hi"})
    assert install.validate_audio_for_role(p, "mgs3", "base")[0] == "not_audio"


def test_mgs2_identified_by_name_or_by_contents(tmp_path):
    # By Nexus id in the name...
    good = build_audio_zip(tmp_path / MGS2_BASE_NAME)
    assert install.validate_audio_for_role(good, "mgs2", "base")[0] == "ok"
    # ...or by its MGS2-only folders when renamed.
    assert install.validate_audio_for_role(
        build_mgs2_base_zip(tmp_path / "renamed.zip"), "mgs2", "base")[0] == "ok"
    # Neither -> ask, never a silent pass.
    assert install.validate_audio_for_role(
        build_audio_zip(tmp_path / "mystery.zip"),
        "mgs2", "base")[0] == "missing_identity"


# -- interactive picker: hardened wrong-file handling -----------------------
def test_not_audio_rejected_outright(tmp_path):
    bad = build_zip(tmp_path / "notes.zip", {"x.txt": b"no"})
    # No yesno is scripted: if the flow offered "use anyway?" it would IndexError.
    ui = FakeUI(menu=["skip"], files=[str(bad)])
    assert install.request_audio_archive(ui, "mgs3", "base", {}) is None
    assert ui.infos                                     # told it was rejected


def test_wrong_game_rejected_outright(tmp_path):
    p = build_audio_zip(tmp_path / MGS2_BASE_NAME)      # mod #3, offered to MGS3
    ui = FakeUI(menu=["skip"], files=[str(p)])
    assert install.request_audio_archive(ui, "mgs3", "base", {}) is None
    assert ui.infos


def test_missing_identity_requires_confirmation(tmp_path):
    renamed = build_audio_zip(tmp_path / "renamed.zip")   # too little to prove
    ui = FakeUI(files=[str(renamed)], yesno=[True])       # picker opens first
    assert install.request_audio_archive(
        ui, "mgs3", "base", {}) == renamed.resolve()
    # Declining sends it back to the menu, then skip -> None.
    ui2 = FakeUI(menu=["skip"], files=[str(renamed)], yesno=[False])
    assert install.request_audio_archive(ui2, "mgs3", "base", {}) is None


def test_cancel_file_pick_no_nexus_nag(monkeypatch):
    calls = []
    monkeypatch.setattr(install, "open_url", lambda u: calls.append(u) or True)
    ui = FakeUI(menu=["skip"], files=[None])             # cancel the picker
    assert install.request_audio_archive(ui, "mgs3", "base", {}) is None
    assert calls == []                                   # Nexus never opened


def test_same_archive_two_roles_rejected(tmp_path):
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    chosen = {str(base.resolve()): ("mgs3", "base")}
    ui = FakeUI(menu=["skip"], files=[str(base)])
    assert install.request_audio_archive(ui, "mgs3", "update", chosen) is None
    assert ui.infos                                 # told it's already in use


# -- full collection: independence ------------------------------------------
def test_collect_base_only(tmp_path):
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    ui = FakeUI(checklist=[["mgs3:base"]], files=[str(base)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base"]


def test_collect_update_only(tmp_path):
    upd = build_mgs3_update_zip(tmp_path / MGS3_UPDATE_NAME)
    ui = FakeUI(checklist=[["mgs3:update"]], files=[str(upd)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["update"]


def test_collect_hq_only(tmp_path):
    hq = build_mgs3_hq_zip(tmp_path / MGS3_HQ_NAME)
    ui = FakeUI(checklist=[["mgs3:hq"]], files=[str(hq)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["hq"]


def test_collect_only_checked_request_files(tmp_path):
    upd = build_mgs3_update_zip(tmp_path / MGS3_UPDATE_NAME)
    ui = FakeUI(checklist=[["mgs3:update"]], files=[str(upd)])
    install.collect_audio_archives(ui, ["mgs3"])
    assert ui._menu == [] and ui._files == []           # exactly one request


def test_collect_all_ordered(tmp_path):
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    hq = build_mgs3_hq_zip(tmp_path / MGS3_HQ_NAME)
    upd = build_mgs3_update_zip(tmp_path / MGS3_UPDATE_NAME)
    ui = FakeUI(checklist=[["mgs3:base", "mgs3:hq", "mgs3:update"]],
                files=[str(base), str(hq), str(upd)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base", "hq", "update"]


def test_collect_cancel_asks_once_then_skips():
    """A mis-tap must not silently discard the recommended audio packs."""
    ui = FakeUI(checklist=[None], yesno=[True])          # cancel -> confirm skip
    assert install.collect_audio_archives(ui, ["mgs2", "mgs3"]) == {}
    assert ui._yesno == []                               # the confirm was shown


def test_collect_cancel_can_go_back(tmp_path):
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    # cancel -> "No, go back" -> checklist again -> pick base -> file
    ui = FakeUI(checklist=[None, ["mgs3:base"]], yesno=[False],
                files=[str(base)])
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base"]


def test_collect_deliberate_empty_needs_no_confirm():
    ui = FakeUI(checklist=[[]])                          # unticked everything
    assert install.collect_audio_archives(ui, ["mgs2", "mgs3"]) == {}
    # no yesno scripted: a deliberate empty selection is respected silently


def test_recommendation_note_base_without_update(tmp_path):
    audio = {"mgs3": install.order_audio_components(
        "mgs3", {"base": tmp_path / "b.zip"})}
    assert "update" in install.audio_recommendation_note(audio).lower()
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
    assert "MGS3 Better Audio update" in tx.mods
    assert "MGS3 Better Audio" not in tx.mods


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
    assert {"MGS3 Better Audio", "MGS3 HQ ending cutscenes",
            "MGS3 Better Audio update"} <= set(tx.mods)


def test_extraction_progress_reported(tmp_path):
    game_dir = tmp_path / "MGS3"
    game_dir.mkdir()
    comps = install.order_audio_components(
        "mgs3", {"base": build_base_audio_zip(tmp_path / "base.zip", n=200)})
    seen = []
    install.install_better_audio(
        tx=install.InstallTxn(game_dir, "mgs3", lambda m: None),
        components=comps, log=lambda m: None,
        report=lambda status, frac: seen.append(frac))
    assert seen                                 # progress was reported
    assert seen[-1] == 1.0                      # finishes at 100%
    assert all(0.0 <= f <= 1.0 for f in seen)


# -- naming clarity (user feedback: the old names were bizarre) --------------
def test_every_audio_name_says_which_game():
    """No user-facing audio label may be game-ambiguous like 'Base 2.0'."""
    for game, spec in install.AUDIO_SPECS.items():
        up = game.upper()
        for role, r in spec["roles"].items():
            for field in ("status", "checklist", "log"):
                assert up in r[field], (game, role, field, r[field])
            # ...and no bare version-soup names.
            assert r["status"] not in ("Base 1.0", "Base 2.0", "Update 2.0")
            assert r["nexus"]              # tells the user what to look for
            assert r["short"]              # short form for the summary


def test_summary_uses_short_names_under_a_game_heading(tmp_path):
    audio = {"mgs3": install.order_audio_components(
        "mgs3", {"base": tmp_path / "main.zip", "update": tmp_path / "upd.zip"})}
    text = install.audio_status_text(audio)
    assert "MGS3 audio" in text                       # game heading
    assert "main.zip" in text and "upd.zip" in text   # actual filenames shown
    assert "Base 1.0" not in text                     # no version soup


def test_one_dialog_per_file_on_the_happy_path(tmp_path):
    """Ticking the box is consent; the picker opens directly (no extra menu)."""
    base = build_mgs3_base_zip(tmp_path / MGS3_BASE_NAME)
    upd = build_mgs3_update_zip(tmp_path / MGS3_UPDATE_NAME)
    ui = FakeUI(checklist=[["mgs3:base", "mgs3:update"]],
                files=[str(base), str(upd)])          # NO menu entries needed
    audio = install.collect_audio_archives(ui, ["mgs3"])
    assert [c["role"] for c in audio["mgs3"]] == ["base", "update"]
    assert ui._files == []                            # both pickers consumed


# -- anchored payload matching ----------------------------------------------
def test_audio_match_is_anchored_not_substring():
    """'us/' must not match inside 'bonus/', and '.sdt' not mid-name."""
    assert install.entries_look_like_audio(["us/stage/a.sdt"])
    assert install.entries_look_like_audio(["mod/us/stage/a.bin"])
    assert install.entries_look_like_audio(["whatever/track.sdx"])
    assert install.entries_look_like_audio(["deep\\path\\clip.xxs"])   # windows sep
    # These previously passed on a bare-substring check:
    assert not install.entries_look_like_audio(["bonus/readme.txt"])
    assert not install.entries_look_like_audio([".sdt_notes/readme.txt"])
    assert not install.entries_look_like_audio(["docs/about.sdt.txt"])
    assert not install.entries_look_like_audio([])


def test_bonus_folder_archive_is_rejected(tmp_path):
    """End-to-end: an archive whose only hint is a 'bonus/' folder is not audio."""
    p = build_zip(tmp_path / "extras-4-1-0-1700000000.zip",
                  {"bonus/readme.txt": b"hi", "bonus/art.png": b"x"})
    assert install.validate_audio_for_role(p, "mgs3", "base")[0] == "not_audio"


# ---------------------------------------------------------------------------
# Signatures taken from the REAL NexusMods archives (inspected July 2026).
# These lock in the exact shapes so a refactor can't silently break detection.
#   MGS2 Full Version      3821 files  us/demo us/demo2 us/movie us/movievr us/vox
#   MGS3 main file         6053 files  us/demo us/movie us/vox
#   MGS3 Update 2.0           3 files  us/demo/_bp/ + us/vox/_bp/
#   MGS3 HQ Ending            2 files  us/demo/_bp/m680_*x.sdt
# ---------------------------------------------------------------------------
REAL_MGS2_BASE = ["us/demo/m01.sdt", "us/demo2/t01.sdt", "us/movie/mv.sdt",
                  "us/movievr/vr.sdt", "us/vox/v.sdt"] + [
    f"us/demo/f{i}.sdt" for i in range(200)]
REAL_MGS3_BASE = [f"us/{d}/f{i}.sdt"
                  for i, d in enumerate(("demo", "movie", "vox") * 70)]
REAL_MGS3_UPDATE = ["us/demo/_bp/m570_010_p010.sdt",
                    "us/demo/_bp/v020_010_p0.sdt",
                    "us/vox/_bp/rm2s151_01.sdt"]
REAL_MGS3_HQ = ["us/demo/_bp/m680_050_04x.sdt",
                "us/demo/_bp/m680_060_05x.sdt"]


def test_real_payloads_identify_their_game():
    assert install.audio_game_from_entries(REAL_MGS2_BASE) == "mgs2"
    assert install.audio_game_from_entries(REAL_MGS3_BASE) == "mgs3"
    # The patches are too small to prove a game; that's honest, not a failure.
    assert install.audio_game_from_entries(REAL_MGS3_UPDATE) is None
    assert install.audio_game_from_entries(REAL_MGS3_HQ) is None


def test_real_payloads_identify_their_role():
    def role(entries):
        return install.classify_mgs3_role(
            {"entries": entries, "file_count": len(entries), "size": 0,
             "version": None, "name": "x.zip"})
    assert role(REAL_MGS3_BASE) == ("base", True)
    assert role(REAL_MGS3_UPDATE) == ("update", True)
    assert role(REAL_MGS3_HQ) == ("hq", True)
    # An unrecognised patch is reported as unknown rather than guessed.
    assert role(["us/movie/odd.sdt"]) == (None, False)
