"""Independent valid old/new records through full mixed-game repair/removal."""
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
    for schema in (1, 2):
        for missing in (False, True):
            with TemporaryDirectory() as folder, MonkeyPatch.context() as patch:
                base = Path(folder)
                patch.setattr(install, 'app_data_dir', lambda: base / 'app-state')
                patch_download.__wrapped__(patch, mod_zips.__wrapped__(base))
                found, options = combined(base)
                game = found['mgs4'][0]
                settings = game / 'MGSPatriotFix.settings'
                parser = install.patriot_defaults()
                parser['Mouse Settings']['Mouse Vertical Sensitivity'] = '2.750000'
                parser['Launcher and Splashscreens']['Internal Upscaling (PW)'] = '"4K"'
                settings.write_text(install.render_ini(parser))
                (game / 'MGSM2Fix.asi').write_bytes(b'unowned original')
                before = snapshot(found)
                for key, location in found.items():
                    options[key] = install.options_for_game(key, location, options[key], lambda _: None)
                adapter, prepared = prepare(base, found, options)
                assert snapshot(found) == before
                install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
                for directory, _ in found.values():
                    record = directory / install.MODKIT_DIRNAME / install.MANIFEST_NAME
                    body = json.loads(record.read_text())
                    body['schema'] = schema
                    if schema == 1:
                        body.pop('files', None)
                    if missing:
                        body.pop('settings', None)
                    else:
                        body['settings']['owner-custom-metadata'] = {'keep-structurally-valid': True}
                    body['mods']['owner-extra-mod'] = 'owner-version'
                    record.write_text(json.dumps(body))
                for key, location in found.items():
                    options[key] = install.options_for_game(key, location, options[key], lambda _: None)
                before_repair = snapshot(found)
                adapter, prepared = prepare(base, found, options, 'repair')
                assert snapshot(found) == before_repair
                install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
                values = install.validate_patriot_settings(settings.read_text())
                assert values['Mouse Settings']['Mouse Vertical Sensitivity'] == '2.750000'
                assert values['Launcher and Splashscreens']['Internal Upscaling (PW)'] == '"4K"'
                for directory, _ in found.values():
                    body = json.loads((directory / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
                    assert body['mods']['owner-extra-mod'] == 'owner-version'
                    notes, ok = install.uninstall_game(directory, lambda _: None)
                    assert ok, notes
                assert snapshot(found) == before
                print('PASS schema', schema, 'settings missing', missing,
                      'all-game install/repair/remove; custom/hidden values, saves, oldest originals and unowned ASI preserved')
    print('All fixtures disposable; native compatibility NOT RUN')


if __name__ == '__main__':
    main()
