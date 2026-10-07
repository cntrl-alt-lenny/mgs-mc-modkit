"""Read-only candidate shortcut checks; run from the repository root."""

import ast
import hashlib
from pathlib import Path
import re


source = Path("install.py").read_bytes()
tree = ast.parse(source)
version = next(
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "MODKIT_VERSION"
            for target in node.targets)
)
digest = hashlib.sha256(source).hexdigest()
assert b"\r" not in source, "Installer must use LF"
print("MODKIT_VERSION=" + version)
print("install.py SHA-256=" + digest)
print("install.py: LF only")
for filename, tag_pattern, sha_pattern in (
    ("Install-MGS-Mods.desktop", rb"TAG=([^;]+);", rb"SHA=([0-9a-f]{64});"),
    ("Install-MGS-Mods.cmd", rb'set "TAG=([^"]+)"', rb'set "SHA=([^"]+)"'),
):
    data = Path(filename).read_bytes()
    tags = re.findall(tag_pattern, data)
    hashes = re.findall(sha_pattern, data)
    assert tags == [("v" + version).encode()], (filename, tags)
    assert hashes == [digest.encode()], (filename, hashes)
    if filename.endswith(".cmd"):
        assert b"\r\n" in data, "No CRLF found"
        remainder = data.replace(b"\r\n", b"")
        assert b"\r" not in remainder and b"\n" not in remainder, "Mixed endings"
        endings = "CRLF only"
    else:
        assert b"\r" not in data, "Desktop file must use LF"
        endings = "LF only"
    print("{}: TAG={}, SHA={}, {}".format(
        filename, tags[0].decode(), hashes[0].decode(), endings))
assert Path("docs/releases/v" + version + ".md").is_file(), "Missing release notes"
print("Versioned release notes exist; both shortcut pins match")
