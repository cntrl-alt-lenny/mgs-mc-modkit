"""Task evidence: set valid local custom preferences before preservation trial."""
import argparse
import configparser
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import install  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--steam-root", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
changes = {
    "MGS1": {"External Resolution": {"Width": "1024", "Height": "768"}},
    "MGS2": {"Language Settings": {"Game Language": '"fr"'},
             "Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)":
             {"Render Width": "1280", "Render Height": "720"}},
    "MGS3": {"Language Settings": {"Game Language": '"es"'},
             "Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)":
             {"Render Width": "1600", "Render Height": "900"}},
}
rows = []
for game, sections in changes.items():
    relative = "MGSM2Fix.ini" if game == "MGS1" else "plugins/MGSHDFix.settings"
    path = args.steam_root / "steamapps/common" / game / relative
    raw = path.read_bytes()
    original = raw.decode("utf-8-sig")
    text = original
    before_values = {}
    for section, keys in sections.items():
        pattern = re.compile(r"(?ms)(^\[" + re.escape(section) + r"\]\r?\n)(.*?)(?=^\[|\Z)")
        matched = pattern.search(text)
        assert matched, section
        block = matched.group(2)
        for key, value in keys.items():
            line = re.compile(r"(?m)^(" + re.escape(key) + r"\s*=\s*)([^\r\n]*)")
            found = line.search(block)
            assert found, key
            before_values[f"{section}/{key}"] = found.group(2)
            block, count = line.subn(lambda item: item.group(1) + value, block)
            assert count == 1
        text = text[:matched.start(2)] + block + text[matched.end(2):]
    if game != "MGS1":
        install.validate_settings(text)
    else:
        checked = configparser.ConfigParser()
        checked.read_string(text)
        assert checked.getint("External Resolution", "Width") == 1024
        assert checked.getint("External Resolution", "Height") == 768
    updated = text.encode("utf-8")
    path.write_bytes(updated)
    row = {"game": game, "path": relative,
           "before_sha256": hashlib.sha256(raw).hexdigest(),
           "after_sha256": hashlib.sha256(updated).hexdigest(),
           "before_values": before_values, "chosen_values": sections,
           "validation": "candidate validator passed" if game != "MGS1" else "INI dimensions parsed"}
    rows.append(row)
    print(json.dumps(row, sort_keys=True))
args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
