"""Read-only presence/build audit after actual candidate removal."""
import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--steam-root", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
rows = []
for game, appid, exe in (
    ("MGS1", "2131630", "METAL GEAR SOLID.exe"),
    ("MGS2", "2131640", "METAL GEAR SOLID2.exe"),
    ("MGS3", "2131650", "METAL GEAR SOLID3.exe"),
):
    root = args.steam_root / "steamapps/common" / game
    manifest = args.steam_root / "steamapps" / ("appmanifest_" + appid + ".acf")
    fields = dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]*)"', manifest.read_text()))
    names = (
        "winhttp.dll", "wininet.dll", "d3d11.dll", "dinput8.dll",
        "MGSM2Fix64.asi", "MGSM2Fix.ini", "plugins/MGSHDFix.asi",
        "plugins/MGSHDFix.settings", "mgs-modkit", "mgs-modkit/manifest.json",
        "mgs-modkit/journal.json", "mgs-modkit/backups", "mgs-modkit/rollback",
        "mgs-modkit/staging", "logs", "steam_appid.txt", "MGSM2Fix.log",
    )
    rows.append({
        "game": game, "appid": appid, "buildid": fields.get("buildid"),
        "StateFlags": fields.get("StateFlags"),
        "exe_sha256": hashlib.sha256((root / exe).read_bytes()).hexdigest(),
        "paths_present": {name: (root / name).exists() for name in names},
    })
result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "games": rows}
args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
