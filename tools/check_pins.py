#!/usr/bin/env python3
"""Report when an upstream mod has released a version newer than we pin.

ALERT ONLY — this never edits install.py. Bumping a mod is a deliberate act:
the pinned versions are a tested, internally-consistent SET. Upstream releases
have removed fixes on the assumption that a newer MGSHDFix supplies them, so
half-updating the stack silently loses fixes. See docs/UPGRADING.md.

    python3 tools/check_pins.py          # human-readable report
    python3 tools/check_pins.py --json   # machine-readable, for CI

Exit codes:  0 = everything current   1 = an update exists   2 = check failed
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install  # noqa: E402


def pinned() -> list[dict]:
    """What install.py currently pins, read from the module itself."""
    return [
        {"what": "MGSHDFix (MGS2/MGS3)",
         "repo": "ShizCalev/MGSHDFix",
         "pin": install.HDFIX_VERSION},
        {"what": "MGS2 Community Bugfix Compilation",
         "repo": "ShizCalev/MGS2-Community-Bugfix-Compilation",
         "pin": install.GAMES["mgs2"]["bugfix_version"]},
        {"what": "MGS3 Community Bugfix Compilation",
         "repo": "ShizCalev/MGS3-Community-Bugfix-Compilation",
         "pin": install.GAMES["mgs3"]["bugfix_version"]},
        {"what": "MGSM2Fix (MGS1)",
         "repo": "nuggslet/MGSM2Fix",
         "pin": install.M2FIX_TAG},
    ]


def latest_tag(repo: str) -> str:
    """Newest release tag for `repo` (raises on network/API failure)."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={"User-Agent": install.UA,
                 "Accept": "application/vnd.github+json"})
    # CI passes a token to dodge the 60/hour anonymous rate limit.
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["tag_name"]


def norm(tag: str) -> str:
    """Compare tags ignoring a leading 'v' — upstream is inconsistent."""
    return tag.strip().lstrip("vV")


def check() -> tuple[list[dict], list[str]]:
    rows, errors = [], []
    for item in pinned():
        try:
            newest = latest_tag(item["repo"])
        except (urllib.error.URLError, urllib.error.HTTPError,
                KeyError, ValueError, TimeoutError) as e:
            errors.append(f"{item['repo']}: {e}")
            continue
        item = dict(item, latest=newest,
                    outdated=norm(newest) != norm(item["pin"]))
        rows.append(item)
    return rows, errors


def main() -> int:
    rows, errors = check()
    outdated = [r for r in rows if r["outdated"]]

    if "--json" in sys.argv:
        print(json.dumps({"rows": rows, "errors": errors,
                          "outdated": len(outdated)}, indent=2))
    else:
        for r in rows:
            mark = "UPDATE" if r["outdated"] else "  ok  "
            extra = f"  ->  {r['latest']}" if r["outdated"] else ""
            print(f"[{mark}] {r['what']:38} pinned {r['pin']}{extra}")
        for e in errors:
            print(f"[ FAIL ] {e}")
        if outdated:
            print(f"\n{len(outdated)} update(s) available. These are NOT "
                  "drop-in bumps — read docs/UPGRADING.md before changing "
                  "anything.")
        elif not errors:
            print("\nAll pinned mod versions are current.")

    if errors:
        return 2
    return 1 if outdated else 0


if __name__ == "__main__":
    raise SystemExit(main())
