"""MGS4 installation journeys and independent pinned-source settings evidence."""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import pytest

import install
from conftest import FakeUI, MOD_LAYOUTS, build_zip
from tools.capture_patriot_schema import capture


def game(root):
    root.mkdir(parents=True, exist_ok=True)
    for name in ('MGS4/mgs4.exe', 'Launcher/launcher.exe'):
        p = root / name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(b'original game')
    saves = root / 'mgs4_savedata_win/123/save.dat'
    saves.parent.mkdir(parents=True)
    saves.write_bytes(b'licensed save')
    return root


def opts(root):
    return install.options_for_game('mgs4', (root, root), {}, lambda m: None)


def perform(root, tmp, choices=None):
    with install.GameLock(root):
        tx = install.InstallTxn(root, 'mgs4', lambda m: None)
        try:
            install.install_patriot(tx, tmp, choices or opts(root), lambda m: None)
            assert not install.verify_install(install.GAMES['mgs4'], root)
            tx.commit()
        except BaseException:
            tx.rollback()
            raise


def test_source_schema_runtime_and_conservative_defaults():
    audit = json.loads((Path(__file__).parent / 'fixtures/patriotfix-0.2.2-schema.json').read_text())
    assert audit['tree'] == install.PATRIOT_TREE
    assert audit['tag'] == install.PATRIOT_VERSION
    assert audit['fields'] == install.PATRIOT_FIELDS
    assert all(key in install.PATRIOT_FIELDS[sec] for sec, key in audit['runtime_reads'])
    parser = install.validate_patriot_settings(install.render_ini(install.patriot_defaults()))
    assert sum(len(parser[s]) for s in parser.sections()) == 28
    graphics = parser['Enhancements && Tweaks']
    assert graphics['Anisotropic Filtering Level'] == '8'
    assert graphics['Disable Motion Blur'] == graphics['Disable Dynamic Resolution'] == '0'
    assert graphics['Custom Shadow Resolution'] == '"0"'
    assert graphics['Pause On Focus Loss'] == '1'
    assert parser['Launcher and Splashscreens']['Internal Resolution (PW)'] == '"Original"'
    assert parser['Controller Settings']['Button Icons (PW)'] == '"Keyboard"'


@pytest.mark.parametrize('edit', [
    lambda b: b.replace('Anisotropic Filtering Level=8', 'Anisotropic Filtering Level=0'),
    lambda b: b.replace('Mouse Horizontal Sensitivity=1.0', 'Mouse Horizontal Sensitivity=nan'),
    lambda b: b.replace('Mouse Horizontal Sensitivity=1.0', 'Mouse Horizontal Sensitivity=11'),
    lambda b: b.replace('Disable Motion Blur=0', 'Disable Motion Blur=yes'),
    lambda b: b.replace('Internal Resolution (PW)="Original"', 'Internal Resolution (PW)="Unknown"'),
    lambda b: b.replace('Internal Resolution (PW)="Original"\n', ''),
    lambda b: b.replace('Game Region="eu"', 'Game Region="jp"'),
    lambda b: b.replace('Button Icons="AUTO"', 'Button Icons="Steam Deck"'),
    lambda b: b + '\n[DEFAULT]\nUnexpected=1\n',
])
def test_malformed_settings_refuse_before_install(tmp_path, patch_download, edit):
    root = game(tmp_path / 'game')
    body = edit(install.render_ini(install.patriot_defaults()))
    (root / 'MGSPatriotFix.settings').write_text(body)
    before = (root / 'MGSPatriotFix.settings').read_bytes()
    with pytest.raises(RuntimeError, match='validation failed'):
        opts(root)
    assert (root / 'MGSPatriotFix.settings').read_bytes() == before
    assert not (root / install.MODKIT_DIRNAME).exists()
    assert patch_download == []


def test_discovery_root_and_ambiguous_layout(tmp_path, monkeypatch):
    root = tmp_path / 'steam'
    folder = game(root / 'steamapps/common/METAL GEAR SOLID 4')
    monkeypatch.setattr(install, 'steam_roots', lambda: [root])
    assert install.find_games()['mgs4'] == (folder, root)
    (folder / 'mgspw').mkdir()
    wrong = folder / 'mgspw/METAL GEAR SOLID PEACE WALKER.exe'
    wrong.write_bytes(b'PW')
    assert 'mgs4' not in install.find_games()
    with pytest.raises(RuntimeError, match='Ambiguous'):
        install.validate_game_destination('mgs4', folder)
    wrong.unlink()
    (folder / 'Launcher/launcher.exe').unlink()
    assert 'mgs4' not in install.find_games()
    with pytest.raises(RuntimeError):
        install.validate_game_destination('mgs4', folder / 'MGS4')


