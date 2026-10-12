"""Combined preparation/replay with the authenticated official MGS4 archive.

Other games use disposable synthetic ZIPs; no game or upstream binary runs.
"""
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import install  # noqa: E402
from conftest import MOD_LAYOUTS, build_zip  # noqa: E402
from test_install_plan import snapshot  # noqa: E402
from test_mgs4_plan import combined, prepare  # noqa: E402
from test_patriot import opts  # noqa: E402

archive = Path(sys.argv[1])
assert install.sha256_file(archive) == install.PATRIOT_SHA256
print('PASS official ZIP:', install.PATRIOT_SHA256)
with tempfile.TemporaryDirectory() as folder:
    base = Path(folder)
    install.app_data_dir = lambda: base / 'app-state'
    payloads = {key: build_zip(base / (key + '.zip'), files)
                for key, files in MOD_LAYOUTS.items() if key != 'MGSPatriotFix'}
    payloads['MGSPatriotFix'] = archive
    install.HDFIX_SHA256 = install.sha256_file(payloads['MGSHDFix'])
    install.M2FIX_SHA256 = install.sha256_file(payloads['MGSM2Fix'])
    for game, key in (('mgs2', 'MGS2-Community-Bugfix'), ('mgs3', 'MGS3-Community-Bugfix')):
        install.GAMES[game]['bugfix_sha256'] = install.sha256_file(payloads[key])

    def download(url, dest, log, sha256=None):
        for key, source in payloads.items():
            if key in url:
                assert install.sha256_file(source) == sha256
                shutil.copyfile(source, dest)
                return
        raise AssertionError(url)

    install.download = download
    found, options = combined(base)
    root = found['mgs4'][0]
    (root / 'MGSM2Fix.asi').write_bytes(b'unowned legacy file')
    parser = install.patriot_defaults()
    parser['Mouse Settings']['Mouse Vertical Sensitivity'] = '2.750000'
    parser['Launcher and Splashscreens']['Internal Upscaling (PW)'] = '"4K"'
    settings = root / 'MGSPatriotFix.settings'
    settings.write_bytes(install.render_ini(parser).encode())
    options['mgs4'] = opts(root)
    before = snapshot(found)
    adapter, prepared = prepare(base, found, options)
    assert snapshot(found) == before
    print('PASS all four games prepared with actual authenticated PatriotFix ZIP; zero live writes')

    def forbidden(*args, **kwargs):
        raise AssertionError('execution fetched or generated settings')

    writer = install.write_patriot_settings
    install.download, install.write_patriot_settings = forbidden, forbidden
    outcomes = dict.fromkeys(found, 'not started')
    install.execute_plan(prepared, adapter, outcomes)
    assert set(outcomes.values()) == {'installed and verified'}
    assert install.validate_patriot_settings(settings.read_text())['Mouse Settings']['Mouse Vertical Sensitivity'] == '2.750000'
    print('PASS mixed execution replays cached actual payload/settings with no network or writer calls')
    install.download, install.write_patriot_settings = download, writer
    for key, location in found.items():
        options[key] = install.options_for_game(key, location, options[key], lambda _: None)
    adapter, prepared = prepare(base, found, options, 'repair')
    install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
    for game, _ in found.values():
        notes, ok = install.uninstall_game(game, lambda _: None)
        assert ok, notes
    assert snapshot(found) == before
    print('PASS actual MGS4 repair/removal keeps oldest custom settings, save bytes and unowned legacy ASI')
print('Native exports/ASI initialization/licensed boots/gameplay/real-device restoration: NOT RUN')
