#!/usr/bin/env python3
"""Pin both launchers to this installer/version, preserving Windows CRLF."""
from pathlib import Path
import hashlib
import re


def main():
    root = Path(__file__).resolve().parents[1]
    source = (root / "install.py").read_bytes()
    version = re.search(rb'^MODKIT_VERSION = "([^"]+)"', source, re.M).group(1).decode()
    digest = hashlib.sha256(source).hexdigest()
    patterns = {
        "Install-MGS-Mods.desktop": [(rb"TAG=[^;]+", f"TAG=v{version}"),
                                      (rb"SHA=[0-9a-f]{64}", f"SHA={digest}")],
        "Install-MGS-Mods.cmd": [(rb'set "TAG=[^"]+"', f'set "TAG=v{version}"'),
                                  (rb'set "SHA=[^"]+"', f'set "SHA={digest}"')],
    }
    for filename, replacements in patterns.items():
        path = root / filename
        data = path.read_bytes()
        for pattern, replacement in replacements:
            data, count = re.subn(pattern, replacement.encode(), data)
            if count != 1:
                raise RuntimeError(f"Expected exactly one pin for {filename}: {pattern!r}")
        if filename.endswith(".cmd"):
            data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        path.write_bytes(data)
        print(f"{filename}: v{version} / {digest}")


if __name__ == "__main__":
    main()
