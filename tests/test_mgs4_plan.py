"""Combined MGS1–4 lifecycle: preparation refusal and protected replay."""
from dataclasses import replace
from pathlib import Path
import json
import threading

import pytest

import install
from conftest import build_zip
from test_install_plan import world, snapshot
from test_patriot import game, opts


def combined(tmp_path):
    found, options = world(tmp_path)
    root = game(tmp_path / 'mgs4')
    found['mgs4'] = (root, found['mgs1'][1])
    options['mgs4'] = opts(root)
    return found, options


def prepare(tmp_path, found, options, name='workspace'):
    plan = install.build_install_plan(found, options, {})
    directory = tmp_path / name
    directory.mkdir()
    adapter = install.CurrentRecipeAdapter(lambda _: None)
    return adapter, install.prepare_plan(plan, adapter, directory)


@pytest.mark.parametrize('failure', ['payload', 'settings', 'loader', 'duplicate', 'record', 'orphan', 'layout'])
def test_late_mgs4_preparation_failure_never_opens_any_transaction(
        tmp_path, monkeypatch, patch_download, mod_zips, failure):
    found, options = combined(tmp_path)
    root = found['mgs4'][0]
    if failure == 'payload':
        build_zip(mod_zips['MGSPatriotFix'], {'MGS4/winmm.dll': b'incomplete'})
        monkeypatch.setattr(install, 'PATRIOT_SHA256', install.sha256_file(mod_zips['MGSPatriotFix']))
    elif failure == 'settings':
        options['mgs4']['patriot_filtering'] = 0
    elif failure == 'loader':
        (root / 'MGS4/winmm.dll').write_bytes(b'unowned loader')
    elif failure == 'duplicate':
        (root / 'Launcher/MGSPatriotFix.asi').write_bytes(b'wrong location')
    elif failure in ('record', 'orphan'):
        recovery = root / install.MODKIT_DIRNAME
        recovery.mkdir()
        if failure == 'record':
            (recovery / install.MANIFEST_NAME).write_text('{malformed')
        else:
            backup = recovery / 'backups/mgs4_savedata_win/save.dat'
            backup.parent.mkdir(parents=True)
            backup.write_bytes(b'unowned save backup')
    else:
        (root / 'Launcher/launcher.exe').unlink()
    before = snapshot(found)

    def forbidden(*args, **kwargs):
        raise AssertionError('Preparation opened a live transaction')

    monkeypatch.setattr(install, 'InstallTxn', forbidden)
    with pytest.raises((RuntimeError, ValueError, OSError)):
        prepare(tmp_path, found, options)
    assert snapshot(found) == before


def test_all_games_prepared_before_first_write_and_no_executor_interaction(
        tmp_path, monkeypatch, patch_download):
    found, options = combined(tmp_path)
    before = snapshot(found)
    adapter, prepared = prepare(tmp_path, found, options)
    assert snapshot(found) == before
    assert tuple(g.game.key for g in prepared.games) == tuple(found)
    assert prepared.games[-1].game.packages[0].name == 'MGSPatriotFix'
    assert prepared.games[-1].mods == (('MGSPatriotFix', '0.2.2'),)
    body = next(data for action, target, data in prepared.games[-1].actions
                if action == 'bytes' and target == 'MGSPatriotFix.settings')
    install.validate_patriot_settings(body.decode())
    for game_plan in prepared.games:
        assert all(Path(source).is_file() for source, _ in game_plan.identities)

    def forbidden(*args, **kwargs):
        raise AssertionError('Execution repeated UI, network or settings/recipe preparation')

    for name in ('UI', 'download', 'fetch', 'install_m2fix', 'install_hdfix',
                 'install_bugfix', 'install_patriot', 'write_settings',
                 'write_patriot_settings', 'set_launcher_options', 'options_for_game'):
        monkeypatch.setattr(install, name, forbidden)
    outcomes = dict.fromkeys(found, 'not started')
    install.execute_plan(prepared, adapter, outcomes)
    assert set(outcomes.values()) == {'installed and verified'}
    assert (found['mgs4'][0] / 'mgs4_savedata_win/123/save.dat').read_bytes() == b'licensed save'


