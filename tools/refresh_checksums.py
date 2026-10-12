#!/usr/bin/env python3
"""Print the SHA-256 of every auto-downloaded mod archive install.py pins.

Run this after bumping a mod version (HDFIX_VERSION / M2FIX_VERSION / a game's
bugfix_version + bugfix_url) to get the hash to paste into the matching
*_SHA256 constant. It downloads each archive to a temp file, hashes it, and
compares against what install.py currently pins so drift is obvious.

    python3 tools/refresh_checksums.py

Nothing is written to install.py — copy the printed values in by hand so the
change is reviewable.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install  # noqa: E402


def sha256_url(url: str) -> str:
    h = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": install.UA})
    with urllib.request.urlopen(req, timeout=300) as r, \
            tempfile.NamedTemporaryFile() as f:
        while chunk := r.read(1024 * 256):
            h.update(chunk)
            f.write(chunk)
    return h.hexdigest()


def main() -> int:
    targets = [
        ("PATRIOT_SHA256", install.PATRIOT_URL, install.PATRIOT_SHA256),
        ("HDFIX_SHA256", install.HDFIX_URL, install.HDFIX_SHA256),
        ("M2FIX_SHA256", install.M2FIX_URL, install.M2FIX_SHA256),
        ("GAMES['mgs2']['bugfix_sha256']", install.GAMES["mgs2"]["bugfix_url"],
         install.GAMES["mgs2"]["bugfix_sha256"]),
        ("GAMES['mgs3']['bugfix_sha256']", install.GAMES["mgs3"]["bugfix_url"],
         install.GAMES["mgs3"]["bugfix_sha256"]),
    ]
    drift = False
    for name, url, pinned in targets:
        print(f"\n{name}\n  {url}")
        got = sha256_url(url)
        ok = got.lower() == pinned.lower()
        drift = drift or not ok
        print(f"  pinned: {pinned}")
        print(f"  actual: {got}   {'✓ match' if ok else '✗ MISMATCH — update it'}")
    if drift:
        print("\nOne or more pins are out of date; update install.py.")
        return 1
    print("\nAll pinned checksums match the live release assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
