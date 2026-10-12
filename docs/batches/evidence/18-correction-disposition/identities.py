"""Read-only comparison with independent Git blobs; no native binaries run."""
from pathlib import Path
import subprocess
import hashlib
import json
import sys

root, upstream, source = map(Path, sys.argv[1:4])
pin = 'b036c761ac2af2d47e61a1b473c708f094bd4295'
mapping = {
    'docs/agents/FRAMEWORK.md': 'framework/FRAMEWORK.md',
    'docs/agents/roles/brain.md': 'framework/roles/brain.md',
    'docs/agents/roles/worker.md': 'framework/roles/worker.md',
    'docs/agents/roles/verifier.md': 'framework/roles/verifier.md',
    'tools/fw.py': 'tools/fw.py',
    'tests/test_framework.py': 'templates/tests/test_framework.py',
}
for name in ('worker-12-install-plan-engine', 'worker-14-mgs4-patriotfix',
             'worker-16-volume1-qol-upgrade'):
    seat = root / '.worktrees' / name
    print('Reviewed SHA:', subprocess.check_output(
        ['git', '-C', str(seat), 'rev-parse', 'HEAD'], text=True).strip())
    for local, original in mapping.items():
        blob = subprocess.check_output(['git', '-C', str(upstream), 'show', pin + ':' + original])
        assert (seat / local).read_bytes().replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n')
    print(name, 'six pinned framework copies unchanged: PASS')
seat = root / '.worktrees/worker-16-volume1-qol-upgrade'
for local in ('install.py', 'Install-MGS-Mods.cmd', 'Install-MGS-Mods.desktop', 'MGSHDFix.settings'):
    if (seat / local).exists():
        blob = subprocess.check_output(['git', '-C', str(root), 'show', 'origin/main:' + local])
        assert (seat / local).read_bytes() == blob
print('Batch 16 shipping installer, shortcuts and template unchanged: PASS')
seat = root / '.worktrees/worker-14-mgs4-patriotfix'
fixture = json.loads((seat / 'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == fixture['tree']
assert subprocess.check_output(['git', '-C', str(source), 'ls-remote', 'origin', 'refs/tags/0.2.2'], text=True).split()[0] == fixture['tree']
names = {p for p in subprocess.check_output(['git', '-C', str(source), 'ls-files'], text=True).splitlines()
         if p.startswith(('src/', 'ConfigTool/')) and Path(p).suffix in ('.cpp', '.hpp', '.h')}
assert names == set(fixture['source_sha256'])
for name in names:
    blob = subprocess.check_output(['git', '-C', str(source), 'show', fixture['tree'] + ':' + name])
    attr = subprocess.check_output(['git', '-C', str(source), 'check-attr', 'eol', '--', name], text=True).strip().split(': ')[-1]
    checkout = blob.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n') if attr == 'crlf' else blob
    assert hashlib.sha256(checkout).hexdigest() == fixture['source_sha256'][name], name
    assert (source / name).read_bytes() == checkout, name
print('PatriotFix live official tag + 61 checkout/blob hashes incl all three headers: PASS')
