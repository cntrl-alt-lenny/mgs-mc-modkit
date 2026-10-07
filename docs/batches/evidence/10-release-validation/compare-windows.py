"""Compare observed snapshots; no game files or payload contents are read."""
import argparse
import gzip
import json
from pathlib import Path


def read(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8-sig"))


def values(rows):
    # Historical snapshots used <account> for the single root bugfix version
    # cache file. Keep originals immutable; normalize only this verified alias.
    result = {}
    for row in rows:
        path = row["path"]
        parts = path.split("/")
        if len(parts) == 2 and parts[1] == "<account>" and parts[0].endswith("_savedata_win"):
            game = parts[0].removesuffix("_savedata_win").upper()
            path = parts[0] + "/" + game + "-Community-Bugfix-Compilation_version_check.txt"
        assert path not in result, "Snapshot path collision: " + path
        result[path] = (row["bytes"], row["sha256"])
    return result


parser = argparse.ArgumentParser()
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
before, after = read(args.before), read(args.after)
results = []
for old_game, new_game in zip(before["games"], after["games"]):
    assert old_game["game"] == new_game["game"]
    old, new = values(old_game["files"]), values(new_game["files"])
    old_saves = {key: value for key, value in old.items()
                 if key.split("/")[0].endswith("_savedata_win")}
    new_saves = {key: value for key, value in new.items()
                 if key.split("/")[0].endswith("_savedata_win")}
    old_userdata, new_userdata = values(old_game["userdata"]), values(new_game["userdata"])
    backups = {key.removeprefix("mgs-modkit/backups/"): value
               for key, value in new.items() if key.startswith("mgs-modkit/backups/")}
    backup_mismatches = [key for key, value in backups.items()
                         if old.get("mgs-modkit/backups/" + key, old.get(key)) != value]
    result = {"game": old_game["game"], "before_files": len(old),
              "after_files": len(new), "original_backups": len(backups),
              "backup_mismatches_against_before": backup_mismatches,
              "save_changes": [key for key in sorted(old_saves.keys() | new_saves.keys())
                               if old_saves.get(key) != new_saves.get(key)],
              "userdata_changes": [key for key in sorted(old_userdata.keys() | new_userdata.keys())
                                   if old_userdata.get(key) != new_userdata.get(key)],
              "shared_file_changes": [key for key in sorted(old.keys() & new.keys())
                                      if old[key] != new[key]],
              "before_only_snapshot_files": sorted(old.keys() - new.keys())
              if before.get("scope", "all common files + userdata")
              == after.get("scope", "all common files + userdata") else None,
              "added_files": sorted(new.keys() - old.keys())}
    results.append(result)
report = {"before_phase": before["phase"], "after_phase": after["phase"],
          "before_scope": before.get("scope", "all common files + userdata"),
          "after_scope": after.get("scope", "all common files + userdata"),
          "games": results}
args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
for row in results:
    print(f"{row['game']}: {row['original_backups']} original backup hashes compared, "
          f"{len(row['backup_mismatches_against_before'])} mismatch; "
          f"save changes={row['save_changes']}; userdata changes={row['userdata_changes']}")
