"""Fresh source/checkout authentication and compiled-header refusal."""

from pathlib import Path
import json
import hashlib
import subprocess
import sys

seat = Path(sys.argv[1]).resolve()
source = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(seat))
from tools.capture_patriot_schema import capture  # noqa: E402 - select the exact isolated delivery first

fixture = json.loads((seat / "tests/fixtures/patriotfix-0.2.2-schema.json").read_text())
assert capture(source) == fixture
print(
    "Reviewed SHA:",
    subprocess.check_output(
        ["git", "-C", str(seat), "rev-parse", "HEAD"], text=True
    ).strip(),
)
assert (
    subprocess.check_output(
        ["git", "-C", str(source), "ls-remote", "origin", "refs/tags/0.2.2"], text=True
    ).split()[0]
    == fixture["tree"]
)
for name in fixture["source_sha256"]:
    blob = subprocess.check_output(
        ["git", "-C", str(source), "show", fixture["tree"] + ":" + name]
    )
    attr = (
        subprocess.check_output(
            ["git", "-C", str(source), "check-attr", "eol", "--", name], text=True
        )
        .strip()
        .split(": ")[-1]
    )
    checkout = (
        blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") if attr == "crlf" else blob
    )
    assert hashlib.sha256(checkout).hexdigest() == fixture["source_sha256"][name]
    assert (source / name).read_bytes() == checkout
print(
    "Official tag and 61 literal blob/checkout hashes: PASS; exact fixture reproduced"
)
for name in ("ConfigTool/pch.h", "src/resources/stdafx.h", "src/resources/version.h"):
    path = source / name
    original = path.read_bytes()
    for mode in ("modified", "omitted"):
        if mode == "modified":
            path.write_bytes(original + b"\n#error unreviewed compiled header\n")
        else:
            path.unlink()
        try:
            capture(source)
        except ValueError as err:
            print(name, mode, "refused:", err)
        else:
            raise AssertionError("header drift accepted")
        finally:
            path.write_bytes(original)
new = source / "src/unreviewed-brain.h"
new.write_bytes(b"#error unreviewed")
try:
    capture(source)
except ValueError as err:
    print("Added header refused:", err)
else:
    raise AssertionError("added header accepted")
finally:
    new.unlink()
assert capture(source) == fixture
print("Source restored; native binaries NOT RUN")
