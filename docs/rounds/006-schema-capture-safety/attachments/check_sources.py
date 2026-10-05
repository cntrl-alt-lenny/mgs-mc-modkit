"""Separate live immutable-source check; not part of the offline test suite."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]


def main():
    scratch, output = map(Path, sys.argv[1:])
    audit = json.loads((ROOT / 'docs/rounds/004-mod-compatibility-audit/attachments/schema-delta.json').read_text())
    baseline = json.loads((ROOT / 'tests/fixtures/hdfix-4.1.0-schema.json').read_text())
    expected = {section: dict(fields) for section, fields in baseline['fields'].items()}
    for section, key, _ in audit['delta']['removed']:
        del expected[section][key]
    for section, key, kind in audit['delta']['added']:
        expected.setdefault(section, {})[key] = kind
    rows = []
    for tag, identity in audit['sources'].items():
        root = scratch / tag
        hashes = {}
        downloads = []
        for name, expected_hash in identity['source_sha256'].items():
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://raw.githubusercontent.com/ShizCalev/MGSHDFix/{identity['commit']}/{name}"
            command = ['curl', '-fLsS', '--retry', '2', url, '-o', str(dest)]
            result = subprocess.run(command, capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
            hashes[name] = hashlib.sha256(dest.read_bytes()).hexdigest()
            assert hashes[name] == expected_hash, name
            downloads.append({'url': url, 'exit': result.returncode})
        command = [sys.executable, str(ROOT / 'tools/capture_settings_schema.py'), str(root),
                   '--tag', tag, '--tree', identity['commit']]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        (scratch / (tag + '-capture.json')).write_text(result.stdout)
        assert data['source_sha256'] == hashes
        assert data['constraints'] == baseline['constraints']
        assert data['fields'] == (expected if tag == '4.1.2' else baseline['fields'])
        if tag == '4.1.0':
            assert data == baseline
        if tag == '4.1.2':
            assert data['flag_unions'] == {'kFirstPersonViewGameFlags': ['MGS2', 'MGS3']}
        rows.append({'tag': tag, 'commit': identity['commit'], 'downloads': downloads,
                     'source_sha256': hashes, 'cli_exit': result.returncode,
                     'sections': len(data['fields']), 'keys': sum(map(len, data['fields'].values())),
                     'exact_expected_fields_equal': True, 'baseline_constraints_equal': True,
                     'whole_baseline_fixture_equal': data == baseline,
                     'flag_unions': data.get('flag_unions', {})})
        print(f"{tag}: CLI exit 0; {rows[-1]['keys']} exact expected keys; constraints and ORIGINAL hashes match")
    output.write_text(json.dumps({'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                                 'rows': rows, 'delta': audit['delta']}, indent=2) + '\n')
    print('4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed')


if __name__ == '__main__':
    main()