@pytest.mark.parametrize('change', ['settings', 'recovery', 'record', 'payload', 'package'])
def test_mgs4_drift_refuses_before_earlier_game_writes(
        tmp_path, monkeypatch, patch_download, change):
    found, options = combined(tmp_path)
    root = found['mgs4'][0]
    settings = root / 'MGSPatriotFix.settings'
    settings.write_text(install.render_ini(install.patriot_defaults()))
    options['mgs4'] = opts(root)
    adapter, prepared = prepare(tmp_path, found, options)
    if change == 'settings':
        # Hash the exact config bytes in snapshots, beyond stat identities.
        assert install.sha256_file(settings) in prepared.plan.games[-1].inputs
        settings.write_text(settings.read_text().replace('Disable Motion Blur=0', 'Disable Motion Blur=1'))
    elif change in ('recovery', 'record'):
        recovery = root / install.MODKIT_DIRNAME
        recovery.mkdir()
        (recovery / (install.JOURNAL_NAME if change == 'recovery' else install.MANIFEST_NAME)).write_text('{}')
    elif change == 'payload':
        Path(prepared.games[-1].identities[0][0]).write_bytes(b'tampered')
    else:
        monkeypatch.setattr(install, 'PATRIOT_SHA256', 'a' * 64)
    before = snapshot(found)
    outcomes = dict.fromkeys(found, 'not started')
    with pytest.raises(install.ReplanRequired):
        install.execute_plan(prepared, adapter, outcomes)
    assert snapshot(found) == before
    assert set(outcomes.values()) == {'not started'}


@pytest.mark.parametrize('failure', ['cancel', 'write'])
def test_mgs4_execution_rolls_back_while_prior_games_stay_committed(
        tmp_path, monkeypatch, patch_download, failure):
    found, options = combined(tmp_path)
    root = found['mgs4'][0]
    settings = root / 'MGSPatriotFix.settings'
    settings.write_text(install.render_ini(install.patriot_defaults()))
    options['mgs4'] = opts(root)
    before = snapshot(found)['mgs4']
    adapter, prepared = prepare(tmp_path, found, options)
    real = install.InstallTxn.write_bytes

    def interrupt(tx, rel, data):
        real(tx, rel, data)
        if tx.game_key == 'mgs4':
            raise install.CancelledInstall('cancel after settings write') if failure == 'cancel' else OSError('write failed')

    monkeypatch.setattr(install.InstallTxn, 'write_bytes', interrupt)
    outcomes = dict.fromkeys(found, 'not started')
    with pytest.raises((install.CancelledInstall, OSError)):
        install.execute_plan(prepared, adapter, outcomes)
    assert all(outcomes[k] == 'installed and verified' for k in ('mgs1', 'mgs2', 'mgs3'))
    assert outcomes['mgs4'] == 'previous setup restored'
    assert snapshot(found)['mgs4'] == before


def test_mgs4_cancel_during_preparation_keeps_all_games_unstarted(tmp_path, monkeypatch, patch_download):
    found, options = combined(tmp_path)
    before = snapshot(found)
    cancel = threading.Event()
    monkeypatch.setattr(install, 'CANCEL_EVENT', cancel)
    real = install.install_patriot

    def interrupt(*args):
        real(*args)
        cancel.set()

    monkeypatch.setattr(install, 'install_patriot', interrupt)
    with pytest.raises(install.CancelledInstall):
        prepare(tmp_path, found, options)
    assert snapshot(found) == before


def test_mgs4_schema1_repair_custom_values_oldest_backup_and_removal(tmp_path, patch_download):
    found, options = combined(tmp_path)
    root = found['mgs4'][0]
    settings = root / 'MGSPatriotFix.settings'
    parser = install.patriot_defaults()
    parser['Language Settings']['Game Language'] = '"fr"'
    parser['Mouse Settings']['Mouse Horizontal Sensitivity'] = '2.5'
    settings.write_text(install.render_ini(parser))
    (root / 'MGSM2Fix.asi').write_bytes(b'unowned legacy-named file')
    options['mgs4'] = opts(root)
    before = snapshot(found)
    adapter, prepared = prepare(tmp_path, found, options)
    install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
    record = root / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    body = json.loads(record.read_text())
    body['schema'] = 1
    body.pop('files', None)
    record.write_text(json.dumps(body))
    custom = install.validate_patriot_settings(settings.read_text())
    custom['Mouse Settings']['Mouse Horizontal Sensitivity'] = '3.5'
    settings.write_text(install.render_ini(custom))
    options['mgs4'] = opts(root)
    adapter, prepared = prepare(tmp_path, found, options, 'repair')
    install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
    assert install.validate_patriot_settings(settings.read_text())['Mouse Settings']['Mouse Horizontal Sensitivity'] == '3.5'
    for folder, _ in found.values():
        notes, ok = install.uninstall_game(folder, lambda _: None)
        assert ok, notes
    assert snapshot(found) == before


def test_mgs4_supplied_audio_refused(tmp_path):
    found, options = combined(tmp_path)
    component = {'path': 'unused.zip', 'role': 'base'}
    with pytest.raises(ValueError, match='Incompatible'):
        install.build_install_plan(found, options, {'mgs4': [component]})


