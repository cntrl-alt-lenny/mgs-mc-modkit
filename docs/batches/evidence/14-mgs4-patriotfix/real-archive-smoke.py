"""Actual upstream archive extraction in a disposable, unlicensed game fixture.

This tests archive handling/transactions only; it never runs Windows binaries.
"""
from pathlib import Path
import shutil
import sys
import tempfile

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root))
import install  # noqa: E402

archive = Path(sys.argv[1])
assert install.sha256_file(archive) == install.PATRIOT_SHA256
with tempfile.TemporaryDirectory(prefix='mgs14-real-archive-') as folder:
    base = Path(folder)
    game = base / 'METAL GEAR SOLID 4'
    for rel in ('MGS4/mgs4.exe', 'Launcher/launcher.exe', 'mgs4_savedata_win/123/save.dat'):
        path = game / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'fixture, not a licensed executable/save')
    tmp = base / 'downloads'
    tmp.mkdir()
    shutil.copyfile(archive, tmp / 'MGS4_MGSPatriotFix_0.2.2.zip')
    install.app_data_dir = lambda: base / 'app-state'
    choices = install.options_for_game('mgs4', (game, base), {}, print)
    with install.GameLock(game):
        tx = install.InstallTxn(game, 'mgs4', print)
        install.install_patriot(tx, tmp, choices, print)
        assert not install.verify_install(install.GAMES['mgs4'], game)
        install.validate_patriot_settings((game / 'MGSPatriotFix.settings').read_text())
        tx.commit()
    assert (game / 'MGS4/winmm.dll').read_bytes()[:2] == b'MZ'
    assert (game / 'Launcher/d3d11.dll').read_bytes()[:2] == b'MZ'
    assert not (game / 'logs/MGSPatriotFix_Game.log').exists()
    notes, ok = install.uninstall_game(game, print)
    assert ok, notes
    assert not (game / 'MGSPatriotFix.settings').exists()
    for rel in ('MGS4/mgs4.exe', 'Launcher/launcher.exe', 'mgs4_savedata_win/123/save.dat'):
        assert (game / rel).read_bytes() == b'fixture, not a licensed executable/save'
print('Actual pinned archive extraction/verification/removal passed; native exports/boots NOT RUN')
