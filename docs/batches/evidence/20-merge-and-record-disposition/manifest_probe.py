"""Reproduce the final Verifier's record-preflight blocker in disposable games."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys


def main():
    seat = Path(sys.argv[1]).resolve()
    sys.path[:0] = [str(seat), str(seat / 'tests')]
    import install
    from pytest import MonkeyPatch
    from conftest import mod_zips, patch_download
    from test_mgs4_plan import combined, prepare
    from test_install_plan import snapshot
    print('Reviewed production SHA:', subprocess.check_output(
        ['git', '-C', str(seat), 'rev-parse', 'HEAD'], text=True).strip())
    for bad in (None, 42, ['invalid']):
        with TemporaryDirectory() as folder, MonkeyPatch.context() as patch:
            base = Path(folder)
            patch.setattr(install, 'TAR', install.find_tar())
            patch.setattr(install, 'app_data_dir', lambda: base / 'app-state')
            patch_download.__wrapped__(patch, mod_zips.__wrapped__(base))
            found, options = combined(base)
            last = found['mgs4'][0]
            record = last / install.MODKIT_DIRNAME / install.MANIFEST_NAME
            record.parent.mkdir()
            record.write_text(json.dumps({'schema': 1, 'game': 'mgs4', 'added': [],
                                          'overwritten': [], 'mods': {}, 'settings': bad}))
            options['mgs4'] = install.options_for_game(
                'mgs4', found['mgs4'], options['mgs4'], lambda _: None)
            before = snapshot(found)
            adapter, prepared = prepare(base, found, options)
            outcomes = dict.fromkeys(found, 'not started')
            try:
                install.execute_plan(prepared, adapter, outcomes)
            except install.CorruptManifestError as error:
                print('settings', repr(bad), type(error).__name__, outcomes)
            else:
                raise AssertionError('expected constructor refusal')
            assert all(outcomes[k] == 'installed and verified' for k in ('mgs1', 'mgs2', 'mgs3'))
            assert snapshot(found)['mgs4'] == before['mgs4']
    print('CONFIRMED: malformed late manifest settings escape preparation; no native games run')


if __name__ == '__main__':
    main()
