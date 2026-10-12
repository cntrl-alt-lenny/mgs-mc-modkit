"""Check the narrow correction against the preserved reviewed production."""
import ast
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[4]
base = '03c58903d386c1c9bc0c9671e8c4b60c69ae30b6'


def prior(name):
    return subprocess.check_output(['git', 'show', base + ':' + name], cwd=root)


def definitions(body):
    return {node.name: ast.dump(node) for node in ast.parse(body).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))}


old = definitions(prior('install.py'))
new = definitions((root / 'install.py').read_bytes())
assert old.keys() == new.keys()
assert [name for name in old if old[name] != new[name]] == ['_plan_validate_record']
print('PASS only _plan_validate_record changes; constructor, recovery, removal, recipes and writers unchanged')
for name in ('install_plan.py', 'tools/embed_install_plan.py',
             'tests/test_audio_acceptance.py', 'tools/capture_patriot_schema.py',
             'tests/fixtures/patriotfix-0.2.2-schema.json',
             'docs/batches/14-mgs4-patriotfix-review.md'):
    assert (root / name).read_bytes() == prior(name), name
print('PASS engine, embedding, audio acceptance, bounded source capture and latest Verifier report preserved')
assert subprocess.run(['git', 'merge-base', '--is-ancestor', base, 'HEAD'], cwd=root).returncode == 0
print('PASS preserved review head remains an ancestor')
