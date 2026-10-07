"""Read-only source/protected-copy comparison; emits portable metadata only."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--steam-root", type=Path, required=True)
parser.add_argument("--protected-root", type=Path, required=True)
args = parser.parse_args()
rows = []
for path in sorted(args.protected_root.rglob("*")):
    if not path.is_file() or path.name == "protected-hashes.csv":
        continue
    rel = path.relative_to(args.protected_root)
    source = (args.steam_root / rel if rel.parts[0] == "userdata"
              else args.steam_root / "steamapps/common" / rel)
    portable = list(rel.parts)
    if portable[0] == "userdata":
        portable[1] = "<account>"
    elif len(portable) > 2 and portable[1].endswith("_savedata_win"):
        portable[2] = "<account>"
    copied_hash = digest(path)
    source_hash = digest(source) if source.is_file() else None
    rows.append({"path": "/".join(portable), "bytes": path.stat().st_size,
                 "source_sha256": source_hash, "protected_sha256": copied_hash,
                 "equal": source_hash == copied_hash})
print(json.dumps({"files": rows, "count": len(rows),
                  "bytes": sum(row["bytes"] for row in rows),
                  "all_equal": all(row["equal"] for row in rows)}, indent=2))
raise SystemExit(0 if all(row["equal"] for row in rows) else 1)