@pytest.mark.parametrize('bad', ['mgspw/winmm.dll', 'mgs4_savedata_win/123/save.dat',
                                'MGS4/mgs4.exe', 'plugins/MGSHDFix.asi', 'MGS4/extra.asi'])
def test_wrong_payload_refuses_before_any_write(tmp_path, bad):
    root = game(tmp_path / 'game')
    files = dict(MOD_LAYOUTS['MGSPatriotFix'], **{bad: b'wrong'})
    archive = build_zip(tmp_path / 'wrong.zip', files)
    tx = install.InstallTxn(root, 'mgs4', lambda m: None)
    with pytest.raises(install.UnsafeArchiveError, match='reviewed MGS4 archive'):
        tx.install_archive(archive, component='patriot')
    assert not (root / 'MGS4/winmm.dll').exists()
    assert (root / 'mgs4_savedata_win/123/save.dat').read_bytes() == b'licensed save'
    assert tx.rollback()


def test_install_repair_preserve_custom_settings_oldest_backup_and_remove(tmp_path, patch_download):
    root = game(tmp_path / 'game')
    original = install.render_ini(install.patriot_defaults()).replace('Game Language="en"', 'Game Language="fr"')
    (root / 'MGSPatriotFix.settings').write_text(original)
    (root / 'logs').mkdir()
    (root / 'logs/MGSPatriotFix_Game.log').write_bytes(b'existing diagnostics')
    perform(root, tmp_path)
    assert all(url == install.PATRIOT_URL and checksum == install.PATRIOT_SHA256 for url, checksum in patch_download)
    custom = (root / 'MGSPatriotFix.settings').read_text().replace('Anisotropic Filtering Level=8', 'Anisotropic Filtering Level=16').replace('Internal Upscaling (PW)="Original"', 'Internal Upscaling (PW)="4K"')
    (root / 'MGSPatriotFix.settings').write_text(custom)
    choices = opts(root)
    choices.update(patriot_motion_blur_off=True, _changed={'patriot_motion_blur_off'})
    perform(root, tmp_path, choices)
    actual = (root / 'MGSPatriotFix.settings').read_text()
    assert 'Game Language="fr"' in actual and 'Anisotropic Filtering Level=16' in actual
    assert 'Disable Motion Blur=1' in actual and 'Internal Upscaling (PW)="4K"' in actual
    backup = root / install.MODKIT_DIRNAME / 'backups/MGSPatriotFix.settings'
    assert backup.read_text() == original
    raw = (root / 'MGSPatriotFix.settings').read_bytes()
    assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b'')
    notes, ok = install.uninstall_game(root, lambda m: None)
    assert ok, notes
    assert (root / 'MGSPatriotFix.settings').read_text() == original
    assert not (root / 'MGS4/winmm.dll').exists()
    assert (root / 'logs/MGSPatriotFix_Game.log').read_bytes() == b'existing diagnostics'
    assert (root / 'mgs4_savedata_win/123/save.dat').read_bytes() == b'licensed save'
    assert (root / 'MGS4/mgs4.exe').read_bytes() == b'original game'


@pytest.mark.parametrize('loader', ['MGS4/winmm.dll', 'Launcher/d3d11.dll', 'MGS4/dinput8.dll'])
def test_unmanaged_loaders_refuse(tmp_path, patch_download, loader):
    root = game(tmp_path / 'game')
    (root / loader).write_bytes(b'manual loader')
    with pytest.raises(RuntimeError, match='conflicting ASI loader'):
        perform(root, tmp_path)
    assert (root / loader).read_bytes() == b'manual loader'
    assert patch_download == []


def test_cancel_and_interrupted_repair_restore_current_settings(tmp_path, patch_download, monkeypatch):
    root = game(tmp_path / 'game')
    perform(root, tmp_path)
    edited = (root / 'MGSPatriotFix.settings').read_text().replace('Game Language="en"', 'Game Language="it"')
    (root / 'MGSPatriotFix.settings').write_text(edited)
    event = threading.Event()
    monkeypatch.setattr(install, 'CANCEL_EVENT', event)
    writer = install.write_patriot_settings

    def cancel(tx, choices, log):
        writer(tx, choices, log)
        event.set()
        install.check_cancelled()

    monkeypatch.setattr(install, 'write_patriot_settings', cancel)
    with pytest.raises(install.CancelledInstall):
        perform(root, tmp_path)
    event.clear()
    assert (root / 'MGSPatriotFix.settings').read_text() == edited
    # Simulate process death after a write; the next locked transaction recovers.
    tx = install.InstallTxn(root, 'mgs4', lambda m: None)
    tx.write_bytes('MGSPatriotFix.settings', b'interrupted')
    fresh = install.InstallTxn(root, 'mgs4', lambda m: None)
    assert (root / 'MGSPatriotFix.settings').read_text() == edited
    assert fresh.rollback()


