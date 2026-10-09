"""Offline preparation ordering, stale-input refusal and transaction replay."""
from dataclasses import replace
from pathlib import Path
import json
import threading
import subprocess
import sys

import pytest

import install
from conftest import build_zip, make_steam_root


def world(tmp_path):
    root = make_steam_root(tmp_path)
    found, options = {}, {}
    for key in ("mgs1", "mgs2", "mgs3"):
        game = tmp_path / key
        game.mkdir()
        (game / install.GAMES[key]["exe"]).write_bytes(b"licensed-executable-fixture")
        found[key] = (game, root)
        options[key] = dict(button_icons="Xbox One", audio_mode="Stereo (2.0)",
                            hq_movies=True, skip_launcher=True, skip_splash=True,
                            update_check=False, device="desktop", _changed=set())
    (found["mgs2"][0] / "winhttp.dll").write_bytes(b"stock")
    return found, options


def snapshot(found):
    return {key: {p.relative_to(game).as_posix(): p.read_bytes()
                  for p in game.rglob("*") if p.is_file()}
            for key, (game, _) in found.items()}


def prepared_world(tmp_path, patch_download):
    found, options = world(tmp_path)
    plan = install.build_install_plan(found, options, {})
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    adapter = install.CurrentRecipeAdapter(lambda _: None)
    prepared = install.prepare_plan(plan, adapter, workspace)
    return found, plan, adapter, prepared


def test_embedded_module_matches_source_and_standalone_compiles():
    root = Path(install.__file__).parent
    body = (root / "install.py").read_text()
    embedded = body.split('# BEGIN EMBEDDED INSTALL PLAN\n', 1)[1].split(
        '# END EMBEDDED INSTALL PLAN\n', 1)[0]
    assert embedded == (root / "install_plan.py").read_text()
    compile(body, "standalone-install.py", "exec")


@pytest.mark.parametrize("invalid", ["schema", "profile", "duplicate", "checksum", "incompatible"])
def test_invalid_plan_refused_before_preparation(tmp_path, invalid):
    found, options = world(tmp_path)
    plan = install.build_install_plan(found, options, {})
    if invalid == "schema":
        plan = replace(plan, schema=2)
    elif invalid == "profile":
        plan = replace(plan, profile="gameplay-mods")
    elif invalid == "duplicate":
        plan = replace(plan, games=(plan.games[0], plan.games[0]))
    elif invalid == "checksum":
        game = replace(plan.games[0], packages=(replace(plan.games[0].packages[0], sha256=""),))
        plan = replace(plan, games=(game,))
    else:
        plan = replace(plan, games=(replace(plan.games[0], incompatibilities=("conflict",)),))
    with pytest.raises(ValueError):
        plan.validate()


@pytest.mark.parametrize("failure", ["archive", "settings", "launcher", "path"])
def test_bad_last_game_does_not_mutate_earlier_games(
        tmp_path, monkeypatch, patch_download, mod_zips, failure):
    found, options = world(tmp_path)
    if failure == "archive":
        mod_zips["MGS3-Community-Bugfix"].write_bytes(b"not an archive")
    elif failure == "settings":
        options["mgs3"]["audio_mode"] = "invalid"
    elif failure == "launcher":
        path = found["mgs3"][0] / "mgs3_savedata_win/123/launcher/launcher_sv"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"broken")
    else:
        (found["mgs3"][0] / "plugins").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    before = snapshot(found)
    plan = install.build_install_plan(found, options, {})
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises((RuntimeError, ValueError, OSError, subprocess.SubprocessError)):
        install.prepare_plan(plan, install.CurrentRecipeAdapter(lambda _: None), workspace)
    assert snapshot(found) == before
    assert all(not (p / install.MODKIT_DIRNAME).exists() for p, _ in found.values())


@pytest.mark.parametrize("change", ["settings", "save", "record", "payload", "package", "recovery"])
def test_stale_inputs_refuse_all_game_writes(tmp_path, monkeypatch, patch_download, change):
    found, plan, adapter, prepared = prepared_world(tmp_path, patch_download)
    game = found["mgs3"][0]
    if change == "settings":
        (game / "MGSM2Fix.ini").write_bytes(b"changed")
    elif change == "save":
        path = game / "mgs3_savedata_win/123/launcher/launcher_sv"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"new launcher state")
    elif change in ("record", "recovery"):
        root = game / install.MODKIT_DIRNAME
        root.mkdir()
        name = install.JOURNAL_NAME if change == "recovery" else install.MANIFEST_NAME
        (root / name).write_bytes(b"changed record")
    elif change == "package":
        monkeypatch.setattr(install, "HDFIX_VERSION", "unexpected-change")
    else:
        Path(prepared.games[-1].identities[-1][0]).write_bytes(b"changed payload")
    before = snapshot(found)
    outcomes = dict.fromkeys(found, "not started")
    with pytest.raises(install.ReplanRequired):
        install.execute_plan(prepared, adapter, outcomes)
    assert snapshot(found) == before
    assert set(outcomes.values()) == {"not started"}


