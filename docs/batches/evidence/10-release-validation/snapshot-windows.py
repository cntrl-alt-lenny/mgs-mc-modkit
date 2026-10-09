"""Read-only game file snapshot; hashes bytes without distributing contents."""
import argparse
import datetime
import gzip
import hashlib
import json
import re
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--steam-root", required=True, type=Path)
parser.add_argument("--phase", required=True)
parser.add_argument("--output", required=True, type=Path)
parser.add_argument("--managed", action="store_true",
                    help="Hash kit-tracked files, recovery records, saves and executables only")
args = parser.parse_args()
games = []
for name, appid in (("MGS1", "2131630"), ("MGS2", "2131640"),
                    ("MGS3", "2131650")):
    folder = args.steam_root / "steamapps/common" / name
    manifest = args.steam_root / "steamapps" / ("appmanifest_" + appid + ".acf")
    fields = dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]*)"',
                            manifest.read_text() if manifest.is_file() else ""))
    files = []
    record = folder / "mgs-modkit/manifest.json"
    managed = set(json.loads(record.read_text()).get("files", {})) if record.is_file() else set()
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        rel = list(path.relative_to(folder).parts)
        if args.managed and not (rel[0] == "mgs-modkit"
                                 or rel[0].endswith("_savedata_win")
                                 or "/".join(rel) in managed
                                 or path.name.startswith("METAL GEAR SOLID")
                                 and path.suffix.lower() == ".exe"):
            continue
        for index, part in enumerate(rel[:-1]):
            if part.endswith("_savedata_win") and re.fullmatch(r"7656119\d{10}", rel[index + 1]):
                rel[index + 1] = "<account>"
        files.append({"path": "/".join(rel), "bytes": path.stat().st_size,
                      "sha256": digest(path)})
    userdata = []
    for account in sorted((args.steam_root / "userdata").iterdir()):
        target = account / appid
        if not target.is_dir():
            continue
        for path in sorted(target.rglob("*")):
            if path.is_file():
                userdata.append({"path": "userdata/<account>/" + appid + "/"
                                 + path.relative_to(target).as_posix(),
                                 "bytes": path.stat().st_size,
                                 "sha256": digest(path)})
    games.append({"game": name, "appid": appid, "userdata": userdata,
                  "buildid": fields.get("buildid"),
                  "StateFlags": fields.get("StateFlags"), "files": files})
result = {"phase": args.phase,
          "scope": "managed + saves + executables" if args.managed else "all common files + userdata",
          "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "games": games}
raw = (json.dumps(result, indent=2) + "\n").encode("utf-8")
if args.output.suffix == ".gz":
    encoded = gzip.compress(raw, compresslevel=9, mtime=0)
    args.output.write_bytes(encoded)
    print(f"metadata uncompressed bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}")
    print(f"metadata gzip bytes={len(encoded)} sha256={hashlib.sha256(encoded).hexdigest()}")
else:
    args.output.write_bytes(raw)
for game in games:
    print("{} app{} build{} StateFlags{}: {} files, {} bytes".format(
        game["game"], game["appid"], game["buildid"], game["StateFlags"],
        len(game["files"]), sum(row["bytes"] for row in game["files"])))
