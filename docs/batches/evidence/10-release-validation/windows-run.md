# Windows validation run

Worker, 2026-10-07. Candidate production is
`15d9277196e7bd1cfbd45fe280a230050b276bed`; local installer SHA-256 is
`a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`.
The existing Worker branch was clean at `bd19eb3`, fetched origin, and normally
merged main `90967b9` into `d83f858dc8372281ef526ee00035c484e5cf11b1`.
Installer, shortcuts, schema and pins are unchanged from the candidate.
The current Windows request supersedes the old brief's Mac access assumption.

## Host and preserved baseline

| Field | Observed value |
| --- | --- |
| OS | Windows 11 Pro, 10.0.26300, build 26300, 64-bit |
| System board/model | Gigabyte X570 AORUS ELITE |
| CPU | AMD Ryzen 7 5800X 8-Core Processor |
| GPU | NVIDIA GeForce RTX 2060, driver 32.0.16.1714; Virtual Display Driver also enumerated |
| Python | 3.12.10 via `py -3` |
| Steam library | Default Windows C: library, one library in `libraryfolders.vdf` |
| Initial free space | 245353246720 bytes (PowerShell); Steam install dialogs >217 GB free |
| Licensed games | Library UI contains all three Master Collection titles and presents INSTALL |
| Initial installation | All three app manifests absent; MGS1 common folder absent; MGS2/MGS3 common folders contain only save directories |
| Existing mods/originals/recovery | None in scoped MGS1/2/3 common folders; no LOCALAPPDATA kit folder observed |
| Existing saves | MGS2/MGS3 remnants: 12 files, 100851 bytes total. MGS1 target Steam userdata: two files, including remote save |
| Preservation | Copied all scoped common-folder remnants and target app userdata into a protected, untracked local directory before Steam install. All 14 source/copy SHA-256 pairs matched |
| Audio | No supplied payload identified; no audio content is redistributed |

Personal paths and Steam account identifiers stay in the untracked protected
inventory. This public record uses portable game/app identities only.
Relevant commands: `Get-CimInstance Win32_OperatingSystem`,
`Win32_ComputerSystem`, `Win32_VideoController`; `Get-PSDrive C`;
read `steamapps/libraryfolders.vdf`; `Test-Path` for app manifests/common
folders; `Get-ChildItem` and `rg --files` scoped to target common folders and
Steam userdata; `Copy-Item -LiteralPath ... -Recurse -Force`;
`Get-FileHash -Algorithm SHA256` on every source and protected copy.
Discovery/copy/verification shell commands completed with exit 0.
Exact scoped commands/redacted output are retained in
`windows-baseline-commands.txt`; `windows-protected-inventory.json` retains
14 individual source/protected-copy SHA-256 comparisons (17796551 bytes).
`inventory-preservation.py` is the read-only portable comparison used to
generate that JSON, independently repeated while downloads were in progress.

## Steam UI actions

Used the computer-use skill, `@oai/sky` via node REPL, with fresh returned
Steam window/state observations. Steam was signed in; no authentication was
automated. User's explicit installation authorization persists.

| Local time (BST, 2026-10-07) | Action/observation |
| --- | --- |
| Before 14:51 | Library search `METAL GEAR` shows all three licensed Master Collection titles. MGS1 INSTALL, 10.55 GB required |
| Around 14:51 | MGS1 Install dialog defaults to C:; clicked Install. Progress observed 1%, then 14% |
| Around 14:52 | MGS2 INSTALL, 18.24 GB required; default C:; clicked Install |
| Around 14:52 | MGS3 INSTALL, 17.54 GB required; default C:; clicked Install |
| 14:53 | Steam queue: MGS3 downloading 4% at ~179 Mbps, 351.6 MB/13.3 GB; MGS2 queued 3%,197.9 MB/13.9 GB; MGS1 queued14%,1.8 GB/7.9 GB |
| 14:58 | MGS3 completed13.3GB/13.3GB, Steam PLAY available; manifestStateFlags4,build22192289 |
| 15:03 | MGS2 completed13.9GB/13.9GB, Steam PLAY available; manifestStateFlags4,build21578573 |
| 15:04–15:05 | MGS1 downloading43–52%; no queue remaining; completion pending |
| 15:12 | Steam Completed list: MGS1 7.9/7.9GB completed15:06, MGS2 and MGS3 also completed; allthree PLAY; UpNext0,network/disk0bps |

UI actions do not expose process exit codes. Installation completion must be
observed separately; queue/download progress is not completion or game boot.

## Pre-kit stock boots

MGS3: clicked Steam PLAY, observed controller recommendation dialog and clicked
OK. Launcher Ver3.0.0 rendered; Return navigated Game Selection, North American
Version, English, Start Game. Steam log15:00:03 recorded actual game command:
`METAL GEAR SOLID3.exe -region us -lan en -selfregion EU -launcherpath launcher.exe -ctrltype XBOX`.
Stock executable SHA256:
`81596a6a670263da6ee59c959b65cbf833be985e64fa0332ad926271aa060bfe`.
Game initially white and `Get-Process`Responding=False,CPU4.28125 at about
15:00:30. No target Application Error/Hang event found15:00:59. By15:02:05,
HD Edition title rendered60FPS,Responding=True,CPU163.25. This delay resolved.