def test_archive_identity_and_audio_incompatibility(tmp_path):
    found, options = world(tmp_path)
    archive = build_zip(tmp_path / "audio.zip", {"us/demo/demo.sdt": b"audio"})
    components = install.order_audio_components("mgs3", {"base": archive})
    plan = install.build_install_plan(found, options, {"mgs3": components})
    archive.write_bytes(b"changed")
    with pytest.raises(install.ReplanRequired, match="archive changed"):
        install.CurrentRecipeAdapter(lambda _: None).recheck(plan)
    components = install.order_audio_components("mgs3", {"base": archive}) * 2
    with pytest.raises(ValueError, match="Incompatible"):
        install.build_install_plan(found, options, {"mgs3": components})


def test_space_is_aggregated_across_games_before_transactions(tmp_path, monkeypatch, patch_download):
    found, _, adapter, prepared = prepared_world(tmp_path, patch_download)
    required = install.SPACE_MARGIN_BYTES + sum(g.required_bytes for g in prepared.games)
    monkeypatch.setattr(install, "free_bytes", lambda _: required - 1)
    before = snapshot(found)
    with pytest.raises(RuntimeError, match="free space"):
        install.execute_plan(prepared, adapter, dict.fromkeys(found, "not started"))
    assert snapshot(found) == before


def test_concurrent_lock_refuses_before_any_game_write(tmp_path, patch_download):
    found, _, adapter, prepared = prepared_world(tmp_path, patch_download)
    before = snapshot(found)
    with install.GameLock(found["mgs3"][0]):
        with pytest.raises(RuntimeError, match="Another installer"):
            install.execute_plan(prepared, adapter, dict.fromkeys(found, "not started"))
    assert snapshot(found) == before
    # Locks acquired before the refusal are released.
    with install.GameLock(found["mgs1"][0]):
        pass


@pytest.mark.parametrize("failure", ["cancel", "write", "rollback"])
def test_execution_keeps_completed_restored_and_unstarted_separate(
        tmp_path, monkeypatch, patch_download, failure):
    found, _, adapter, prepared = prepared_world(tmp_path, patch_download)
    before = snapshot(found)
    real_archive = install.InstallTxn.install_archive

    def interrupt(tx, archive, **kwargs):
        result = real_archive(tx, archive, **kwargs)
        if tx.game_key == "mgs2":
            if failure == "cancel":
                raise install.CancelledInstall("cancel fixture")
            raise OSError("write fixture")
        return result

    monkeypatch.setattr(install.InstallTxn, "install_archive", interrupt)
    if failure == "rollback":
        monkeypatch.setattr(install.InstallTxn, "rollback", lambda _: False)
    outcomes = dict.fromkeys(found, "not started")
    with pytest.raises((OSError, install.CancelledInstall)):
        install.execute_plan(prepared, adapter, outcomes)
    assert outcomes["mgs1"] == "installed and verified"
    assert outcomes["mgs3"] == "not started"
    assert outcomes["mgs2"] == ("recovery incomplete; backups kept" if failure == "rollback"
                                 else "previous setup restored")
    if failure != "rollback":
        assert snapshot(found)["mgs2"] == before["mgs2"]
    assert snapshot(found)["mgs3"] == before["mgs3"]


def test_executor_has_no_download_picker_confirmation_or_recipe_calls(
        tmp_path, monkeypatch, patch_download):
    found, _, adapter, prepared = prepared_world(tmp_path, patch_download)

    def forbidden(*args, **kwargs):
        raise AssertionError("Executor attempted interaction or preparation")

    for name in ("UI", "download", "fetch", "install_hdfix", "install_bugfix",
                 "install_m2fix", "install_better_audio", "write_settings", "set_launcher_options"):
        monkeypatch.setattr(install, name, forbidden)
    outcomes = dict.fromkeys(found, "not started")
    install.execute_plan(prepared, adapter, outcomes)
    assert set(outcomes.values()) == {"installed and verified"}
    for key, (game, _) in found.items():
        assert install.verify_install(install.GAMES[key], game) == []


