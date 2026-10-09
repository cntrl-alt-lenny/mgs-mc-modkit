#!/usr/bin/env python3
"""Read-only candidate archive/source/export checks; never authorize adoption.

See docs/upgrades/volume1-2026-10-09.md for native capture instructions.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import io
import json
import math
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

import capture_settings_schema as capture

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/upgrades/volume1-candidate.json"
SCHEMA = ROOT / "tests/fixtures/hdfix-4.1.2-candidate-schema.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def source_check(root, identity):
    """Compare tag, HEAD, and every audited byte with the official commit."""
    for ref in ("HEAD", "refs/tags/" + identity["tag"]):
        if git(root, "rev-parse", ref + "^{commit}").decode().strip() != identity["commit"]:
            raise ValueError("source commit/tag mismatch: " + ref)
    for name, expected in identity["source_sha256"].items():
        data = (root / name).read_bytes()
        if digest(data) != expected:
            raise ValueError("source bytes mismatch: " + name)
        blob = git(root, "show", identity["commit"] + ":" + name)
        if digest(blob) != identity["git_blob_sha256"][name]:
            raise ValueError("source git blob mismatch: " + name)
        # Upstream's committed .gitattributes requests CRLF for C++ files.
        # Record both identities and permit only that exact checkout transform.
        if identity["checkout_eol"][name] == "crlf":
            if b"\r" in blob:
                raise ValueError("reviewed git blob must be LF: " + name)
            blob = blob.replace(b"\n", b"\r\n")
        if data != blob:
            raise ValueError("source bytes mismatch: " + name)
    schema = capture.capture(root, identity["tag"], identity["commit"])
    expected_schema = json.loads(SCHEMA.read_text())
    if schema != expected_schema:
        raise ValueError("canonical capture differs from reviewed candidate")
    constants = capture.constant_values(capture.without_comments(
        (root / "src/resources/config_keys.hpp").read_text(encoding="utf-8-sig")))
    runtime = capture.without_comments(
        (root / "src/resources/config.cpp").read_text(encoding="utf-8-sig"))
    # Bounded to the hashed, reviewed file: no claim of a general C++ parser.
    pattern = (r"(?:ConfigHelper::getValue|InputHandler::GetKeybind)\s*\(\s*ini\s*,"
               r"\s*ConfigKeys::(\w+_Section)\s*,\s*ConfigKeys::(\w+_Setting)\s*,")
    reads = {}
    for section, key in re.findall(pattern, runtime):
        reads.setdefault(constants(section), set()).add(constants(key))
    reads = {s: sorted(keys) for s, keys in sorted(reads.items())}
    if reads != identity["runtime_reads"]:
        raise ValueError("runtime reads differ from reviewed candidate")
    if reads != {s: sorted(keys) for s, keys in schema["fields"].items()}:
        raise ValueError("runtime/UI field mismatch")
    return {"commit": identity["commit"], "fields": sum(map(len, reads.values())),
            "native_exports": "not established by source"}


def archive_check(path, asset):
    """Hash and CRC-check without extracting; reject ambiguous/unsafe layouts."""
    with path.open("rb") as stream:
        h = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    if h.hexdigest() != asset["sha256"] or path.stat().st_size != asset["size"]:
        raise ValueError("archive digest/size mismatch: " + path.name)
    with zipfile.ZipFile(path) as archive:
        names = []
        folded = set()
        for member in archive.infolist():
            name = member.filename
            parts = PurePosixPath(name).parts
            if (not parts or name.startswith("/") or "\\" in name or ":" in name
                    or any(p in {"..", "."} for p in name.rstrip("/").split("/"))
                    or (member.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError("unsafe archive path: " + name)
            if name.casefold() in folded:
                raise ValueError("duplicate archive path: " + name)
            folded.add(name.casefold())
            names.append(name)
        if sorted(names) != asset["members"]:
            raise ValueError("archive layout mismatch: " + path.name)
        if not set(asset.get("required_members", [])) <= set(names):
            raise ValueError("installer-required members missing: " + path.name)
        bad = archive.testzip()
        if bad:
            raise ValueError("archive CRC mismatch: " + bad)
        for name, expected in asset.get("payload_sha256", {}).items():
            if digest(archive.read(name)) != expected:
                raise ValueError("payload digest mismatch: " + name)
    return {"asset": path.name, "sha256": h.hexdigest(), "members": len(names), "crc": "pass"}


def parse_export(data, schema):
    if b"\n" not in data or b"\n" in data.replace(b"\r\n", b""):
        raise ValueError("native export must retain CRLF bytes")
    parser = configparser.ConfigParser(interpolation=None, strict=True,
                                       delimiters=("=",), empty_lines_in_values=False)
    parser.optionxform = str
    parser.read_file(io.StringIO(data.decode("utf-8-sig")))
    if parser.defaults():
        raise ValueError("DEFAULT inheritance is unsupported")
    fields = {s: dict(parser.items(s)) for s in parser.sections()}
    if {s: set(keys) for s, keys in fields.items()} != {
            s: set(keys) for s, keys in schema["fields"].items()}:
        raise ValueError("export section/key mismatch (including hidden fields)")
    for section, keys in schema["fields"].items():
        for key, kind in keys.items():
            raw = fields[section][key]
            value = raw
            if kind in {"Choice", "Str", "Hotkey"}:
                # Config Tool QuoteIfNeeded wraps literal text, without JSON escaping.
                if raw.startswith('"') and raw.endswith('"'):
                    value = raw[1:-1]
                elif '"' in raw:
                    raise ValueError("malformed string: " + key)
            elif kind == "Bool":
                if raw not in {"0", "1"}:
                    raise ValueError("invalid bool: " + key)
            elif kind == "Int":
                if not re.fullmatch(r"-?\d+", raw):
                    raise ValueError("invalid integer: " + key)
                value = int(raw)
            elif kind == "Float":
                value = float(raw)
                if not math.isfinite(value):
                    raise ValueError("non-finite float: " + key)
            constraint = schema["constraints"].get(section, {}).get(key, {})
            if "choices" in constraint and value not in constraint["choices"]:
                raise ValueError("invalid static choice: " + key)
            if "range" in constraint and not constraint["range"][0] <= value <= constraint["range"][1]:
                raise ValueError("out of range: " + key)
            fields[section][key] = value
    return fields


def bundle_file(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("capture file outside bundle or missing")
    return path.read_bytes()


def dynamic_fields(schema):
    return {(s, k) for s, keys in schema["fields"].items() for k, kind in keys.items()
            if kind in {"Hotkey", "Float"} or
            (kind == "Choice" and "choices" not in schema["constraints"].get(s, {}).get(k, {})) or
            (kind == "Int" and "range" not in schema["constraints"].get(s, {}).get(k, {}))}


def export_check(bundle, manifest, schema):
    """Validate declared capture provenance; human review must confirm it is real."""
    metadata = json.loads((bundle / "capture.json").read_text())
    asset = next(a for a in manifest["assets"] if a["id"] == "hdfix")
    if metadata.get("tag") != "4.1.2" or metadata.get("archive_sha256") != asset["sha256"]:
        raise ValueError("capture package identity mismatch")
    if metadata.get("config_tool_sha256") != asset["payload_sha256"]["plugins/MGSHDFix Config Tool.exe"]:
        raise ValueError("capture executable identity mismatch")
    if metadata.get("platform") not in {"Windows", "Proton"}:
        raise ValueError("native platform required")
    for key in ("captured_utc", "platform_version", "operator", "procedure", "observations"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError("missing provenance: " + key)
    if set(metadata.get("games", {})) != {"mgs2", "mgs3"}:
        raise ValueError("both per-game captures required")
    dynamic = dynamic_fields(schema)
    values = {}
    for game, record in metadata["games"].items():
        values[game] = {}
        for profile in ("default", "kit"):
            entry = record[profile]
            data = bundle_file(bundle, entry["file"])
            if digest(data) != entry["sha256"]:
                raise ValueError("export byte hash mismatch")
            values[game][profile] = parse_export(data, schema)
        observed = record["dynamic_fields"]
        if {(s, k) for s, keys in observed.items() for k in keys} != dynamic:
            raise ValueError("dynamic choice/hotkey/float observations incomplete")
        for s, k in dynamic:
            row = observed[s][k]
            if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
                raise ValueError("missing dynamic UI evidence reference")
            for profile in ("default", "kit"):
                value = values[game][profile][s][k]
                if row.get(profile) != value:
                    raise ValueError("dynamic observation/export mismatch")
                if schema["fields"][s][k] == "Choice" and value not in row.get("choices", []):
                    raise ValueError("dynamic choice absent from observed UI list")
                if schema["fields"][s][k] in {"Float", "Int"}:
                    bounds = row.get("range", [])
                    if (len(bounds) != 2 or any(type(b) not in {int, float} or not math.isfinite(b)
                                               for b in bounds) or not bounds[0] <= value <= bounds[1]):
                        raise ValueError("dynamic numeric range missing/invalid")
    differences = {}
    for profile in ("default", "kit"):
        differences[profile] = {s: {k: {g: values[g][profile][s][k] for g in values}
                                   for k in keys if values["mgs2"][profile][s][k] !=
                                   values["mgs3"][profile][s][k]}
                                for s, keys in schema["fields"].items()}
        differences[profile] = {s: keys for s, keys in differences[profile].items() if keys}
    return {"structural_validation": "pass", "per_game_differences": differences,
            "adoption": "still requires independent provenance/defaults/native review"}


def capture_template(manifest, schema):
    asset = next(a for a in manifest["assets"] if a["id"] == "hdfix")
    games = {}
    for game in ("mgs2", "mgs3"):
        record = {p: {"file": game + "-" + p + ".settings", "sha256": ""}
                  for p in ("default", "kit")}
        record["dynamic_fields"] = {}
        for s, keys in schema["fields"].items():
            for k, kind in keys.items():
                if (s, k) in dynamic_fields(schema):
                    row = {"default": None, "kit": None, "evidence": ""}
                    if kind == "Choice":
                        row["choices"] = []
                    if kind in {"Float", "Int"}:
                        row["range"] = []
                    record["dynamic_fields"].setdefault(s, {})[k] = row
        games[game] = record
    return {"tag": "4.1.2", "archive_sha256": asset["sha256"],
            "config_tool_sha256": asset["payload_sha256"]["plugins/MGSHDFix Config Tool.exe"],
            "platform": "", "platform_version": "", "captured_utc": "", "operator": "",
            "procedure": "", "observations": "", "games": games}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, help="directory of exact official candidate ZIPs")
    parser.add_argument("--source", type=Path, help="MGSHDFix checkout at reviewed tag/commit")
    parser.add_argument("--exports", type=Path, help="native capture bundle with capture.json")
    parser.add_argument("--capture-template", action="store_true", help="print blank native metadata form")
    args = parser.parse_args()
    if not any((args.archives, args.source, args.exports, args.capture_template)):
        parser.error("select at least one check")
    manifest = json.loads(MANIFEST.read_text())
    if args.capture_template:
        if any((args.archives, args.source, args.exports)):
            parser.error("capture template must be requested separately")
        print(json.dumps(capture_template(manifest, json.loads(SCHEMA.read_text())), indent=2))
        return
    result = {}
    try:
        if args.archives:
            result["archives"] = [archive_check(args.archives / a["name"], a)
                                  for a in manifest["assets"]]
        if args.source:
            result["source"] = source_check(args.source, manifest["hdfix_source"])
        if args.exports:
            result["exports"] = export_check(args.exports, manifest, json.loads(SCHEMA.read_text()))
    except (ValueError, OSError, KeyError, TypeError, configparser.Error,
            subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        parser.exit(1, f"candidate validation failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
