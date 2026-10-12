"""Independently verify authenticated checkout bytes and fixture delta."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
source = Path(sys.argv[1])
head = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
assert head == 'c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de'
assert subprocess.check_output(['git', '-C', str(source), 'ls-remote', 'origin', 'refs/tags/0.2.2'], text=True).split()[0] == head
assert not subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'])
fixture = json.loads((ROOT / 'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
tracked = subprocess.check_output(['git', '-C', str(source), 'ls-files'], text=True).splitlines()
names = {n for n in tracked if n.startswith(('src/', 'ConfigTool/')) and Path(n).suffix in {'.cpp', '.hpp', '.h'}}
assert names == set(fixture['source_sha256'])
for name in sorted(names):
    literal = subprocess.check_output(['git', '-C', str(source), 'show', head + ':' + name])
    # The official .gitattributes applies text eol=crlf to these inputs.
    attributes = subprocess.check_output(['git', '-C', str(source), 'check-attr', 'eol', '--', name], text=True)
    assert attributes.strip().endswith(': crlf'), attributes
    expected = literal.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    raw = (source / name).read_bytes()
    assert raw == expected, name
    assert hashlib.sha256(raw).hexdigest() == fixture['source_sha256'][name], name
    if name.endswith('.h'):
        print(name, 'authenticated Git blob + CRLF attribute:', hashlib.sha256(raw).hexdigest())
old = json.loads(subprocess.check_output(['git', 'show', '38ef1b6:tests/fixtures/patriotfix-0.2.2-schema.json'], cwd=ROOT))
added = set(fixture['source_sha256']) - set(old['source_sha256'])
assert added == {'ConfigTool/pch.h', 'src/resources/stdafx.h', 'src/resources/version.h'}
for name in added:
    fixture['source_sha256'].pop(name)
assert fixture == old
captured = subprocess.check_output([sys.executable, str(ROOT / 'tools/capture_patriot_schema.py'), str(source)])
assert json.loads(captured) == json.loads((ROOT / 'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
print('PASS independently enumerated/hashes verified 61 reviewed C++ files; clean capture reproduces fixture')
print('PASS only three header hashes added; settings fields/runtime reads/constraints and old hashes unchanged')
print('Boundary excludes build projects, resources, external dependencies and binaries; no build reproducibility claim')
