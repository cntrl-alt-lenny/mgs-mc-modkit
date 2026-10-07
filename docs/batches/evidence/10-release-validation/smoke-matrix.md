# 2.3.0 real-machine results

Candidate: `15d9277196e7bd1cfbd45fe280a230050b276bed`.
Checklist: `docs/RELEASING.md` at that commit. No real-machine scenario has
run. **Release readiness is blocked.** CI and synthetic fixtures are separate
evidence. NOT RUN means no observation; N/A means this checklist does not
require that platform. Replace each NOT RUN separately after collecting its
run record; do not inherit one game's or platform's result for another.

Run the candidate's local `install.py` after checking out the literal SHA
above and verifying its installer hash (`python3 install.py` on Deck/Linux;
`py -3 install.py` or `python install.py` on Windows). Do not use the latest
published shortcuts for candidate testing: the observed latest release is
2.2.0, and a v2.3.0 release asset is unavailable. Static shortcut pins match;
runtime asset download/hash verification remains pending publication and must
be recorded separately. See `discovery-and-release.txt` for release queries.

## Access and dependencies

| ID | Dependency | Current evidence |
| --- | --- | --- |
| H | Windows or Steam Deck/Linux validation host, agreed access and preserved baseline | Worker shell is Darwin/macOS, Python 3.9.6; configured SSH file absent. No suitable host or licensed game installation was made available to this seat. Brain is resolving access. |
| G | Licensed MGS1, MGS2 and MGS3 with recorded Steam build IDs and stock baseline | Unavailable to this seat; game builds, boot behavior and save state unknown. |
| P | Real upstream mod archives matching candidate checksums | Pins recorded below; archives not downloaded/extracted in this batch. |
| A | Owner-supplied compatible Nexus audio payload | Unavailable; filename/version/hash and compatibility unknown. Payload must not be redistributed. |
| V | Steam verification access and retained recovery records | Requires H/G, original-file hashes and an agreed destructive-test baseline. |

Brain must arrange a Windows host and a Steam Deck/Linux host, a supported
interactive shell/session with native GUI display, licensed installations of
all three games, network access to official archives, and owner-supplied audio
for the optional/large-audio scenarios. Record existing mods, saves and recovery
state first. No licensed stock baseline may be manufactured from synthetic
fixtures; no unattended Steam verification is authorized by this matrix.

## Scenario matrix

| ID | Action and required observation | Windows | Deck/Linux | Dependencies |
| --- | --- | --- | --- | --- |
| 01 | Fresh install completes for all three titles; retain per-game verification and log | NOT RUN | NOT RUN | H/G/P |
| 02 | MGS1 starts from the installed baseline; record region, menus and playable scene | NOT RUN | NOT RUN | 01 |
| 03 | MGS2 starts; no missing settings/schema errors; record playable scene | NOT RUN | NOT RUN | 01 |
| 04 | MGS3 starts; no missing settings/schema errors; record playable scene | NOT RUN | NOT RUN | 01 |
| 05 | Change an option per game and record saved settings and observed behavior | NOT RUN | NOT RUN | 02–04 |
| 06 | Repair each title completes without losing saves, originals or recovery records | NOT RUN | NOT RUN | 05 |
| 07 | Custom language/resolution survives repair independently per game; retain before/after settings | NOT RUN | NOT RUN | 06 |
| 08 | Removal completes per title, identifies any required Steam verification and preserves saves | NOT RUN | NOT RUN | 06/V if needed |
| 09 | MGS1 starts stock after removal; compare to baseline | NOT RUN | NOT RUN | 08 |
| 10 | MGS2 starts stock after removal; compare to baseline | NOT RUN | NOT RUN | 08 |
| 11 | MGS3 starts stock after removal; compare to baseline | NOT RUN | NOT RUN | 08 |
| 12 | Proton launch options are recorded; all three modded and stock boots work with applicable options | N/A | NOT RUN | H/G; 02–04/09–11 |
| 13 | Install optional audio and hear expected sound in each applicable title; record payload identity | N/A | NOT RUN | H/G/P/A |
| 14 | Cancel during extraction of a real install/repair; restoration completes and prior files/settings match baseline | N/A | NOT RUN | H/G/P; preserved baseline |
| 15 | Launch the restored game after cancellation and confirm saves still load | N/A | NOT RUN | 14 |
| 16 | Native progress window renders, responds and shows progress/cancellation results | N/A | NOT RUN | 01/06/14 |
| 17 | Session logs persist, identify each operation/outcome and permit recovery diagnosis | N/A | NOT RUN | 01/06/08/14 |
| 18 | Large-audio removal reports Steam verification needed and retains cleanup/hash records | NOT RUN | NOT RUN | H/G/A/V |
| 19 | Steam verification restores large originals; record identity and original-hash comparison | NOT RUN | NOT RUN | 18/V |
| 20 | Repeat removal finishes cleanup; originals/saves retained and applicable stock boots succeed | NOT RUN | NOT RUN | 19 |
| 21 | Second repair while another process holds the same game's lock refuses without changing files | NOT RUN | NOT RUN | H/G; controlled first process |

## Candidate inputs

| Component | Candidate pin | Expected archive SHA-256 |
| --- | --- | --- |
| Kit installer | 2.3.0 | `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5` |
| MGSHDFix | 4.1.0 | `413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523` |
| MGSM2Fix | v3.6 / archive 3.6.0 | `a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d` |
| MGS2 Bugfix Base | 3.0.0 | `a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003` |
| MGS3 Bugfix Base | 2.0.1 | `a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769` |

These are expected candidate inputs, not evidence that real archives or audio
were tested. Pins/schema remain unchanged. Each actual run must capture its
own fetched archive identity and checksum outcome.

## Run record to copy when resuming

Use one record per platform/scenario sequence. Preserve and review the stock
baseline, saves, settings, originals and existing recovery data before any
mutation. Follow README.md and troubleshooting guidance; stop on unexplained
recovery state. Record facts without personal paths, accounts or payload files.

| Field | Actual run value |
| --- | --- |
| Operator seat, UTC date/time, scenario IDs | NOT RUN |
| Candidate SHA / installer hash verified before execution | NOT RUN |
| Hardware model, OS/build, Python/archive tools, Proton version | UNKNOWN |
| MGS1/MGS2/MGS3 Steam build IDs, regions, executable hashes | UNKNOWN |
| Stock boot/save/settings baseline and protected-copy references | UNKNOWN |
| Actual mod versions, archive hashes and settings schema/export identity | UNKNOWN |
| Audio payload filename, version, local SHA-256, supported game | UNKNOWN |
| Initial/final Steam launch options | UNKNOWN |
| Exact commands/actions, observed output and command exit values | NOT RUN |
| Before/after file hashes, settings, saves and recovery-state comparison | NOT RUN |
| Log/screenshot evidence references; playable boot/audio observation | NOT RUN |
| Result per scenario (PASS/FAIL/BLOCKED), discrepancy and next action | BLOCKED: dependencies above |
