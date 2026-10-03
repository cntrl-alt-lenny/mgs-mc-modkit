"""Compare reviewed Config Tool source declarations without running its binary."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def flat(data):
    return {(section, key): value for section, fields in data.items() for key, value in fields.items()}


def main():
    repo, scratch, output = map(Path, sys.argv[1:])
    spec = importlib.util.spec_from_file_location('capture', ROOT / 'tools/capture_settings_schema.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = {}
    evidence = {}
    for tag in ['4.1.0', '4.1.1', '4.1.2']:
        commit = subprocess.check_output(['git', 'rev-parse', tag + '^{commit}'], cwd=repo, text=True).strip()
        target = scratch / tag
        hashes = {}
        for name in ['ConfigTool/tab_data.cpp', 'src/resources/config_keys.hpp']:
            data = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=repo)
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        raw = module.capture(target, tag, commit)
        # 4.1.2 moved three existing MGS2 fields behind a flag alias. Both
        # #if branches include MGS2; normalizing its union selects those same
        # fields. This is audited static preprocessing, not a runtime export.
        tabs = target / 'ConfigTool/tab_data.cpp'
        text = tabs.read_text(encoding='utf-8-sig')
        aliases = text.count('(kFirstPersonViewGameFlags)')
        if tag == '4.1.2':
            assert aliases == 3 and 'constexpr int kFirstPersonViewGameFlags = MGS2;' in text
            assert 'constexpr int kFirstPersonViewGameFlags = MGS2 | MGS3;' in text
            tabs.write_text(text.replace('(kFirstPersonViewGameFlags)', '(MGS2|MGS3)'))
        else:
            assert aliases == 0
        parsed = module.capture(target, tag, commit)
        results[tag] = parsed
        evidence[tag] = {'commit': commit, 'raw_keys': len(flat(raw['fields'])),
                         'reviewed_union_keys': len(flat(parsed['fields'])),
                         'sections': len(parsed['fields']), 'source_sha256': hashes,
                         'flag_alias_substitutions': aliases}
    fixture = json.loads((ROOT / 'tests/fixtures/hdfix-4.1.0-schema.json').read_text())
    assert results['4.1.0'] == fixture
    a, b = results['4.1.0'], results['4.1.2']
    af, bf = flat(a['fields']), flat(b['fields'])
    ac, bc = flat(a['constraints']), flat(b['constraints'])
    delta = {'added': [[*k, bf[k]] for k in sorted(bf.keys() - af.keys())],
             'removed': [[*k, af[k]] for k in sorted(af.keys() - bf.keys())],
             'type_changes': [[*k, af[k], bf[k]] for k in sorted(af.keys() & bf.keys()) if af[k] != bf[k]],
             'captured_constraint_changes': [[*k, ac.get(k), bc.get(k)] for k in sorted(ac.keys() | bc.keys()) if ac.get(k) != bc.get(k)]}
    result = {'baseline_fixture_equal': True, 'sources': evidence, 'delta': delta,
              'limits': 'Not an actual Config Tool export. Union of MGS2/MGS3 declarations. Existing capture handles only explicit choice lists and known integer ranges; dynamic choices and float bounds/defaults are not fully represented.'}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
