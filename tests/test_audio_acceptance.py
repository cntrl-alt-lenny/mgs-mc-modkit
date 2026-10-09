"""Selection identity through real collection, review, preparation and execution."""
from dataclasses import replace

import pytest

import install
from conftest import FakeUI, build_audio_zip, build_mgs2_base_zip
from test_install_plan import world, snapshot
from test_user_journey import _fake_world


@pytest.mark.parametrize("uncertain", [False, True])
@pytest.mark.parametrize("change_at", ["selection", "review", "settings", "reset", "prepared", None])
def test_selected_bytes_cannot_be_rebound_in_real_journey(
        tmp_path, monkeypatch, patch_download, uncertain, change_at):
    g1, g2, _ = _fake_world(tmp_path, monkeypatch, patch_download)
    found = install.find_games()
    before = snapshot(found)
    archive = tmp_path / "user-audio.zip"
    (build_audio_zip if uncertain else build_mgs2_base_zip)(archive)
    original = install.sha256_file(archive)

    def change():
        build_audio_zip(archive, {"us/vox/another.sdt": b"replacement"})
        assert install.sha256_file(archive) != original
        assert install.validate_audio_for_role(archive, "mgs2", "base")[0] == "missing_identity"

    class JourneyUI(FakeUI):
        def menu(self, title, body, items):
            if title == "Ready to install" and change_at in ("review", "reset"):
                change()
            if title == "Sound" and change_at == "settings":
                change()
            return super().menu(title, body, items)

    menu = ["go"]
    checklists = [["mgs1", "mgs2"], ["mgs2:base"]]
    if change_at == "settings":
        menu = ["opts", "Xbox One", "Stereo (2.0)", "go"]
        checklists.append([])
    elif change_at == "reset":
        menu = ["reset", "go"]
    ui = JourneyUI(menu=menu, checklist=checklists, files=[str(archive)],
                   yesno=[True] if uncertain else [])
    monkeypatch.setattr(install, "UI", lambda: ui)
    collect = install.collect_audio_archives

    def collection(*args):
        result = collect(*args)
        accepted = result["mgs2"][0]["acceptance"]
        assert (accepted.sha256, accepted.game, accepted.role, accepted.explicit) == (
            original, "mgs2", "base", uncertain)
        if change_at == "selection":
            change()
        return result

    monkeypatch.setattr(install, "collect_audio_archives", collection)
    prepare = install.prepare_plan

    def preparation(*args):
        result = prepare(*args)
        if change_at == "prepared":
            change()
        return result

    monkeypatch.setattr(install, "prepare_plan", preparation)
    assert install.main() == (0 if change_at is None else 1)
    assert ui._yesno == []  # unchanged acceptances never need executor confirmation
    if change_at is None:
        assert not ui.errors
        for key, game in (("mgs1", g1), ("mgs2", g2)):
            assert install.verify_install(install.GAMES[key], game) == []
        assert (g2 / ("us/demo/m010_050_p030.sdt" if uncertain else
                      "us/demo/clip0000.sdt")).is_file()
    else:
        assert ui.errors
        assert snapshot(found) == before  # every selected game stays untouched
        assert all(not (g / install.MODKIT_DIRNAME).exists() for g in (g1, g2))


@pytest.mark.parametrize("during", ["classification", "confirmation"])
def test_change_during_selection_is_not_accepted(tmp_path, monkeypatch, during):
    archive = build_audio_zip(tmp_path / "user-audio.zip")
    accepted = {}
    classify = install.validate_audio_for_role

    def change():
        build_audio_zip(archive, {"us/vox/replaced.sdt": b"new"})

    def classification(*args):
        result = classify(*args)
        if during == "classification":
            change()
        return result

    class ChangingUI(FakeUI):
        def yesno(self, *args):
            change()
            return super().yesno(*args)

    monkeypatch.setattr(install, "validate_audio_for_role", classification)
    ui = ChangingUI(files=[str(archive)], yesno=[True], menu=["skip"])
    assert install.request_audio_archive(ui, "mgs2", "base", {}, accepted) is None
    assert accepted == {}
    assert ui.infos


@pytest.mark.parametrize("change", ["absent", "game", "role", "confirmation", "digest", "classification"])
def test_plan_requires_exact_selection_acceptance(tmp_path, change):
    found, options = world(tmp_path)
    archive = build_audio_zip(tmp_path / "user-audio.zip")
    audio = install.collect_audio_archives(
        FakeUI(checklist=[["mgs2:base"]], files=[str(archive)], yesno=[True]), ["mgs2"])
    component = audio["mgs2"][0]
    if change == "absent":
        component.pop("acceptance")
    else:
        changes = {"game": {"game": "mgs3"}, "role": {"role": "hq"},
                   "confirmation": {"explicit": False}, "digest": {"sha256": "a" * 64},
                   "classification": {"classification": "wrong_game"}}
        component["acceptance"] = replace(component["acceptance"], **changes[change])
    before = snapshot(found)
    with pytest.raises(install.ReplanRequired, match="acceptance"):
        install.build_install_plan(found, options, audio)
    assert snapshot(found) == before


@pytest.mark.parametrize("classification,game,role,filename", [
    ("unknown_mod", "mgs2", "base", "audio-999-1-0-1739564749.zip"),
    ("ambiguous", "mgs3", "base", "user-audio.zip"),
    ("mismatch", "mgs3", "hq", "user-audio.zip"),
])
def test_unchanged_explicit_acceptance_survives_preparation(
        tmp_path, patch_download, classification, game, role, filename):
    from conftest import build_mgs3_update_zip
    found, options = world(tmp_path)
    archive = (build_mgs3_update_zip if classification == "mismatch" else
               build_audio_zip)(tmp_path / filename)
    if classification == "ambiguous":
        from conftest import build_zip
        build_zip(archive, {"us/demo/_bp/m570_patch.sdt": b"audio"})
    assert install.validate_audio_for_role(archive, game, role)[0] == classification
    ui = FakeUI(checklist=[[f"{game}:{role}"]], files=[str(archive)], yesno=[True])
    audio = install.collect_audio_archives(ui, [game])
    plan = install.build_install_plan(found, options, audio)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    adapter = install.CurrentRecipeAdapter(lambda _: None)
    prepared = install.prepare_plan(plan, adapter, workspace)
    outcomes = dict.fromkeys(found, "not started")
    install.execute_plan(prepared, adapter, outcomes)
    assert set(outcomes.values()) == {"installed and verified"}
    assert ui._yesno == []
