"""Assert unchanged recipes, safety correction, source boundary and engine."""
import ast
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def definitions(body):
    return {n.name: ast.dump(n) for n in ast.parse(body).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


before = definitions(git('show', 'c2e7ea470d5c38390238fc8854f31187499ff330:install.py'))
after = definitions((ROOT / 'install.py').read_bytes())
for name in ('InstallTxn', 'GameLock', 'recover_interrupted', '_uninstall_game',
             '_validate_manifest', 'validate_game_destination', 'install_patriot',
             'write_patriot_settings', 'validate_patriot_settings', 'install_hdfix',
             'install_bugfix', 'install_m2fix', 'install_better_audio',
             'write_settings', 'set_launcher_options', 'options_for_game'):
    assert before[name] == after[name], name
print('PASS original recipes/writers/InstallTxn/locks/recovery/removal/layout validation unchanged')
for name in ('install_plan.py', 'tools/embed_install_plan.py', 'tests/test_audio_acceptance.py'):
    assert (ROOT / name).read_bytes() == git('show', 'c3ecd64a7a3a3a3e8994a77511bb1585b3ec04a9:' + name)
print('PASS authoritative engine/embed tool/audio acceptance tests equal literal Batch 12 input')
for name in ('tests/fixtures/patriotfix-0.2.2-schema.json', 'tools/capture_patriot_schema.py',
             'docs/batches/14-mgs4-patriotfix-review.md'):
    assert (ROOT / name).read_bytes() == git('show', 'c2e7ea470d5c38390238fc8854f31187499ff330:' + name)
fixture = json.loads((ROOT / 'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
assert len(fixture['source_sha256']) == 61
assert len(fixture['runtime_reads']) == 24
assert sum(len(fields) for fields in fixture['fields'].values()) == 28
print('PASS original independent review/capture/61 source hashes/28 fields/24 reads preserved')
readme = (ROOT / 'README.md').read_text()
assert readme.count('| MGS4 |') == 1
assert '8 October 2026' in readme and 'unpublished' in readme
print('PASS one MGS4 README row; dated upstream candidates and unpublished checkout instructions')
print('Checked commit:', git('rev-parse', 'HEAD').decode().strip())
