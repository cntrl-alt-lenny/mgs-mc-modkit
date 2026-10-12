"""Synthetic validator failures; these fixtures are never native exports."""
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("candidate", ROOT / "tools/validate_volume1_candidate.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

SCHEMA = {"fields": {"Hidden MG": {"Crop": "Bool"}, "Options": {
    "Choice": "Choice", "Dynamic": "Choice", "Hotkey": "Hotkey", "Scale": "Float",
    "Size": "Int", "Name": "Str"}}, "constraints": {"Options": {
        "Choice": {"choices": ["a", "b"]}, "Size": {"range": [0, 10]}}}}
EXPORT = ('[Hidden MG]\r\nCrop=1\r\n[Options]\r\nChoice="a"\r\nDynamic="en"\r\n'
          'Hotkey="F8"\r\nScale=1.0\r\nSize=2\r\nName="Test"\r\n').encode()


@pytest.mark.parametrize("before,after", [
    (b"Crop=1", b"Crop=2"), (b"Crop=1", b"Crap=1"), (b"Crop=1\r\n", b""),
    (b"Size=2", b"Size=11"), (b'Choice="a"', b'Choice="c"'),
    (b"Scale=1.0", b"Scale=nan"), (b"Size=2", b"Size=2.0"),
    (b"Crop=1", b"Crop=1\r\nCrop=1"), (b"\r\n", b"\n"),
    (b"[Hidden MG]", b"[DEFAULT]\r\nExtra=1\r\n[Hidden MG]"),
])
def test_export_rejects_malformed_or_incomplete(before, after):
    with pytest.raises((ValueError, candidate.configparser.Error)):
        candidate.parse_export(EXPORT.replace(before, after), SCHEMA)


def bundle(tmp_path):
    (tmp_path / "default.settings").write_bytes(EXPORT)
    (tmp_path / "kit.settings").write_bytes(EXPORT)
    record = {p: {"file": p + ".settings", "sha256": candidate.digest(EXPORT)}
              for p in ("default", "kit")}
    record["dynamic_fields"] = {"Options": {
        k: {"default": value, "kit": value, "evidence": "synthetic test only",
            "choices": ["en"], "range": [0, 10]}
        for k, value in (("Dynamic", "en"), ("Hotkey", "F8"), ("Scale", 1.0))}}
    metadata = {"tag": "4.1.2", "archive_sha256": "archive", "config_tool_sha256": "exe",
                "platform": "Windows", "captured_utc": "synthetic", "platform_version": "synthetic",
                "operator": "synthetic", "procedure": "synthetic", "observations": "synthetic",
                "games": {"mgs2": record, "mgs3": record}}
    manifest = {"assets": [{"id": "hdfix", "sha256": "archive", "payload_sha256": {
        "plugins/MGSHDFix Config Tool.exe": "exe"}}]}
    (tmp_path / "capture.json").write_text(json.dumps(metadata))
    return metadata, manifest


def test_structural_pass_never_authorizes_adoption(tmp_path):
    _, manifest = bundle(tmp_path)
    result = candidate.export_check(tmp_path, manifest, SCHEMA)
    assert result["structural_validation"] == "pass"
    assert "still requires" in result["adoption"]


@pytest.mark.parametrize("mutation", [
    lambda m: m.update(platform="macOS"),
    lambda m: m.update(config_tool_sha256="wrong"),
    lambda m: m["games"].pop("mgs3"),
    lambda m: m["games"]["mgs2"].update(dynamic_fields={}),
    lambda m: m["games"]["mgs2"]["default"].update(sha256="wrong"),
    lambda m: m["games"]["mgs2"]["default"].update(file="../outside.settings"),
    lambda m: m["games"]["mgs2"]["dynamic_fields"]["Options"]["Dynamic"].update(choices=[]),
    lambda m: m["games"]["mgs2"]["dynamic_fields"]["Options"]["Scale"].update(kit=2.0),
    lambda m: m["games"]["mgs2"]["dynamic_fields"]["Options"]["Scale"].update(range=[]),
])
def test_bundle_rejects_missing_provenance_and_dynamic_evidence(tmp_path, mutation):
    metadata, manifest = bundle(tmp_path)
    mutation(metadata)
    (tmp_path / "capture.json").write_text(json.dumps(metadata))
    with pytest.raises(ValueError):
        candidate.export_check(tmp_path, manifest, SCHEMA)


def raw_name_archive(path, name):
    # Assign after construction: Windows ZipInfo.__init__ rewrites backslashes,
    # and all platforms truncate at NUL. Both ZIP headers must retain raw bytes.
    member = zipfile.ZipInfo("placeholder")
    member.filename = member.orig_filename = name
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, b"test")
    assert path.read_bytes().count(name.encode("utf-8")) == 2
    with zipfile.ZipFile(path) as archive:
        assert archive.infolist()[0].orig_filename == name
    return {"sha256": candidate.digest(path.read_bytes()), "size": path.stat().st_size,
            "members": [name]}


@pytest.mark.parametrize("name", ["../outside", "/absolute", "C:/drive", "a\\b", "a/./b",
                                 "safe\x00/../outside", "safe\x00", "a\nb", "a\x7fb"])
def test_archive_rejects_unsafe_paths_without_extraction(tmp_path, name):
    path = tmp_path / "archive.zip"
    asset = raw_name_archive(path, name)
    with pytest.raises(ValueError, match="unsafe"):
        candidate.archive_check(path, asset)
    assert not (tmp_path.parent / "outside").exists()


@pytest.mark.parametrize("name,normalized", [("a\\b", "a/b"),
                                              ("safe\x00/../outside", "safe"),
                                              ("original", "changed")])
