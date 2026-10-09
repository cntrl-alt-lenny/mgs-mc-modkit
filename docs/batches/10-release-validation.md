# 10-release-validation

## Done

Resumed Windows validation under the Checked path. Safely merged main's
framework provenance correction; installer, pins, schema and version remain
equal to candidate `15d9277`. Installed three licensed games in Steam's default
library after preserving saves/settings. Hardware, Steam builds/executable
hashes, commands, outputs and protected-copy inventories are in
[Windows run](evidence/10-release-validation/windows-run.md).

Executed exact local `install.py`: verified all four pinned archives and all
three manifests. Ran all three modded trials, settings changes, actual repair,
two-process concurrent refusal, removal and post-removal stock trials.
[Runtime evidence](evidence/10-release-validation/windows-modded-observations.md)
and [stock observations](evidence/10-release-validation/windows-poststock-observations.md)
distinguish content outcomes from UI/gameplay limits.

## Checked

Windows Python 3.12.10: 271 tests passed/two privileged symlink tests skipped;
Ruff, compilation, framework hygiene and both shortcut pin/line-ending checks
passed. [Exact checks](evidence/10-release-validation/windows-checks.txt).
Installer SHA256 remains
`a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`.

Install and immediate repair preserved common saves/target userdata. All
9875 MGS2/3790 MGS3 original backups matched stock; after removal each matched
its restored live path. All common/remote save bytes survived removal;
MGS1's remotecache alone changed, cause unproven. Full stock comparison found
zero missing files or changed original assets/executables. Earlier launcher
preferences/game-generated cache/log changes are identified separately.

Repair preserved MGS1's 1024x768 resolution, MGS2 French/1280x720 and MGS3
Spanish/1600x900 independently. MGS1's native launcher rendered 1024x768.
Second real candidate refused at GameLock before download/InstallTxn while
the first legitimately repaired; no synthetic lock holder substituted.

Unchanged main's terminal-backend selection harness removed all three mods
and restored originals, actual exit 0. Native confirmation was unreachable.
Final machine has no candidate loaders/configs/recovery folders, unchanged
game builds/executable hashes, no active games/downloads and intact private
14/16-file protected copies. Permitted generated leftovers are documented.

## Not checked

Full playable/save-loading observations, MGS1 native language/first-time
settings and normal native installer acknowledgements remain unproven.
Deck/Proton, cancellation, optional/large-audio restoration remain NOT RUN;
no suitable user-supplied audio payload was identified in this run.
Published shortcuts still target 2.2.0; static 2.3.0 pins do not prove
unpublished release-asset runtime behavior. No tag/publication ran.

## Failed or blocked

**Release readiness remains BLOCKED.** MGS2/MGS3 actual launcher/game logs
report missing `MSX Skip Launcher Game` in `Launcher and Splashscreens`,
leaving error consoles. No migration/fix was made. MGS1 showed border art/
black center with abnormal exits, including a separate four-minute follow-up.
Stock MGS1 remained launcher-only; stock MGS2/MGS3 titles rendered, playable
unproven. Stock MGS3 faulted before and after kit removal. Close/fault
causality is unproven. Untargetable native installer final dialogs required
controlled own-process cleanup, actual exit 1, separate from verified content.
Earlier Mac access failure was an access limitation. PR15 stays draft.
