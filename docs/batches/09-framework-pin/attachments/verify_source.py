"""Compare installed copies with the immutable framework release checkout."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


root = Path(__file__).resolve().parents[4]
source = Path(sys.argv[1]).resolve()
revision = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
assert revision == "b036c761ac2af2d47e61a1b473c708f094bd4295", revision
assert not subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=source, text=True).strip()
manifest = json.loads((root / "docs/agents/framework.json").read_text())
assert manifest["framework"]["release"] == "4.0.0"
mapping = {
    "docs/agents/FRAMEWORK.md": "framework/FRAMEWORK.md",
    "docs/agents/roles/brain.md": "framework/roles/brain.md",
    "docs/agents/roles/worker.md": "framework/roles/worker.md",
    "docs/agents/roles/verifier.md": "framework/roles/verifier.md",
    "tools/fw.py": "tools/fw.py",
    "tests/test_framework.py": "templates/tests/test_framework.py",
}
for local, upstream in mapping.items():
    data = (root / local).read_bytes().replace(b"\r\n", b"\n")
    assert data == (source / upstream).read_bytes().replace(b"\r\n", b"\n"), local
    assert hashlib.sha256(data).hexdigest() == manifest["files"][local]["sha256"], local
    print(local, "matches immutable release and manifest")
for name in ("tools/fw.py", "install.py"):
    ast.parse((root / name).read_text(), feature_version=(3, 9))
print("Python 3.9 syntax valid")
subprocess.run([
    "git", "diff", "--exit-code", "15d9277196e7bd1cfbd45fe280a230050b276bed",
    "HEAD", "--", "install.py", "Install-MGS-Mods.cmd", "Install-MGS-Mods.desktop",
], cwd=root, check=True)
print("Installer and both shortcuts unchanged")
print("Checked commit:", subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip())
