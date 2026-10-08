"""Independent shortcut bytes, base pins, Python grammar and framework copies."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
raw = (root / 'install.py').read_bytes()
digest = hashlib.sha256(raw).hexdigest().encode()
assert re.search(rb'^MODKIT_VERSION = "([^"]+)"', raw, re.M)[1] == b'2.3.0'
for name in ('Install-MGS-Mods.cmd', 'Install-MGS-Mods.desktop'):
    data = (root / name).read_bytes()
    assert re.search(rb'(?:set ")?TAG=(v[^";\r\n]+)', data)[1] == b'v2.3.0'
    assert re.search(rb'(?:set ")?SHA=([0-9a-f]{64})', data)[1] == digest
    assert (b'\n' not in data.replace(b'\r\n', b'') and b'\r' not in data.replace(b'\r\n', b'')) if name.endswith('.cmd') else b'\r' not in data
    print(name, 'v2.3.0', digest.decode(), 'line endings OK')
for path in root.rglob('*.py'):
    if '.git' in path.parts or '.worktrees' in path.relative_to(root).parts or '.venv' in path.parts:
        continue
    data = path.read_bytes()
    assert b'\r' not in data, path
    ast.parse(data, feature_version=(3, 9))
print('All candidate Python files: LF and Python 3.9 grammar OK')


def constants(body):
    return {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(body).body
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in {'MODKIT_VERSION', 'GAMES', 'HDFIX_VERSION', 'HDFIX_URL', 'HDFIX_SHA256',
                                   'M2FIX_VERSION', 'M2FIX_TAG', 'M2FIX_URL', 'M2FIX_SHA256'}}


base = '67d1406fafb8f6e68f61f182665a2e1d9fc6f6a0'
old = constants(subprocess.check_output(['git', 'show', base + ':install.py'], cwd=root))
new = constants(raw)
assert new['GAMES'].pop('mgs4')['appid'] == '2492670'
assert new == old
print('MGS1–3 definitions/pins/URLs/checksums and unpublished kit version unchanged')
assert not subprocess.check_output(['git', 'diff', base, '--', 'docs/agents', 'tools/fw.py', 'tests/test_framework.py'], cwd=root)
source = Path(sys.argv[1])
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip() == 'b036c761ac2af2d47e61a1b473c708f094bd4295'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source)
manifest = json.loads((root / 'docs/agents/framework.json').read_text())
for local, upstream in {
    'docs/agents/FRAMEWORK.md': 'framework/FRAMEWORK.md',
    'docs/agents/roles/brain.md': 'framework/roles/brain.md',
    'docs/agents/roles/worker.md': 'framework/roles/worker.md',
    'docs/agents/roles/verifier.md': 'framework/roles/verifier.md',
    'tools/fw.py': 'tools/fw.py',
    'tests/test_framework.py': 'templates/tests/test_framework.py',
}.items():
    data = (root / local).read_bytes().replace(b'\r\n', b'\n')
    assert data == (source / upstream).read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(data).hexdigest() == manifest['files'][local]['sha256']
    print(local, 'matches pinned immutable framework 4.0.0 and manifest')
print('Checked commit:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip())
