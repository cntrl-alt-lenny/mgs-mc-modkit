"""Audit only authenticated 4.1.0 bytes; no general C++ runtime parser."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools.capture_settings_schema import constant_values, without_comments  # noqa: E402

TREE = 'f4f662d67a2a033dee0877e436a0fe65eb719e0b'
HASHES = {'ConfigTool/main.cpp': '99a7051819fb4e6a5c5d623e718fbb8a97548c41a2ac0043f86094955fc0eabc', 'ConfigTool/tab_data.cpp': 'f96e385ad00e144d838466a28cad5ccaf447b4312900d27121ba115f49241561', 'src/resources/config.cpp': '18581108db3ced5866d00bb31d6300abed2d5f5ec4db5dc1a156e9560add1f73', 'src/resources/config_keys.hpp': '67f699e684014a56aedb8b0a4d12c64022f46d1d49807a5d6d3b41f790f6a3df'}
root = Path(sys.argv[1])
assert subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip() == TREE
for name, digest in HASHES.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
constant = constant_values(without_comments((root / 'src/resources/config_keys.hpp').read_text(encoding='utf-8-sig')))
source = without_comments((root / 'src/resources/config.cpp').read_text(encoding='utf-8-sig'))
pattern = r'(?:ConfigHelper::getValue|InputHandler::GetKeybind)\(ini,\s*ConfigKeys::(\w+),\s*ConfigKeys::(\w+)'
calls = re.findall(pattern, source)
# Ensure every call, including conditional/hotkey reads, is covered by this spelling.
assert len(calls) == len(re.findall(r'(?:ConfigHelper::getValue|InputHandler::GetKeybind)\(', source)) == 133
reads = {}
for section, key in calls:
    reads.setdefault(constant(section), set()).add(constant(key))
result = {'tree': TREE, 'reads': {s: sorted(keys) for s, keys in sorted(reads.items())}}
fixture = Path(__file__).resolve().parents[4] / 'tests/fixtures/hdfix-4.1.0-runtime-reads.json'
assert result == json.loads(fixture.read_text())
print(json.dumps({'source_sha256': HASHES, 'calls': len(calls), 'runtime': result}, indent=2))
