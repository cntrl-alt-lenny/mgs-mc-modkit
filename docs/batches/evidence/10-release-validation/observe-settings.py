"""Read selected installed preferences for validation evidence only."""
import argparse
import configparser
import datetime
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--steam-root", required=True, type=Path)
parser.add_argument("--phase", required=True)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
games = []
for game in ("MGS1", "MGS2", "MGS3"):
    relative = "MGSM2Fix.ini" if game == "MGS1" else "plugins/MGSHDFix.settings"
    path = args.steam_root / "steamapps/common" / game / relative
    row = {"game": game, "path": relative, "exists": path.is_file()}
    if path.is_file():
        raw = path.read_bytes()
        settings = configparser.ConfigParser()
        settings.optionxform = str
        settings.read_string(raw.decode("utf-8-sig"))
        wanted = ("External Resolution", "Internal Resolution", "Launcher") if game == "MGS1" else (
            "Language Settings", "Controller Settings", "Launcher and Splashscreens",
            "Internal Resolution / Render Scale (+ Downsampling / Supersampling / 21:9+ and 4:3 Support)")
        row.update(sha256=hashlib.sha256(raw).hexdigest(),
                   values={section: dict(settings[section]) for section in wanted})
    games.append(row)
result = {"phase": args.phase, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "games": games}
args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, sort_keys=True))