def test_lock_refusal_and_reset(tmp_path, patch_download):
    root = game(tmp_path / 'game')
    perform(root, tmp_path)
    with install.GameLock(root):
        with pytest.raises(RuntimeError):
            with install.GameLock(root):
                pass
    custom = (root / 'MGSPatriotFix.settings').read_text().replace('Disable Motion Blur=0', 'Disable Motion Blur=1')
    (root / 'MGSPatriotFix.settings').write_text(custom)
    choices = opts(root)
    # Reset receives upfront conservative options from the plan.
    choices.update(opts(game(tmp_path / 'fresh')))
    choices['_reset'] = True
    perform(root, tmp_path, choices)
    assert 'Disable Motion Blur=0' in (root / 'MGSPatriotFix.settings').read_text()


def test_unreviewed_source_tree_refuses(tmp_path):
    with pytest.raises(Exception):
        capture(tmp_path)


def world(tmp_path, monkeypatch, found):
    monkeypatch.setattr(install, 'find_games', lambda: dict(found))
    monkeypatch.setattr(install, 'apply_branding', lambda log: None)
    monkeypatch.setattr(install, 'IS_WINDOWS', True)
    monkeypatch.setattr(sys, 'argv', ['install.py'])


def test_full_mgs4_journey_and_upfront_visual_choices(tmp_path, patch_download, monkeypatch):
    root = game(tmp_path / 'game')
    world(tmp_path, monkeypatch, {'mgs4': (root, tmp_path)})
    ui = FakeUI(menu=['opts', 'PlayStation 5', 'East for OK', '2048', '16', 'go'],
                checklist=[['skip_launcher', 'patriot_ds3', 'patriot_motion_blur_off']])
    monkeypatch.setattr(install, 'UI', lambda: ui)
    assert install.main() == 0
    assert not ui.errors and not ui._menu and not ui._checklist
    parser = install.validate_patriot_settings((root / 'MGSPatriotFix.settings').read_text())
    assert parser['Enhancements && Tweaks']['Custom Shadow Resolution'] == '"2048"'
    assert parser['Enhancements && Tweaks']['Disable Motion Blur'] == '1'
    assert parser['Controller Settings']['Button Icons'] == '"PlayStation 5"'
    assert 'winmm=n,b' in install.build_launch_options_text(['mgs4'])
    ui = FakeUI(menu=['uninstall'], checklist=[['mgs4']], yesno=[True])
    monkeypatch.setattr(install, 'UI', lambda: ui)
    assert install.main() == 0
    assert not (root / 'MGSPatriotFix.settings').exists()
    assert (root / 'mgs4_savedata_win/123/save.dat').exists()


