# 10-release-validation: Windows Verifier review

Reviewed literal Worker delivery `decf9fb0cd5c2cbf0dbb98fbabc0a14609583cb7`
in an isolated detached checkout. Candidate remains
`15d9277196e7bd1cfbd45fe280a230050b276bed`. Installer, shortcuts, pins,
schema and version are byte-identical to candidate. Windows 11 Pro
26300.9550, Ryzen 5800X/RTX2060 and Steam builds 20872173/21578573/22192289
agree across host, runtime and snapshot records. No game/UI operation ran during this review.

Independent Python comparisons reconstructed all seven phase reports, checking
unique paths and byte/hash pairs rather than helper assertions. The two
historical cache aliases were identified by their individual hashes. All
9875/3790 originals match stock backups and restored live paths; full stock
comparison has no missing files or changed assets/executables. Install and
immediate repair preserve saves/userdata. Removal preserves common/remote
save bytes; only MGS1 remotecache changes, cause unknown. Earlier and subsequent
game writes remain separate. Actual protected copies independently rehash to
14/16 files with zero mismatches. Settings hashes match phase snapshots;
1024x768, French 1280x720 and Spanish 1600x900 survive repair independently.

Actual archive verification logs, loaded-module versions, three modded trials,
post-stock process exits and all 15 screenshots support the limited observations.
Public text, NUL-normalized logs and six decompressed gzip inventories contain
no detected personal paths/account IDs; screenshots are clean. No save/game/audio
payload is distributed. Historical Mac access records are not Windows failures.

## Smoke judgments

Judgments concern complete requirements; verified partial content is identified.
Windows N/A rows have no Windows observation. Every Deck/Linux row is cannot tell
because no hardware run exists.

| Rows | Windows | Deck/Linux | Basis |
| --- | --- | --- | --- |
| 01 | Cannot tell | Cannot tell | All three content installations verified; final native acknowledgement/normal exit unknown. |
| 02 | Cannot tell | Cannot tell | Injection/border art, black center through four-minute follow-up; title/playable unproven, abnormal exits. |
| 03, 04 | Not met independently | Cannot tell | Each launcher/game reports missing MSX settings key. |
| 05 | Cannot tell | Cannot tell | Saved changes; MGS1 resolution effect observed, other runtime effects blocked. |
| 06 | Cannot tell | Cannot tell | All three repair contents and preservation verified; native completion exit unproven. |
| 07 | Cannot tell | Cannot tell | Per-game storage preserved; MGS1 native language remains unproven. |
| 08 | Cannot tell | Cannot tell | Production terminal removal/preservation met, exit 0; native confirmation unproven. |
| 09, 10, 11 | Cannot tell independently | Cannot tell | Stock launcher/title boundaries match baseline; controls/save loading unproven; stock MGS3 faults before/after. |
| 12, 13, 14, 15, 16, 17 | Cannot tell (N/A) | Cannot tell | Proton/audio/cancellation/restored play/progress/log sequence not run. |
| 18, 19, 20 | Cannot tell | Cannot tell | Compatible audio/Steam-verification/repeat-removal sequence absent. |
| 21 | Met | Cannot tell | Real second candidate fails GameLock before downloads/InstallTxn while first legitimately repairs; native error acknowledgement unknown. |

## Findings and verdict

**BLOCKER (release):** `install.py:355` omits `MSX Skip Launcher Game`;
actual 4.1.0 launcher/game readers for both MGS2/MGS3 stop configuration
initialization and leave error consoles. Content verification cannot establish
initialization. No production fix belongs in this batch.

**UNPROVEN CLAIM boundary:** `docs/batches/10-release-validation.md:47`
and `docs/batches/evidence/10-release-validation/windows-modded-observations.md:193` leave playable/control/native completion,
Deck and audio success unproven; forced own-process cleanup exits 1 cannot prove
normal acknowledgements. MGS1/stock MGS3 close-fault causality is unknown.

**NOTE:** `docs/batches/evidence/10-release-validation/windows-checks.txt:9` honestly records
raw-log whitespace exit 2; it is not a required brief check. Newer upstream pins
are advisory. No evidence BLOCKER or SHOULD FIX found. Verdict: evidence accepted
as scoped; candidate release readiness remains BLOCKED. PR15 remains draft;
no approval, merge, tag or publication.

## Actual commands and results at reviewed delivery

Local Windows Python 3.12.10, bsdtar 3.8.8; desktop validator unavailable locally.

| Command | Actual result | Exit |
| --- | --- | --- |
| `py -3 tools/fw.py status` | Framework 4.0.0; clean detached delivery; project checks pass | 0 |
| `py -3 -m pytest tests/ -q` | 271 passed, 2 privileged-symlink tests skipped, 14.14s | 0 |
| `py -3 -m ruff check .` | All checks passed! | 0 |
| `py -3 -m py_compile tools/fw.py install.py` and seven evidence helpers | No output | 0 |
| `py -3 tools/fw.py check` | 0 errors, 0 warnings | 0 |
| `git diff --exit-code 15d9277 -- install.py Install-MGS-Mods.cmd Install-MGS-Mods.desktop tests/fixtures/hdfix-4.1.0-schema.json` | No output | 0 |
| `py -3 docs/batches/evidence/10-release-validation/verify-pins.py`; independent AST/byte check | v2.3.0; SHA a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5; CMD CRLF, installer/desktop LF | 0 |
| `py -3 tools/refresh_checksums.py` | Four live primary release assets match pinned SHA256 | 0 |
| `py -3 tools/check_pins.py` | MGSHDFix 4.1.2/MGSM2Fix v3.7.3 available; no change | 1 |
| Independent PowerShell here-strings piped to `py -3 -` | Seven metadata report fields agree; all originals/restorations equal; protected 14/16 copies equal; privacy findings [] | 0 after corrected read-only path/probe attempts |
| `git diff --check origin/main...HEAD` | Actual raw-log whitespace, 545 output lines | 2 |
| `gh release view --json tagName,url`; `gh release view v2.3.0 --json tagName,url` | Latest v2.2.0; v2.3.0 release not found | 0; 1 |
| `gh pr view 15 --json isDraft,headRefOid,state,url` | OPEN/draft; literal reviewed delivery head | 0 |

Primary GitHub `gh run view <id> --json jobs,headSha,conclusion,event,url`
and `--log` queries returned 0. These CI results establish no hardware success.

| Run | Checkout identity | Actual successful test results |
| --- | --- | --- |
| [37525559856](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37525559856) | All four checkout logs: literal candidate 15d9277196e7bd1cfbd45fe280a230050b276bed | Linux 3.9/3.11/3.12: 273 passed 6.73/5.51/6.30s; Windows 271 passed, 2 skipped, 18.08s |
| [37647529127](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37647529127) | Metadata head decf9fb0cd5c2cbf0dbb98fbabc0a14609583cb7; Linux logs checkout PR merge a4e88ba2ace6b29c553ce18bc0126c7912ed4a25 into main 90967b9; Windows checkout step successful, its SHA absent from retrieved job logs | Linux 3.9/3.11/3.12: 273 passed 8.19/6.66/5.72s; Windows 271 passed, 2 skipped, 26.13s |

BATCH 10-release-validation: Reviewed; evidence accepted, release blocked.
