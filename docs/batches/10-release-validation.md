# 10-release-validation

## Done

Resumed on Windows under the Checked path. Safely merged main's framework
provenance correction; candidate production files, pins, schema and version
remain unchanged. Installed three licensed games in Steam's default library
after preserving saves/settings. Recorded hardware, Steam builds/executable
hashes and protected-copy inventories in
[Windows run](evidence/10-release-validation/windows-run.md).

Executed exact candidate local `install.py`, verified pinned archives and all
three committed manifests, and observed final completion text. Captured real
modded trials and second-installer refusal in
[runtime observations](evidence/10-release-validation/windows-modded-observations.md).
**Interim checkpoint: repair/removal/post-removal trials remain in progress;
this is not final Verifier delivery.**

## Checked

Windows Python3.12.10:271 tests passed/two privileged symlink tests skipped;
Ruff, compilation, framework hygiene and shortcut pin/line-ending checks
passed. [Exact checks](evidence/10-release-validation/windows-checks.txt).
Prior macOS/CI evidence remains separately retained. Installer SHA256 remains
`a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`.

Before modded boots, common saves/target Steam userdata were byte equal
through installation. MGS2's9875 and MGS3's3790 original backup hashes match
stock. Actual modules/logs prove MGSM2Fix3.6.0, MGSHDFix4.1.0 and Bugfix3.0.0/
2.0.1 injection; this does not prove successful initialization. Second real
candidate refused at GameLock before InstallTxn while the first MGS2 repair
continued. No synthetic lock holder was substituted.

## Not checked

Repair preservation, removal and post-removal stock comparisons remain in
progress. Full playable Windows observations remain unproven. Deck/Proton,
cancellation, optional audio and large-audio Steam restoration remain NOT RUN;
no compatible owner-supplied audio is available. Latest published shortcuts
still target2.2.0; static2.3.0 matching does not establish unpublished asset
runtime behavior. No tag/publication ran.

## Failed or blocked

**Release readiness remains BLOCKED.** Actual MGS2/MGS3 launcher/game logs
report missing `MSX Skip Launcher Game` in `Launcher and Splashscreens`;
games remain at error consoles. No migration/fix was made. MGS1 rendered
border artwork/black center during47seconds then exited abnormally;
title/playable and native first-time settings are unproven. Stock MGS3 also
exited abnormally before kit installation. Exact times and UI access failures
are retained; close/fault causality is unproven. Unenumerated native final
dialogs leave process exit outcomes pending. Earlier Mac access failure was
an access limitation, not a Windows test failure. Missing required evidence
and observed runtime errors preclude release approval. PR15 stays draft.
