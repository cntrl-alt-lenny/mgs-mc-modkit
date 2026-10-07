# 2.3.0 real-machine results

Candidate: `15d9277196e7bd1cfbd45fe280a230050b276bed`.
Checklist: `docs/RELEASING.md` at that commit. Windows trials now have actual
observations; Windows trials are recorded below. **Release readiness is blocked.** CI and synthetic fixtures are separate
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
| H | Windows or Steam Deck/Linux validation host, agreed access and preserved baseline | Windows11Pro/build26300.9550 reached; preserved inventories and hardware identity in windows-run.md. Deck remains unavailable. Earlier Mac access limitation remains historical evidence. |
| G | Licensed MGS1, MGS2 and MGS3 with recorded Steam build IDs and stock baseline | Steam-installed: MGS1 build20872173, MGS2 build21578573, MGS3 build22192289. Stock MGS2/3 title observed; MGS1 launcher only; playable remains unproven. |
| P | Real upstream mod archives matching candidate checksums | All four actual archives downloaded/checksum-verified by exact candidate; fresh installation verification retained in windows-fresh-install.txt. |
| A | Owner-supplied compatible Nexus audio payload | Unavailable; filename/version/hash and compatibility unknown. Payload must not be redistributed. |
| V | Steam verification access and retained recovery records | Steam available, original-file hashes retained; large-audio restoration untested without payload. |

Windows access, licensed games, preserved baseline and official archive
downloads are now observed. Remaining dependencies include a Deck/Linux host,
owner-supplied compatible audio for optional/large-audio checks, and real
playable/control observations. The Windows candidate's live configuration
failures require a separately authorized production-fix batch; this validation
keeps installer/pins/schema/version unchanged. Existing stock/save and
recovery observations are preserved. Owner-authorized default Steam installs
do not waive Deck checks or turn synthetic fixtures into hardware evidence.

## Scenario matrix

| ID | Action and required observation | Windows | Deck/Linux | Dependencies |
| --- | --- | --- | --- | --- |
| 01 | Fresh install completes for all three titles; retain per-game verification and log | PARTIAL: all3 content verified/committed and completion text observed; native acknowledgement/normal exit unproven, own pending process terminated(exit1) | NOT RUN | H/G/P |
| 02 | MGS1 starts from the installed baseline; record region, menus and playable scene | PARTIAL: injection/border art/black center; initial47s and separate repaired four-minute follow-up, no title/playable; abnormal exits | NOT RUN | 01 |
| 03 | MGS2 starts; no missing settings/schema errors; record playable scene | FAIL: launcher/game missing MSX Skip Launcher Game key; error console, no playable scene | NOT RUN | 01 |
| 04 | MGS3 starts; no missing settings/schema errors; record playable scene | FAIL: independent launcher/game same missing key; error console, no playable scene | NOT RUN | 01 |
| 05 | Change an option per game and record saved settings and observed behavior | PARTIAL: native Keyboard/Mouse/boot-straight changes saved; MGS1 external1024x768 rendered; MGS2 French1280x720/MGS3 Spanish1600x900 stored, runtime effects blocked | NOT RUN | 02–04 |
| 06 | Repair each title completes without losing saves, originals or recovery records | PARTIAL: all3 content verified; immediate save/userdata equality and original backup equality PASS; native acknowledgement/normal exit unproven, cleanup exit1 | NOT RUN | 05 |
| 07 | Custom language/resolution survives repair independently per game; retain before/after settings | PARTIAL: storage PASS independently MGS1 external1024x768, MGS2 fr1280x720, MGS3 es1600x900; MGS1 native language selection unproven | NOT RUN | 06 |
| 08 | Removal completes per title, identifies any required Steam verification and preserves saves | PARTIAL: production terminal-backend removal PASS/exit0; all9875/3790 originals and all common/remote save bytes preserved; MGS1 cache-only change cause unproven; native confirmation unavailable/cleanup exit1 | NOT RUN | 06/V if needed |
| 09 | MGS1 starts stock after removal; compare to baseline | PARTIAL: same native launcher boundary, absent mod modules, normal exit0; emulated title/playable unproven | NOT RUN | 08 |
| 10 | MGS2 starts stock after removal; compare to baseline | PARTIAL: actual EU-English game/HDtitle60FPS, no mod modules/error console, normal game+launcher exits0; playable unproven | NOT RUN | 08 |
| 11 | MGS3 starts stock after removal; compare to baseline | PARTIAL: actual US-English game/HDtitle60FPS, no mod modules/error console; game abnormal c0000005 like pre-kit stock, launcher exit0; playable unproven | NOT RUN | 08 |
| 12 | Proton launch options are recorded; all three modded and stock boots work with applicable options | N/A | NOT RUN | H/G; 02–04/09–11 |
| 13 | Install optional audio and hear expected sound in each applicable title; record payload identity | N/A | NOT RUN | H/G/P/A |
| 14 | Cancel during extraction of a real install/repair; restoration completes and prior files/settings match baseline | N/A | NOT RUN | H/G/P; preserved baseline |
| 15 | Launch the restored game after cancellation and confirm saves still load | N/A | NOT RUN | 14 |
| 16 | Native progress window renders, responds and shows progress/cancellation results | N/A | NOT RUN | 01/06/14 |
| 17 | Session logs persist, identify each operation/outcome and permit recovery diagnosis | N/A | NOT RUN | 01/06/08/14 |
| 18 | Large-audio removal reports Steam verification needed and retains cleanup/hash records | NOT RUN | NOT RUN | H/G/A/V |
| 19 | Steam verification restores large originals; record identity and original-hash comparison | NOT RUN | NOT RUN | 18/V |
| 20 | Repeat removal finishes cleanup; originals/saves retained and applicable stock boots succeed | NOT RUN | NOT RUN | 19 |
| 21 | Second repair while another process holds the same game's lock refuses without changing files | OBSERVED REFUSAL: actual second candidate stops at GameLock before InstallTxn/download; first continues legitimately; native error acknowledgement unproven, cleanup exit1 | NOT RUN | H/G; controlled first process |

## Candidate inputs

| Component | Candidate pin | Expected archive SHA-256 |
| --- | --- | --- |
| Kit installer | 2.3.0 | `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5` |
| MGSHDFix | 4.1.0 | `413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523` |
| MGSM2Fix | v3.6 / archive 3.6.0 | `a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d` |
| MGS2 Bugfix Base | 3.0.0 | `a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003` |
| MGS3 Bugfix Base | 2.0.1 | `a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769` |

These are candidate inputs. Windows actual verified downloads are retained
in windows-fresh-install.txt; no audio payload was tested. Pins/schema remain unchanged. Each actual run must capture its
own fetched archive identity and checksum outcome.

## Template run record to copy when resuming

The placeholders below are a template, not current Windows facts; see the
Windows run/phase logs/snapshots and poststock observations for actual values.
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