def test_mgs4_plan_settings_identity_is_immutable(tmp_path, patch_download):
    found, options = combined(tmp_path)
    adapter, prepared = prepare(tmp_path, found, options)
    # Replacing the confirmed game/settings cannot be replayed with old actions.
    changed = replace(prepared.plan.games[-1], settings='{}')
    stale = replace(prepared, plan=replace(prepared.plan, games=prepared.plan.games[:-1] + (changed,)))
    before = snapshot(found)
    with pytest.raises(ValueError, match='plan order'):
        install.execute_plan(stale, adapter, dict.fromkeys(found, 'not started'))
    assert snapshot(found) == before


@pytest.mark.parametrize('key', ['mgs3', 'mgs4'])
@pytest.mark.parametrize('obstruction', ['root', 'staging', 'rollback', 'backups', 'backup-parent', 'backup-destination'])
def test_transaction_obstructions_refuse_before_any_game_commits(
        tmp_path, patch_download, key, obstruction):
    found, options = combined(tmp_path)
    root = found[key][0]
    recovery = root / install.MODKIT_DIRNAME
    if obstruction == 'root':
        recovery.write_bytes(b'obstruction')
    else:
        recovery.mkdir()
        if obstruction.startswith('backup-'):
            dest = root / ('plugins/MGSHDFix.asi' if key == 'mgs3' else 'MGS4/scripts/MGSPatriotFix.asi')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b'original')
            rel = dest.relative_to(root)
            if obstruction == 'backup-parent':
                backup = recovery / 'backups' / rel.parent
                backup.parent.mkdir(parents=True)
                backup.write_bytes(b'obstructed parent')
            else:
                (recovery / 'backups' / rel).mkdir(parents=True)
        else:
            (recovery / obstruction).write_bytes(b'obstruction')
    before = snapshot(found)
    with pytest.raises((RuntimeError, ValueError, OSError)):
        prepare(tmp_path, found, options)
    assert snapshot(found) == before
    assert all(not (g / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
               for g, _ in found.values())


@pytest.mark.parametrize('key', ['mgs3', 'mgs4'])
def test_cached_archive_replacement_after_first_commit_is_refused(
        tmp_path, monkeypatch, patch_download, key):
    found, options = combined(tmp_path)
    adapter, prepared = prepare(tmp_path, found, options)
    before = snapshot(found)
    cached_game = next(g for g in prepared.games if g.game.key == key)
    cached = Path(cached_game.identities[-1][0])
    real = adapter.execute

    def replace_after_first(game, index, outcomes):
        real(game, index, outcomes)
        if index == 0:
            build_zip(cached, {'plugins/UNCONFIRMED.asi': b'unconfirmed'})

    monkeypatch.setattr(adapter, 'execute', replace_after_first)
    outcomes = dict.fromkeys(found, 'not started')
    with pytest.raises(install.ReplanRequired, match='Prepared payload changed'):
        install.execute_plan(prepared, adapter, outcomes)
    assert outcomes['mgs1'] == 'installed and verified'
    assert outcomes[key] == 'not changed; inspect recovery record / lock'
    assert snapshot(found)[key] == before[key]
    assert not any('UNCONFIRMED' in rel for files in snapshot(found).values() for rel in files)
    if key == 'mgs3':
        assert outcomes['mgs4'] == 'not started'


def test_cached_source_change_during_extraction_cannot_change_replay_bytes(
        tmp_path, monkeypatch, patch_download):
    found, options = combined(tmp_path)
    adapter, prepared = prepare(tmp_path, found, options)
    originals = {source: Path(source).read_bytes()
                 for game in prepared.games for source, _ in game.identities}
    real = install.InstallTxn.install_archive
    calls = []

    def mutate_originals(tx, archive, **kwargs):
        assert str(archive) not in originals
        # The selected game's every archive is already authenticated privately.
        game = next(g for g in prepared.games if g.game.key == tx.game_key)
        for source, _ in game.identities:
            Path(source).write_bytes(b'replaced during archive use')
        assert archive.read_bytes() in originals.values()
        calls.append(tx.game_key)
        return real(tx, archive, **kwargs)

    monkeypatch.setattr(install.InstallTxn, 'install_archive', mutate_originals)
    outcomes = dict.fromkeys(found, 'not started')
    install.execute_plan(prepared, adapter, outcomes)
    assert set(outcomes.values()) == {'installed and verified'}
    assert set(calls) == set(found)
    for folder, _ in found.values():
        notes, ok = install.uninstall_game(folder, lambda _: None)
        assert ok, notes
