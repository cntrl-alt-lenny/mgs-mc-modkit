"""Brain correction rechecks in disposable fixtures; no games or native binaries run."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock
import zipfile


def audio_identity(seat):
    sys.path.insert(0, str(seat))
    sys.path.insert(0, str(seat / "tests"))
    import install
    from conftest import MOD_LAYOUTS, FakeUI, build_audio_zip, build_mgs2_base_zip, build_zip, make_steam_root
    with tempfile.TemporaryDirectory(prefix="mgs-brain-audio-") as td:
        base = Path(td)
        game = base / "mgs2"
        game.mkdir()
        (game / install.GAMES["mgs2"]["exe"]).write_bytes(b"fixture")
        steam = make_steam_root(base)
        install.app_data_dir = lambda: base / "state"
        hdfix = build_zip(base / "hdfix.zip", MOD_LAYOUTS["MGSHDFix"])
        bugfix = build_zip(base / "bugfix.zip", MOD_LAYOUTS["MGS2-Community-Bugfix"])
        install.HDFIX_SHA256 = install.sha256_file(hdfix)
        install.GAMES["mgs2"]["bugfix_sha256"] = install.sha256_file(bugfix)
        def download(url, dest, log, sha256=None):
            shutil.copyfile(hdfix if "MGSHDFix" in url else bugfix, dest)
        install.download = download
        audio = build_mgs2_base_zip(base / "user-audio.zip")
        ui = FakeUI(yesno=[])
        accepted = {}
        old_hash = install.sha256_file(audio)
        assert install.validate_audio_for_role(audio, "mgs2", "base")[0] == "ok"
        assert install._accept_audio_file(ui, audio, "mgs2", "base", {},
                                         install.AUDIO_SPECS["mgs2"]["roles"]["base"], accepted) == audio
        # Replacement occurs after selection, before construction of the review plan.
        build_audio_zip(audio)
        print("Replacement classification:", install.validate_audio_for_role(audio, "mgs2", "base")[0])
        opts = dict(button_icons="Xbox One", audio_mode="Stereo (2.0)", hq_movies=True,
                    skip_launcher=True, skip_splash=True, update_check=False, device="desktop", _changed=set())
        components = install.order_audio_components("mgs2", {"base": audio})
        components[0]["acceptance"] = accepted[str(audio)]
        assert old_hash != install.sha256_file(audio)
        before = {p.relative_to(game).as_posix(): p.read_bytes() for p in game.rglob("*") if p.is_file()}
        try:
            install.build_install_plan({"mgs2": (game, steam)}, {"mgs2": opts}, {"mgs2": components})
        except install.ReplanRequired as error:
            print("Replacement refused:", error)
        else:
            raise AssertionError("Replacement incorrectly accepted")
        after = {p.relative_to(game).as_posix(): p.read_bytes() for p in game.rglob("*") if p.is_file()}
        assert before == after and not (game / install.MODKIT_DIRNAME).exists()
        assert accepted[str(audio)].sha256 == old_hash
        print("PASS: original acceptance retained; all game bytes unchanged")



def removal(seat, archive):
    sys.path.insert(0, str(seat))
    import install
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == install.PATRIOT_SHA256
    with tempfile.TemporaryDirectory(prefix="mgs-brain-removal-") as td:
        base = Path(td)
        game = base / "game"
        downloads = base / "downloads"
        downloads.mkdir()
        shutil.copyfile(archive, downloads / f"MGS4_MGSPatriotFix_{install.PATRIOT_VERSION}.zip")
        install.app_data_dir = lambda: base / "state"
        for name in ("MGS4/mgs4.exe", "Launcher/launcher.exe", "mgs4_savedata_win/1/save.dat", "MGSM2Fix.asi"):
            path = game / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"untracked original " + name.encode())
        original = (game / "MGSM2Fix.asi").read_bytes()
        save = (game / "mgs4_savedata_win/1/save.dat").read_bytes()
        with install.GameLock(game):
            tx = install.InstallTxn(game, "mgs4", lambda _: None)
            install.install_patriot(tx, downloads, {}, lambda _: None)
            tx.commit()
        record = json.loads((game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
        assert "MGSM2Fix.asi" not in record["added"]
        assert all(x["path"] != "MGSM2Fix.asi" for x in record["overwritten"])
        assert (game / "MGSM2Fix.asi").read_bytes() == original
        notes, ok = install.uninstall_game(game, lambda _: None)
        print("Removal returns success:", ok)
        print("Unowned MGSM2Fix.asi preserved:", (game / "MGSM2Fix.asi").exists())
        print("Save bytes preserved:", (game / "mgs4_savedata_win/1/save.dat").read_bytes() == save)
        print("Removal notes:", notes)
        assert ok and (game / "MGSM2Fix.asi").read_bytes() == original
        assert (game / "mgs4_savedata_win/1/save.dat").read_bytes() == save
        print("PASS: actual-archive removal preserves unowned ASI and save bytes")


def source_drift(seat, source):
    sys.path.insert(0, str(seat))
    from tools.capture_patriot_schema import capture
    with tempfile.TemporaryDirectory(prefix="mgs-brain-source-") as td:
        copy = Path(td) / "source"
        subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--shared", str(source), str(copy)], check=True)
        before = capture(copy)
        fixture = json.loads((seat / "tests/fixtures/patriotfix-0.2.2-schema.json").read_text())
        assert before == fixture
        print("Exact source tree:", before["tree"])
        for name in ("src/resources/stdafx.h", "ConfigTool/pch.h", "src/resources/version.h"):
            header = copy / name
            original = header.read_bytes()
            for action in ("modified", "omitted"):
                if action == "modified":
                    header.write_bytes(original + b"\n#error Unreviewed compiled header\n")
                else:
                    header.unlink()
                try:
                    capture(copy)
                except ValueError as error:
                    print(name, action, "refused:", error)
                else:
                    raise AssertionError("Header drift accepted")
                header.write_bytes(original)
        addition = copy / "src/new-unreviewed.h"
        addition.write_bytes(b"#error addition")
        try:
            capture(copy)
        except ValueError as error:
            print("Added header refused:", error)
        else:
            raise AssertionError("Added header accepted")
        print("PASS: exact fresh source reproduces fixture; all three header edits/omissions/additions refused")



def windows_archive(seat):
    sys.path.insert(0, str(seat / "tools"))
    import validate_volume1_candidate as candidate
    with tempfile.TemporaryDirectory(prefix="mgs-brain-zip-") as td:
        path = Path(td) / "raw-backslash.zip"
        info = zipfile.ZipInfo("a/b")
        info.filename = "a\\b"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(info, b"fixture")
        asset = {"sha256": candidate.digest(path.read_bytes()), "size": path.stat().st_size, "members": ["a/b"]}
        with mock.patch("zipfile.os.sep", "\\"):
            with zipfile.ZipFile(path) as archive:
                member = archive.infolist()[0]
                print("Original member:", repr(member.orig_filename))
                print("Normalized member:", repr(member.filename))
            try:
                candidate.archive_check(path, asset)
            except ValueError as error:
                assert "unsafe" in str(error)
                print("Raw backslash refused:", error)
            else:
                raise AssertionError("Windows normalization bypass accepted")
        print("PASS: raw serialized path rejected despite matching normalized layout")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", choices=("audio", "removal", "source", "windows"))
    parser.add_argument("--seat", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    print("Reviewed SHA:", subprocess.check_output(["git", "-C", str(args.seat), "rev-parse", "HEAD"], text=True).strip())
    if args.probe == "audio":
        audio_identity(args.seat)
    elif args.probe == "removal":
        removal(args.seat, args.archive)
    elif args.probe == "source":
        source_drift(args.seat, args.source)
    else:
        windows_archive(args.seat)
    print("All fixtures disposable; native games/exports/binaries NOT RUN")


if __name__ == "__main__":
    main()
