"""Independent record/preparation checks; all game directories are disposable."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    seat = Path(sys.argv[1]).resolve()
    sys.path[:0] = [str(seat), str(seat / 'tests')]
    import install
    from pytest import MonkeyPatch
    from conftest import mod_zips, patch_download
    from test_mgs4_plan import combined, prepare
    from test_install_plan import snapshot
    print('Reviewed SHA:', subprocess.check_output(
        ['git', '-C', str(seat), 'rev-parse', 'HEAD'], text=True).strip())
    cases = [None, 42, ['invalid'], [], [['custom', 'value']], 'invalid', True]
    count = 0
    for key in ('mgs1', 'mgs2', 'mgs3', 'mgs4'):
        for bad in cases:
            with TemporaryDirectory() as folder, MonkeyPatch.context() as patch:
                base = Path(folder)
                patch.setattr(install, 'app_data_dir', lambda: base / 'app-state')
                patch_download.__wrapped__(patch, mod_zips.__wrapped__(base))
                found, options = combined(base)
                found[key] = found.pop(key)
                game = found[key][0]
                records = game / install.MODKIT_DIRNAME
                records.mkdir()
                record = records / install.MANIFEST_NAME
                record.write_text(json.dumps({'schema': 1, 'game': key, 'added': [],
                                              'overwritten': [], 'mods': {}, 'settings': bad}))
                backup = records / 'backups' / (
                    'MGSPatriotFix.settings' if key == 'mgs4' else 'original.bin')
                backup.parent.mkdir()
                backup.write_bytes(b'oldest original bytes')
                options[key] = install.options_for_game(key, found[key], options[key], lambda _: None)
                before = snapshot(found)
                membership = {k: sorted(p.relative_to(g).as_posix() for p in g.rglob('*'))
                              for k, (g, _) in found.items()}
                opened = []

                def forbidden(*args, **kwargs):
                    opened.append(args)
                    raise AssertionError('Live transaction opened during preparation')

                patch.setattr(install, 'InstallTxn', forbidden)
                try:
                    prepare(base, found, options)
                except install.CorruptManifestError as error:
                    assert 'Invalid install record' in str(error)
                else:
                    raise AssertionError('Malformed settings accepted')
                assert not opened and snapshot(found) == before
                assert membership == {k: sorted(p.relative_to(g).as_posix() for p in g.rglob('*'))
                                      for k, (g, _) in found.items()}
                count += 1
        print(key, 'late malformed settings refused; records/backups/all games unchanged')
    print('PASS', count, 'independent malformed settings cases; no live transaction construction')
    print('Native games and real-device restoration NOT RUN')


if __name__ == '__main__':
    main()