def test_mixed_game_failure_keeps_first_committed_result(tmp_path, patch_download, monkeypatch):
    mgs1 = tmp_path / 'mgs1'
    mgs1.mkdir()
    (mgs1 / 'METAL GEAR SOLID.exe').write_bytes(b'game')
    mgs4 = game(tmp_path / 'mgs4')
    (mgs4 / 'MGS4/winmm.dll').write_bytes(b'manual')
    world(tmp_path, monkeypatch, {'mgs1': (mgs1, tmp_path), 'mgs4': (mgs4, tmp_path)})
    ui = FakeUI(menu=['go'], checklist=[['mgs1', 'mgs4']])
    monkeypatch.setattr(install, 'UI', lambda: ui)
    assert install.main() == 1
    assert (mgs1 / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
    assert not (mgs4 / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
    error = str(ui.errors)
    assert 'MGS1: installed and verified' in error and 'MGS4: previous setup restored' in error
    assert (mgs4 / 'MGS4/winmm.dll').read_bytes() == b'manual'


@pytest.mark.parametrize('rel', ['mgs4_savedata_win/123/save.dat', 'MGS4/mgs4.exe'])
def test_malformed_removal_records_cannot_touch_game_or_saves(tmp_path, patch_download, rel):
    root = game(tmp_path / 'game')
    perform(root, tmp_path)
    mf = root / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    data = json.loads(mf.read_text())
    data['added'].append(rel)
    mf.write_text(json.dumps(data))
    before = (root / rel).read_bytes()
    notes, ok = install.uninstall_game(root, lambda m: None)
    assert not ok and 'outside' in str(notes)
    assert (root / rel).read_bytes() == before and mf.exists()


def test_recovery_missing_snapshot_keeps_journal_and_backups(tmp_path, patch_download):
    root = game(tmp_path / 'game')
    perform(root, tmp_path)
    tx = install.InstallTxn(root, 'mgs4', lambda m: None)
    tx.write_bytes('MGSPatriotFix.settings', b'interrupted')
    (tx.rollback_dir / 'MGSPatriotFix.settings').unlink()
    with pytest.raises(install.CorruptManifestError, match='incomplete'):
        install.InstallTxn(root, 'mgs4', lambda m: None)
    assert tx.journal.exists() and (tx.root / install.MANIFEST_NAME).exists()


def test_capture_refuses_modified_source_and_added_reader(tmp_path, monkeypatch):
    import tools.capture_patriot_schema as tool
    monkeypatch.setattr(tool.subprocess, 'check_output', lambda *a, **k: tool.TREE)
    for name in tool.REVIEWED:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'unreviewed')
    with pytest.raises(ValueError, match='Unreviewed source bytes'):
        tool.capture(tmp_path)
    (tmp_path / 'src/new_reader.cpp').write_text('new reader')
    with pytest.raises(ValueError, match='inventory changed'):
        tool.capture(tmp_path)


def test_wrong_game_record_and_unsafe_journal_refuse(tmp_path, patch_download):
    root = game(tmp_path / 'game')
    perform(root, tmp_path)
    mf = root / install.MODKIT_DIRNAME / install.MANIFEST_NAME
    original = mf.read_text()
    record = json.loads(original)
    record['game'] = 'mgs2'
    mf.write_text(json.dumps(record))
    notes, ok = install.uninstall_game(root, lambda m: None)
    assert not ok and 'different' in str(notes)
    mf.write_text(original)
    tx = install.InstallTxn(root, 'mgs4', lambda m: None)
    tx.write_bytes('MGSPatriotFix.settings', b'interrupted')
    journal = json.loads(tx.journal.read_text())
    journal['entries'].append({'path': 'mgs4_savedata_win/123/save.dat', 'existed': False})
    tx.journal.write_text(json.dumps(journal))
    with pytest.raises(install.CorruptManifestError, match='Unsafe recovery record'):
        install.recover_interrupted(root, lambda m: None)
    assert (root / 'mgs4_savedata_win/123/save.dat').read_bytes() == b'licensed save'
    assert tx.journal.exists()


def test_orphan_save_backup_and_duplicate_asi_refuse(tmp_path, patch_download):
    root = game(tmp_path / 'game')
    backup = root / install.MODKIT_DIRNAME / 'backups/mgs4_savedata_win/123/save.dat'
    backup.parent.mkdir(parents=True)
    backup.write_bytes(b'wrong save')
    notes, ok = install.uninstall_game(root, lambda m: None)
    assert not ok and 'outside reviewed' in str(notes)
    assert (root / 'mgs4_savedata_win/123/save.dat').read_bytes() == b'licensed save'
    assert backup.exists()
    other = game(tmp_path / 'other')
    (other / 'MGS4/MGSPatriotFix.asi').write_bytes(b'manual')
    with pytest.raises(RuntimeError, match='Duplicate PatriotFix'):
        perform(other, tmp_path)


@pytest.mark.parametrize('header', ['ConfigTool/pch.h', 'src/resources/stdafx.h',
                                  'src/resources/version.h'])
def test_capture_authenticates_compiled_headers(tmp_path, monkeypatch, header):
    import hashlib
    import tools.capture_patriot_schema as tool
    monkeypatch.setattr(tool.subprocess, 'check_output', lambda *a, **k: tool.TREE)
    reviewed = {}
    for name in tool.REVIEWED:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'reviewed fixture')
        reviewed[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(tool, 'REVIEWED', reviewed)
    path = tmp_path / header
    path.write_bytes(b'reviewed fixture\n#error Unreviewed compiled header\n')
    with pytest.raises(ValueError, match='Unreviewed source bytes: ' + header):
        tool.capture(tmp_path)
    path.unlink()
    with pytest.raises(ValueError, match='inventory changed'):
        tool.capture(tmp_path)
    path.write_bytes(b'reviewed fixture')
    (tmp_path / 'src/added.h').write_bytes(b'new header')
    with pytest.raises(ValueError, match='inventory changed'):
        tool.capture(tmp_path)
