#!/usr/bin/env python3
"""Capture the pinned Config Tool's MGS2/MGS3 fields independently of install.py.

Input is a reviewed upstream checkout. Supports the 4.1.0 declaration layout;
changed upstream syntax requires reviewing this extractor, not guessing keys.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def capture(root, tag, tree):
    sources = ["ConfigTool/tab_data.cpp", "src/resources/config_keys.hpp"]
    tabs = (root / sources[0]).read_text(encoding="utf-8-sig")
    keys = (root / sources[1]).read_text(encoding="utf-8-sig")
    constants = dict(re.findall(r'constexpr const char\*\s+(\w+)\s*=\s*"([^"\n]*)";', keys))
    for name, alias in re.findall(r"constexpr const char\*\s+(\w+)\s*=\s*(\w+)\s*;", keys):
        constants[name] = constants[alias]
    fields, constraints = {}, {}
    pattern = (r"\{\s*\(([^)]+)\),\s*ConfigKeys::(\w+)_Section,\s*"
               r"ConfigKeys::(\w+)_Setting,(.*?)(?=\{\s*\(|\Z)")
    for match in re.finditer(pattern, tabs, re.S):
        flags, section_id, key_id, body = match.groups()
        if "MGS2" not in flags and "MGS3" not in flags:
            continue
        section, key = constants[section_id + "_Section"], constants[key_id + "_Setting"]
        kind = re.search(r"Field::(\w+)", body).group(1)
        fields.setdefault(section, {})[key] = kind
        constraint = {}
        if kind == "Choice":
            options = re.search(r"Field::Choice,\s*[^,]*,\s*[^,]*,\s*[^,]*,\s*[^,]*,\s*\{([^}]*)\}", body)
            if options:
                values = [constants[a] if a else b for a, b in
                          re.findall(r'ConfigKeys::(\w+)|"([^"]*)"', options.group(1))]
                if values:
                    constraint["choices"] = values
        elif kind == "Int":
            bounds = re.search(r"Field::Int,\s*[^,]+,\s*([^,]+),\s*([^,}]+)", body)
            if bounds:
                known = {"D3D11_REQ_TEXTURE2D_U_OR_V_DIMENSION": 16384,
                         "D3D11_DEFAULT_MAX_ANISOTROPY": 16}
                values = [int(v.strip()) if v.strip().isdigit() else known.get(v.strip())
                          for v in bounds.groups()]
                if None not in values:
                    constraint["range"] = values
        if constraint:
            constraints.setdefault(section, {})[key] = constraint
    if not fields:
        raise RuntimeError("No fields recognized; review the upstream declaration format")
    return {"upstream": "ShizCalev/MGSHDFix", "tag": tag, "tree": tree,
            "sources": sources,
            "fields": {s: dict(sorted(fields[s].items())) for s in sorted(fields)},
            "constraints": constraints,
            "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                              for name in sources}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_checkout", type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--tree", required=True)
    args = parser.parse_args()
    print(json.dumps(capture(args.upstream_checkout, args.tag, args.tree), indent=2))


if __name__ == "__main__":
    main()