def test_prepared_repair_and_removal_keep_legacy_records(tmp_path, patch_download):
    found, _, adapter, prepared = prepared_world(tmp_path, patch_download)
    before = snapshot(found)
    install.execute_plan(prepared, adapter, dict.fromkeys(found, "not started"))
    # Existing schema-1 records remain readable; no new transaction schema.
    for game, _ in found.values():
        path = game / install.MODKIT_DIRNAME / install.MANIFEST_NAME
        body = json.loads(path.read_text())
        body["schema"] = 1
        body.pop("files", None)
        path.write_text(json.dumps(body))
    defaults = json.loads(prepared.plan.games[0].settings)
    options = {key: install.options_for_game(key, loc, defaults, lambda _: None)
               for key, loc in found.items()}
    plan = install.build_install_plan(found, options, {})
    workspace = tmp_path / "repair-workspace"
    workspace.mkdir()
    repair = install.prepare_plan(plan, adapter, workspace)
    install.execute_plan(repair, adapter, dict.fromkeys(found, "not started"))
    for game, _ in found.values():
        notes, ok = install.uninstall_game(game, lambda _: None)
        assert ok, notes
    assert snapshot(found) == before


def test_preparation_cancellation_is_zero_mutation(tmp_path, monkeypatch, patch_download):
    found, options = world(tmp_path)
    plan = install.build_install_plan(found, options, {})
    before = snapshot(found)
    cancel = threading.Event()
    cancel.set()
    monkeypatch.setattr(install, "CANCEL_EVENT", cancel)
    with pytest.raises(install.CancelledInstall):
        install.prepare_plan(plan, install.CurrentRecipeAdapter(lambda _: None), tmp_path)
    assert snapshot(found) == before


def test_standalone_import_and_engine_without_adjacent_module(tmp_path):
    source = Path(install.__file__).read_bytes()
    standalone = tmp_path / "install.py"
    standalone.write_bytes(source)
    result = subprocess.run([sys.executable, "-I", "-c", '''
import runpy, sys
m = runpy.run_path(sys.argv[1])
p = m['PlanPackage']('fixture', '1', 'local', 'a'*64)
g = m['PlanGame']('future-game', '/game', '/steam', '{}', (p,), 'snapshot')
m['InstallPlan']((g,)).validate()
assert 'install_plan' not in sys.modules
print('standalone plan works without source module')
''', str(standalone)], capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'standalone plan works without source module'
    assert not (tmp_path / 'install_plan.py').exists()


def test_sync_check_is_nonwriting_and_bad_markers_fail(tmp_path):
    root = Path(install.__file__).parent
    (tmp_path / 'tools').mkdir()
    tool = tmp_path / 'tools/embed_install_plan.py'
    tool.write_bytes((root / 'tools/embed_install_plan.py').read_bytes())
    source = tmp_path / 'install.py'
    source.write_bytes((root / 'install.py').read_bytes())
    (tmp_path / 'install_plan.py').write_bytes((root / 'install_plan.py').read_bytes())
    before = source.read_bytes(), source.stat().st_mtime_ns
    result = subprocess.run([sys.executable, str(tool), '--check'], capture_output=True)
    assert result.returncode == 0
    assert (source.read_bytes(), source.stat().st_mtime_ns) == before
    for body in (b'no markers', source.read_bytes() + b'# END EMBEDDED INSTALL PLAN\n'):
        source.write_bytes(body)
        for args in ([], ['--check']):
            result = subprocess.run([sys.executable, str(tool), *args], capture_output=True)
            assert result.returncode != 0
            assert source.read_bytes() == body


def test_corrupt_last_record_is_rejected_during_preparation(tmp_path, patch_download):
    found, options = world(tmp_path)
    record = found['mgs3'][0] / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    record.parent.mkdir()
    record.write_text('{bad record')
    before = snapshot(found)
    plan = install.build_install_plan(found, options, {})
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    with pytest.raises(install.CorruptManifestError):
        install.prepare_plan(plan, install.CurrentRecipeAdapter(lambda _: None), workspace)
    assert snapshot(found) == before


def test_preparation_never_constructs_live_transaction(tmp_path, monkeypatch, patch_download):
    found, options = world(tmp_path)
    plan = install.build_install_plan(found, options, {})
    before = snapshot(found)

    def forbidden(*args, **kwargs):
        raise AssertionError('Preparation constructed a live transaction')

    monkeypatch.setattr(install, 'InstallTxn', forbidden)
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    install.prepare_plan(plan, install.CurrentRecipeAdapter(lambda _: None), workspace)
    assert snapshot(found) == before
