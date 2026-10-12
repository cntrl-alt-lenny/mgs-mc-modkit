"""Worker rerun of preserved independent review probes; disposable fixtures only, no native binaries run."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import install  # noqa: E402
from conftest import FakeUI, MOD_LAYOUTS, build_zip  # noqa: E402
from tools.capture_patriot_schema import capture  # noqa: E402


def game(root):
    for name in ('MGS4/mgs4.exe', 'Launcher/launcher.exe', 'mgs4_savedata_win/1/save.dat'):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'original fixture')
    return root


def perform(root, tmp):
    with install.GameLock(root):
        tx = install.InstallTxn(root, 'mgs4', print)
        try:
            choices = install.options_for_game('mgs4', (root, root), {}, print)
            install.install_patriot(tx, tmp, choices, print)
            tx.commit()
        except BaseException:
            tx.rollback()
            raise


def main():
    source = Path(sys.argv[1])
    archive = Path(sys.argv[2])
    expected = json.loads((ROOT / 'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
    assert capture(source) == expected
    print('PASS fresh official source capture equals fixture: 28 fields / 24 reads')
    for name in ('src/resources/stdafx.h', 'ConfigTool/pch.h', 'src/resources/version.h'):
        header = source / name
        original = header.read_bytes()
        try:
            header.write_bytes(original + b'\n#error Unreviewed compiled header\n')
            try:
                capture(source)
            except ValueError as error:
                assert 'Unreviewed source bytes: ' + name in str(error)
            else:
                raise AssertionError('modified header accepted: ' + name)
            print('PASS modified compiled header refuses at unchanged HEAD:', name)
        finally:
            header.write_bytes(original)
    assert capture(source) == expected
    data = archive.read_bytes()
    assert hashlib.sha256(data).hexdigest() == install.PATRIOT_SHA256
    print('PASS official ZIP hash', install.PATRIOT_SHA256)
    parser = install.patriot_defaults()
    for section in parser.sections():
        for key in parser[section]:
            missing = install.patriot_defaults()
            missing.remove_option(section, key)
            try:
                install.validate_patriot_settings(install.render_ini(missing))
            except RuntimeError:
                pass
            else:
                raise AssertionError('omission accepted: ' + key)
    print('PASS each of 28 missing keys refused')
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder)
        install.app_data_dir = lambda: base / 'app-state'
        tmp = base / 'downloads'
        tmp.mkdir()
        # Actual authenticated archive for all MGS4 writes.
        def fetch(url, dest, log, sha256=None):
            assert url == install.PATRIOT_URL and sha256 == install.PATRIOT_SHA256
            shutil.copyfile(archive, dest)
        install.download = fetch
        root = game(base / 'game')
        custom = install.patriot_defaults()
        custom['Language Settings']['Game Language'] = '"fr"'
        custom['Mouse Settings']['Mouse Vertical Sensitivity'] = '2.750000'
        custom['Launcher and Splashscreens']['Internal Upscaling (PW)'] = '"4K"'
        original_settings = install.render_ini(custom).encode()
        settings = root / 'MGSPatriotFix.settings'
        settings.write_bytes(original_settings)
        perform(root, tmp)
        assert install.validate_patriot_settings(settings.read_text())['Mouse Settings']['Mouse Vertical Sensitivity'] == '2.750000'
        tx = install.InstallTxn(root, 'mgs4', print)
        tx.write_bytes('MGSPatriotFix.settings', b'process died')
        install.find_games = lambda: {'mgs4': (root, base)}
        install.apply_branding = lambda log: None
        install.kit_update_notice = lambda log: ''
        install.IS_WINDOWS = True
        sys.argv = ['install.py']
        ui = FakeUI(menu=['install', 'go'])
        install.UI = lambda: ui
        assert install._main(print) == 0, ui.errors
        restored = install.validate_patriot_settings(settings.read_text())
        assert restored['Language Settings']['Game Language'] == '"fr"'
        assert restored['Mouse Settings']['Mouse Vertical Sensitivity'] == '2.750000'
        assert restored['Launcher and Splashscreens']['Internal Upscaling (PW)'] == '"4K"'
        print('PASS full UI interrupted-repair recovery retains custom and hidden values')
        # Corrupt journal must refuse before touching saves.
        tx = install.InstallTxn(root, 'mgs4', print)
        tx.write_bytes('MGSPatriotFix.settings', b'interrupted')
        journal = json.loads(tx.journal.read_text())
        journal['entries'].append({'path':'mgs4_savedata_win/1/save.dat','existed':False})
        tx.journal.write_text(json.dumps(journal))
        try:
            install.recover_interrupted(root, print)
        except install.CorruptManifestError:
            pass
        else:
            raise AssertionError('unsafe save journal accepted')
        assert (root / 'mgs4_savedata_win/1/save.dat').read_bytes() == b'original fixture'
        journal['entries'].pop()
        tx.journal.write_text(json.dumps(journal))
        assert install.recover_interrupted(root, print)[1]
        # Linked settings destination refuses and leaves external bytes untouched.
        external = base / 'external.settings'
        external.write_bytes(settings.read_bytes())
        settings.unlink()
        settings.symlink_to(external)
        try:
            install.options_for_game('mgs4', (root, base), {}, print)
        except RuntimeError:
            pass
        else:
            raise AssertionError('linked settings accepted')
        settings.unlink()
        settings.write_bytes(external.read_bytes())
        print('PASS corrupt save journal and linked settings refusal')
        notes, ok = install.uninstall_game(root, print)
        assert ok, notes
        assert settings.read_bytes() == original_settings
        print('PASS actual archive install/repair/removal restores oldest settings and save bytes')
        unrelated = game(base / 'unrelated-root')
        manual_asi = unrelated / 'MGSM2Fix.asi'
        manual_asi.write_bytes(b'untracked user file')
        perform(unrelated, tmp)
        assert manual_asi.read_bytes() == b'untracked user file'
        manifest = json.loads((unrelated / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
        assert 'MGSM2Fix.asi' not in manifest['added']
        assert all(o['path'] != 'MGSM2Fix.asi' for o in manifest['overwritten'])
        notes, ok = install.uninstall_game(unrelated, print)
        assert ok and manual_asi.read_bytes() == b'untracked user file', notes
        print('PASS actual-archive MGS4 removal preserves unowned MGSM2Fix.asi:', notes)
        # Mixed cancellation after MGS1 commits must retain first result.
        first = base / 'mgs1'
        first.mkdir()
        (first / 'METAL GEAR SOLID.exe').write_bytes(b'original fixture')
        second = game(base / 'mgs4-second')
        mgs1zip = build_zip(base / 'mgs1.zip', MOD_LAYOUTS['MGSM2Fix'])
        def mixed_download(url, dest, log, sha256=None):
            if url == install.PATRIOT_URL:
                install.CANCEL_EVENT.set()
                install.check_cancelled()
            shutil.copyfile(mgs1zip, dest)
        install.download = mixed_download
        install.find_games = lambda: {'mgs1':(first, base), 'mgs4':(second, base)}
        ui = FakeUI(menu=['go'], checklist=[['mgs1','mgs4']])
        install.UI = lambda: ui
        assert install._main(print) == 1
        assert (first / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
        assert not (second / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
        assert 'MGS1: installed and verified' in str(ui.errors)
        assert 'MGS4: previous setup restored' in str(ui.errors)
        print('PASS mixed-game cancellation retains prior committed success')
    print('Native exports/ASI initialization/GUI/gameplay/real licensed restoration: NOT RUN')


if __name__ == '__main__':
    main()