Return,Escape,Tab,H,2 and clicking the game surface did not establish a menu
or playable scene. The [official PC manual](https://metalgear.konami.net/manual/mc1/mgs3/pc/en/page04.html)
lists relevant keyboard mappings; no new input runtime or fabricated hold API
was used. Alt+F4 was attempted; no force termination. Later input encountered
`foreground window did not report a process id`; fresh window enumeration
showed the game absent. Steam recorded game exit-1073741819(0xC0000005)15:04:39,
launcher exit0. EventId1000 reported0xC0000005 in stock executable3.0.0.0,
offset0x115f64,TimeCreated15:04:13. Input/close causality is not established.
See`windows-stock-process.txt` for exact target records and redacted commands.
Result: title rendering observed; full stock smoke/playable success unproven;
abnormal exit observed before kit installation.

MGS2: stock executable SHA256
`9c8575e6b2d6449636d1a04b63ef8c9e44c3aecf84cadddc27b4874c62688f2b`.
Steam PLAY and controller-dialogOK issued; stock launcher/warnings rendered.
Launcher Ver2.1.0: Game Selection → English → Start Game. Unlike MGS3, no
region-selection screen was offered. Actual executable started15:07:55;
opening logos and cinematic rendered60FPS. Get-Process15:08:23:
PID62704,Responding=True,CPU43.6875. Return,Tab,2 and Escape did not establish
skip/input success; cinematic observation continues naturally. The
[official manual](https://metalgear.konami.net/manual/mc1/mgs2/pc/en/page04.html)
documents those keyboard layouts. HD Edition title rendered60FPS15:11:30.
Tab,2,Return at title did not establish menu or playable control. Alt+F4
requested close; Steam15:11:51 records both game and launcher exit0; fresh
window/process discovery confirms absent. Result: stock title observed,
normal exit; playable input unproven.

MGS1 manifest15:08:23: StateFlags4,build20872173,BytesDownloaded and
BytesToDownload both8432542112. Stock executable SHA256:
`e320062847ec71a52292e9931bcf2ee33ea6586429ecb2a38e567ab37b66c373`.
Steam completion confirmed above. PLAY → controller-recommendationOK;
stock integrated launcher Ver3.0.0 rendered61FPS. Return before/after surface
focus click, then documented H confirmation, did not pass PRESS ANY BUTTON.
[Official mapping](https://metalgear.konami.net/manual/mc1/mgs1/pc/en/page03.html)
was read. Launcher closed using its windowX; Steam exit0 at15:13:44.
Result: launcher rendering observed; actual emulated game and playable scene
unproven. C: free192760107008bytes15:09:40.

Brain authorized conditional candidate trials after these bounded baselines:
MGS3/MGS2 actual title observed, MGS1 integrated launcher only. None meets the
full playable requirement yet. The stock MGS3 crash precedes kit installation.

Before kit mutation, all target game/launcher processes absent. Copied current
common `*_savedata_win` and target app userdata into a separate private pre-kit
phase backup:16files17799742bytes, all source/protected SHA256 pairs equal.
See `windows-phase-commands.txt`, `windows-prekit-protected-inventory.json`.
This phase follows stock boots, so legitimate game-authored settings/cache
changes are distinct from installer preservation comparisons.

## Failed discovery/logging attempts retained

Completed Windows runtime evidence is in `windows-modded-observations.md`
and `windows-poststock-observations.md`: actual fresh install/repair content,
save/original preservation, modded failures, real concurrent refusal,
production removal and post-removal stock trials. Normal native installer
acknowledgements and full gameplay remain unproven. Final machine is restored
with loaders/configs/kit recovery folders absent, all games closed, Steam
downloads idle and protected copies retained. Historical discovery failures
below remain separate from candidate failures. PR15 remains draft.

- Brain's first status attempt ran from the generated chat directory without
  `tools/fw.py`; second ran at a stale repository checkout before main update.
  These are discovery failures, not installer checks.
- Worker incorrectly probed root `FRAMEWORK.md` and the brief before merging
  main. Read corrected `docs/agents/FRAMEWORK.md` and main's brief afterward.
  Later absent `10-release-validation-summary.md` probe exit1 was corrected
  to the existing `10-release-validation.md`; no candidate check failed.
- Brain's initial Steam launch had no target window; fresh `list_windows`
  returned Steam successfully.
- Protected-hash CSV was accidentally included in a live pipeline while being
  written, causing a file-in-use warning. Recreated hash list excluding CSV;
  verified all14 source/copy pairs afterward.
- Windows PowerShell rejects `Tee-Object -LiteralPath` with `-Append` as an
  ambiguous parameter set. First logging harness exit1; corrected harness uses
  buffered output and `Add-Content`. Retained successful checks in
  `windows-checks.txt`.

## Automated Windows checks

At `d83f858`, candidate production: 271 tests passed, two privileged symlink
tests skipped; Ruff, compilation, framework hygiene and both shortcut pin/
line-ending checks passed. See `windows-checks.txt` for exact commands, real
outputs and individual exit codes. These results establish no hardware smoke
scenario.

Native archive tool: bsdtar/libarchive3.8.8. `git diff --exit-code` confirmed
installer, shortcuts and schema fixture equal to the candidate (exit0).
Advisory `tools/check_pins.py` exited1: MGSHDFix4.1.2 and MGSM2Fixv3.7.3
are available. Candidate pins remain4.1.0/v3.6; both bugfix pins current.
No update was made. Live newer-version discovery is not candidate validation.
