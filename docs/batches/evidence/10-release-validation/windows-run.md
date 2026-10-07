# Windows validation run (in progress)

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

UI actions do not expose process exit codes. Installation completion must be
observed separately; queue/download progress is not completion or game boot.

## Failed discovery/logging attempts retained

- Brain's first status attempt ran from the generated chat directory without
  `tools/fw.py`; second ran at a stale repository checkout before main update.
  These are discovery failures, not installer checks.
- Worker incorrectly probed root `FRAMEWORK.md` and the brief before merging
  main. Read corrected `docs/agents/FRAMEWORK.md` and main's brief afterward.
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
