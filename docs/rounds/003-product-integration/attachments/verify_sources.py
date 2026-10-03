"""Verify integration bytes against the literal product and adoption sources."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRODUCT = "7630a81a04abf4e7f96dd75663bae70ba31c4f2e"
BASELINE = "e5c50788b15bed5bf43e6a52529ebb0067f9a9b1"
FRAMEWORK = "eca1306dc43cb81f0df3ee42f841812da68e8b1e"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    framework = Path(sys.argv[1])
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=framework).decode().strip() == FRAMEWORK
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=framework)
    product_files = git("ls-tree", "-r", "--name-only", PRODUCT).decode().splitlines()
    for name in product_files:
        assert (ROOT / name).read_bytes() == git("show", f"{PRODUCT}:{name}"), name
    print(f"All {len(product_files)} product files match reviewed source {PRODUCT}")
    names = git("diff", "--name-only", PRODUCT, "HEAD").decode().splitlines()
    print("Files differing from reviewed source (adoption and round records only):")
    for name in names:
        assert name in {"AGENTS.md", ".worktrees/.gitignore", "tools/fw.py", "tests/test_framework.py", "docs/state.md"} or name.startswith(("docs/agents/", "docs/rounds/")), name
        print("  " + name)
    manifest = json.loads((ROOT / "docs/agents/framework.json").read_text())
    assert manifest["framework"]["release"] == "3.1.0"
    for name, entry in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        assert data == git("show", f"{BASELINE}:{name}"), name
        if entry["kind"] == "copy":
            source = ("framework/" + name.removeprefix("docs/agents/") if name.startswith("docs/agents/")
                      else "templates/tests/test_framework.py" if name == "tests/test_framework.py" else name)
            assert data == (framework / source).read_bytes(), name
            assert hashlib.sha256(data).hexdigest() == entry["sha256"], name
            print("Framework source/fingerprint match: " + name)
    assert (ROOT / "docs/agents/framework.json").read_bytes() == git("show", f"{BASELINE}:docs/agents/framework.json")
    print("All adoption manifest paths and the manifest match merged baseline")
    source = (ROOT / "install.py").read_bytes()
    tree = ast.parse(source, feature_version=(3, 9))
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    print("Python 3.9 installer syntax valid")
    for key in ("HDFIX_VERSION", "HDFIX_SHA256", "M2FIX_VERSION", "M2FIX_TAG", "M2FIX_SHA256", "SETTINGS_CAPTURED_FROM"):
        print(f"{key}={values[key]}")
    print("Configuration schema and capture fixture match reviewed source byte-for-byte")
    digest = hashlib.sha256(source).hexdigest()
    tag = "v" + values["MODKIT_VERSION"]
    for name in ("Install-MGS-Mods.desktop", "Install-MGS-Mods.cmd"):
        data = (ROOT / name).read_bytes()
        assert f"TAG={tag}".encode() in data
        assert f"SHA={digest}".encode() in data
        if name.endswith(".cmd"):
            assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b"")
        print(f"{name}: TAG={tag} SHA={digest}; reviewed bytes and line endings preserved")


if __name__ == "__main__":
    main()