def test_archive_rejects_reader_normalization_even_with_matching_layout(
        tmp_path, monkeypatch, name, normalized):
    path = tmp_path / "archive.zip"
    asset = raw_name_archive(path, name)
    asset["members"] = [normalized]
    original_init = zipfile.ZipInfo.__init__

    def normalize(member, *args, **kwargs):
        original_init(member, *args, **kwargs)
        if member.orig_filename == name:
            member.filename = normalized

    monkeypatch.setattr(zipfile.ZipInfo, "__init__", normalize)
    with zipfile.ZipFile(path) as archive:
        member = archive.infolist()[0]
        assert member.orig_filename == name
        assert member.filename == normalized
    with pytest.raises(ValueError, match="unsafe"):
        candidate.archive_check(path, asset)



def test_archive_verifies_digest_layout_and_payload(tmp_path):
    path = tmp_path / "archive.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("plugins/tool.exe", b"test")
    asset = {"sha256": candidate.digest(path.read_bytes()), "size": path.stat().st_size,
             "members": ["plugins/tool.exe"], "payload_sha256": {
                 "plugins/tool.exe": candidate.digest(b"test")}}
    assert candidate.archive_check(path, asset)["crc"] == "pass"
    asset["payload_sha256"]["plugins/tool.exe"] = "wrong"
    with pytest.raises(ValueError, match="payload"):
        candidate.archive_check(path, asset)
    asset["sha256"] = "wrong"
    with pytest.raises(ValueError, match="digest"):
        candidate.archive_check(path, asset)


def test_candidate_is_separate_from_shipping_schema():
    schema = json.loads(candidate.SCHEMA.read_text())
    manifest = json.loads(candidate.MANIFEST.read_text())
    assert schema["tree"] == manifest["hdfix_source"]["commit"]
    assert {s: sorted(keys) for s, keys in schema["fields"].items()} == manifest["hdfix_source"]["runtime_reads"]
    import install
    assert install.HDFIX_VERSION == "4.1.0"
    assert install.M2FIX_TAG == "v3.6"
    assert schema["fields"] != install.SETTINGS_SCHEMA


def test_template_is_incomplete_and_cannot_validate_as_native(tmp_path):
    manifest = json.loads(candidate.MANIFEST.read_text())
    schema = json.loads(candidate.SCHEMA.read_text())
    form = candidate.capture_template(manifest, schema)
    assert set(form["games"]) == {"mgs2", "mgs3"}
    assert {(s, k) for s, keys in form["games"]["mgs2"]["dynamic_fields"].items()
            for k in keys} == candidate.dynamic_fields(schema)
    (tmp_path / "capture.json").write_text(json.dumps(form))
    with pytest.raises(ValueError, match="native platform"):
        candidate.export_check(tmp_path, manifest, schema)


def test_source_rejects_wrong_head_and_modified_bytes(tmp_path, monkeypatch):
    identity = {"tag": "candidate", "commit": "a" * 40, "source_sha256": {"field.cpp": "wrong"}}
    monkeypatch.setattr(candidate, "git", lambda *args: b"b" * 40)
    with pytest.raises(ValueError, match="commit/tag"):
        candidate.source_check(tmp_path, identity)
    monkeypatch.setattr(candidate, "git", lambda *args: b"a" * 40)
    (tmp_path / "field.cpp").write_text("changed")
    with pytest.raises(ValueError, match="source bytes"):
        candidate.source_check(tmp_path, identity)


def test_archive_rejects_case_collisions(tmp_path):
    path = tmp_path / "archive.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("file.dll", b"one")
        archive.writestr("FILE.dll", b"two")
    asset = {"sha256": candidate.digest(path.read_bytes()), "size": path.stat().st_size,
             "members": ["file.dll", "FILE.dll"]}
    with pytest.raises(ValueError, match="duplicate"):
        candidate.archive_check(path, asset)


def test_per_game_values_are_compared(tmp_path):
    metadata, manifest = bundle(tmp_path)
    changed = EXPORT.replace(b'Name="Test"', b'Name="Other"')
    (tmp_path / "other.settings").write_bytes(changed)
    metadata["games"]["mgs3"] = json.loads(json.dumps(metadata["games"]["mgs3"]))
    metadata["games"]["mgs3"]["default"] = {"file": "other.settings", "sha256": candidate.digest(changed)}
    (tmp_path / "capture.json").write_text(json.dumps(metadata))
    result = candidate.export_check(tmp_path, manifest, SCHEMA)
    assert result["per_game_differences"]["default"]["Options"]["Name"] == {
        "mgs2": "Test", "mgs3": "Other"}


def test_archive_rejects_symlink(tmp_path):
    path = tmp_path / "archive.zip"
    member = zipfile.ZipInfo("link")
    member.create_system = 3
    member.external_attr = 0o120777 << 16
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, b"target")
    asset = {"sha256": candidate.digest(path.read_bytes()), "size": path.stat().st_size,
             "members": ["link"]}
    with pytest.raises(ValueError, match="unsafe"):
        candidate.archive_check(path, asset)


@pytest.mark.parametrize("failure", ["size", "members", "required_members", "crc"])
def test_archive_preserves_integrity_refusals(tmp_path, failure):
    path = tmp_path / "archive.zip"
    asset = raw_name_archive(path, "safe")
    expected = {"size": "digest/size", "members": "layout", "required_members": "required",
                "crc": "CRC"}[failure]
    if failure == "crc":
        path.write_bytes(path.read_bytes().replace(b"test", b"fail"))
        asset["sha256"] = candidate.digest(path.read_bytes())
    else:
        asset[failure] = 0 if failure == "size" else ["missing"]
    with pytest.raises(ValueError, match=expected):
        candidate.archive_check(path, asset)
