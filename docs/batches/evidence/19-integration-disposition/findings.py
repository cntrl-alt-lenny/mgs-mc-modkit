"""Independent counterexamples for the two Batch 12 Verifier findings."""

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import json

seat = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(seat), str(seat / "tests")]
import install  # noqa: E402 - select the exact isolated delivery first
from pytest import MonkeyPatch  # noqa: E402 - select the exact isolated delivery first
from conftest import mod_zips, patch_download, build_zip  # noqa: E402 - select the exact isolated delivery first
from test_install_plan import world, snapshot  # noqa: E402 - select the exact isolated delivery first

print(
    "Reviewed SHA:",
    subprocess.check_output(
        ["git", "-C", str(seat), "rev-parse", "HEAD"], text=True
    ).strip(),
)
corrected = sys.argv[2] == "corrected"
for case in ("staging", "rollback", "backups", "cache", "during-use"):
    if case == "during-use" and not corrected:
        continue
    with TemporaryDirectory() as td, MonkeyPatch.context() as mp:
        root = Path(td)
        patch_download.__wrapped__(mp, mod_zips.__wrapped__(root))
        found, opts = world(root)
        last = found["mgs3"][0]
        if case not in ("cache", "during-use"):
            records = last / install.MODKIT_DIRNAME
            records.mkdir()
            (records / case).write_bytes(b"obstruction")
            (last / "winhttp.dll").write_bytes(b"original")
        before = snapshot(found)
        plan = install.build_install_plan(found, opts, {})
        workspace = root / "workspace"
        workspace.mkdir()
        adapter = install.CurrentRecipeAdapter(lambda _: None)
        outcomes = dict.fromkeys(found, "not started")
        try:
            prepared = install.prepare_plan(plan, adapter, workspace)
        except install.CorruptManifestError as error:
            assert corrected and case in ("staging", "rollback", "backups")
            assert snapshot(found) == before
            assert not any(
                (game / install.MODKIT_DIRNAME / install.MANIFEST_NAME).exists()
                for game, _ in found.values()
            )
            print(case, "REFUSED BEFORE ANY GAME WRITE:", error)
            continue
        assert case in ("cache", "during-use") or not corrected
        if case == "cache":
            real = adapter.execute

            def execute(game, index, outcomes):
                real(game, index, outcomes)
                if index == 0:
                    cached = Path(prepared.games[2].identities[-1][0])
                    build_zip(
                        cached,
                        {
                            "plugins/MGS3-Community-Bugfix-Compilation.asi": b"UNCONFIRMED"
                        },
                    )

            adapter.execute = execute
        if case == "during-use":
            real_archive = install.InstallTxn.install_archive
            originals = {
                source: Path(source).read_bytes()
                for game in prepared.games
                for source, _ in game.identities
            }

            def use(tx, archive, **kwargs):
                assert str(archive) not in originals
                game = next(g for g in prepared.games if g.game.key == tx.game_key)
                for source, _ in game.identities:
                    Path(source).write_bytes(b"UNCONFIRMED DURING USE")
                assert archive.read_bytes() in originals.values()
                return real_archive(tx, archive, **kwargs)

            mp.setattr(install.InstallTxn, "install_archive", use)
        try:
            install.execute_plan(prepared, adapter, outcomes)
        except install.ReplanRequired as error:
            assert corrected and case == "cache"
            assert snapshot(found)["mgs3"] == before["mgs3"]
            assert outcomes["mgs3"] == "not changed; inspect recovery record / lock"
            print(
                "cache REFUSED BEFORE TARGET TRANSACTION:", error, json.dumps(outcomes)
            )
            continue
        except OSError as error:
            assert not corrected and case in ("staging", "rollback", "backups")
            assert snapshot(found)["mgs3"] == before["mgs3"]
            print(case, "ORIGINAL FAILURE:", type(error).__name__, json.dumps(outcomes))
            continue
        if case == "cache":
            assert not corrected
            assert (
                last / "plugins/MGS3-Community-Bugfix-Compilation.asi"
            ).read_bytes() == b"UNCONFIRMED"
            print(
                "cache ORIGINAL FAILURE: unconfirmed ASI installed",
                json.dumps(outcomes),
            )
        else:
            assert case == "during-use" and set(outcomes.values()) == {
                "installed and verified"
            }
            print(
                "during-use PASS: original cached bytes replaced; private replay remains authenticated"
            )
print("All fixtures disposable; native games NOT RUN")
