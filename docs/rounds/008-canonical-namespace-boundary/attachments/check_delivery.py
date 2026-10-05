"""Reproducible local evidence for round 008; no installer or game execution."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
BASE = '2c7a0372cb251b78b0c7ea75ad5581d04edf270d'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    rows = []

    def run(command, cwd=ROOT):
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        rows.append({'command': command, 'exit': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
        print(' '.join(command), '->', result.returncode)
        print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        return result

    head = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
    run(['git', 'diff', '--stat', BASE])
    files = run(['git', 'ls-tree', '-r', '--name-only', BASE]).stdout.splitlines()
    allowed = {'tools/capture_settings_schema.py', 'tests/test_schema_capture.py', 'docs/UPGRADING.md'}
    protected = [name for name in files if name not in allowed
                 and not name.startswith('docs/rounds/008-canonical-namespace-boundary/attachments/')]
    for name in protected:
        original = subprocess.run(['git', 'show', BASE + ':' + name], cwd=ROOT,
                                  capture_output=True, check=True).stdout
        assert (ROOT / name).read_bytes() == original, name
    print('Protected tracked files byte-identical:', len(protected))
    with tempfile.TemporaryDirectory() as scratch:
        prior = Path(scratch)
        (prior / 'tools').mkdir()
        (prior / 'tests/fixtures').mkdir(parents=True)
        old = subprocess.run(['git', 'show', BASE + ':tools/capture_settings_schema.py'], cwd=ROOT,
                             capture_output=True, check=True).stdout
        (prior / 'tools/capture_settings_schema.py').write_bytes(old)
        shutil.copy(ROOT / 'tests/test_schema_capture.py', prior / 'tests')
        shutil.copy(ROOT / 'tests/fixtures/hdfix-reviewed-header-tail.hpp', prior / 'tests/fixtures')
        regression = run([sys.executable, '-m', 'pytest', 'tests/test_schema_capture.py', '-q'], prior)
        assert regression.returncode == 1
        assert 'test_namespace_boundary_rejects_api_and_cli' in regression.stdout
        run([sys.executable, str(ROOT / 'docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py'),
             '--source-root', str(prior), '--compile-cpp'])
    for command in [
        [sys.executable, 'docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py', '--compile-cpp'],
        [sys.executable, '-m', 'pytest', 'tests/test_schema_capture.py', '-q'],
        [sys.executable, '-m', 'pytest', 'tests/', '-q'],
        [sys.executable, '-m', 'ruff', 'check', '.'],
        [sys.executable, '-m', 'py_compile', 'tools/fw.py', 'install.py', 'tools/capture_settings_schema.py'],
        [sys.executable, 'tools/fw.py', 'check'],
        [sys.executable, 'tools/fw.py', 'status'],
    ]:
        assert run(command).returncode == 0, command
    for name in ['tools/capture_settings_schema.py', 'tests/test_schema_capture.py']:
        ast.parse((ROOT / name).read_text(), feature_version=(3, 9))
    from tools.capture_settings_schema import STRING, without_comments
    import re
    tail = without_comments((ROOT / 'tests/fixtures/hdfix-reviewed-header-tail.hpp').read_text())
    fingerprint = hashlib.sha256('\0'.join(re.findall(
        STRING + r'|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|\S', tail)).encode()).hexdigest()
    assert fingerprint == '8ade693eb22bd65377db0fed88492cb132ce0213af49d05d3b49fc00546e39fd'
    args.output.write_text(json.dumps({'checked_commit': head, 'baseline': BASE,
                                      'protected_byte_identical': len(protected),
                                      'python39_syntax': True, 'reviewed_tail_sha256': fingerprint,
                                      'commands': rows}, indent=2) + '\n')


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    main()
