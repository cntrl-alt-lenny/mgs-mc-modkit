"""Independent byte-level shortcut, line ending and unchanged pin checks."""
import ast
import hashlib
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[4]
source = (root / 'install.py').read_bytes()
assert b'\r' not in source
version = re.search(rb'^MODKIT_VERSION = "([^"]+)"', source, re.M).group(1)
assert version == b'2.3.0'
digest = hashlib.sha256(source).hexdigest().encode()
for name in ('Install-MGS-Mods.cmd', 'Install-MGS-Mods.desktop'):
    raw = (root / name).read_bytes()
    tag = re.search(rb'(?:set ")?TAG=(v[^";\r\n]+)', raw).group(1)
    pin = re.search(rb'(?:set ")?SHA=([0-9a-f]{64})', raw).group(1)
    assert tag == b'v' + version and pin == digest
    if name.endswith('.cmd'):
        assert b'\n' not in raw.replace(b'\r\n', b'') and b'\r' not in raw.replace(b'\r\n', b'')
    else:
        assert b'\r' not in raw
    print(name, tag.decode(), pin.decode(), 'line endings OK')
for name in subprocess.check_output(['git', 'ls-files', '*.py'], cwd=root, text=True).splitlines():
    raw = (root / name).read_bytes()
    assert b'\r' not in raw, name
    ast.parse(raw, feature_version=(3, 9))
print('All tracked Python LF / Python 3.9 grammar OK')
# Compare literal version/checksum/URL assignments with the base rather than importing it.
def pins(raw):
    module = ast.parse(raw)
    names = {'MODKIT_VERSION', 'HDFIX_VERSION', 'HDFIX_SHA256', 'HDFIX_URL',
             'M2FIX_VERSION', 'M2FIX_TAG', 'M2FIX_SHA256', 'M2FIX_URL', 'GAMES'}
    return {n.targets[0].id: ast.dump(n.value) for n in module.body
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names}
base = subprocess.check_output(['git', 'show', '90967b9:install.py'], cwd=root)
assert pins(source) == pins(base)
assert not subprocess.check_output(['git', 'diff', '90967b9', '--', 'docs/agents', 'tools/fw.py'], cwd=root)
print('All mod pins/checksums/URLs, kit version and framework copies unchanged from 90967b9')
