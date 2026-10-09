# 14-mgs4-patriotfix: independent Verifier review

Reviewed PR #19 at **48cfa4127a4f77080cec55263c2477166826b67b** on 9 October 2026.
Dispatch: `095a3b1b03d8bb543aa929069eca501b9e7cd8fa`.
Isolated detached seat; production diff inspected before Worker summary.

## Findings and verdict

**BLOCKER — MGS4 removal deletes an untracked file**, `install.py:2845–2854`.
MGS1 legacy cleanup runs unconditionally for MGS4. Reproduction: place an
untracked root `MGSM2Fix.asi`, install MGS4, then remove it. Install preserves
the file and records no backup/ownership; removal deletes it and reports success.
The independent actual-archive probe confirms permanent loss of those user bytes.
Limit legacy cleanup to the appropriate game and preserve unowned MGS4 files.

**SHOULD FIX — incomplete source authentication**, `tools/capture_patriot_schema.py:87–94`.
The inventory/hash boundary includes only `.cpp`/`.hpp`, omitting compiled headers
such as `src/resources/stdafx.h` and `ConfigTool/pch.h`. HEAD alone does not
prove working-tree bytes. Independently appending `#error Unreviewed compiled
header` to the former leaves capture successful and its JSON identical, despite
invalidating compilation. Authenticate these inputs and reject drift; correct the
“whole-source”/“all source drift” claims. The header was restored afterward.
No missing keys were demonstrated in the clean release.

**NOTE — native compatibility remains unproved.** Windows/Deck Config Tool
exports, GUI rendering, actual ASI initialization, licensed boot/gameplay, DS3,
flashback behavior and real repair/removal are **NOT RUN**. The Worker handoff
correctly retains these gates.

Verdict: **BLOCKED for acceptance** by destructive MGS4 removal; source
authentication also needs correction. No production changes, acceptance, merge,
release, tag or publication performed. Brain decides disposition.

## Goal judgments

Met offline: MGS4 identity/root/save mapping, official 0.2.2 tag/archive/hash,
exact ten-file payload, separate Launcher/game loaders and upstream Proton
option; all 28 settings, 24 runtime reads, hidden PW fields, valid language pairs,
conservative rendering defaults and disabled update checks. Fresh official source
independently checked; MGS1–3 definitions/pins unchanged.

Met in disposable fixtures: selection/settings flow, custom/hidden-value
preservation, reset, unmanaged-loader refusal, corrupt manifests/journals, linked
settings refusal, oldest backups, interrupted repair, cancellation, mixed-game
failure/success reporting and removal. Additional probes use authenticated archive
bytes for MGS4; every omitted key refuses. Full UI interrupted repair preserves
custom values; later-game cancellation preserves the first game's commit.
Real hardware behavior: cannot tell.

## Checked

[Exact commands, output and exits](evidence/14-mgs4-patriotfix-verifier/checks.txt),
[reproducible probes](evidence/14-mgs4-patriotfix-verifier/probes.py),
[probe output](evidence/14-mgs4-patriotfix-verifier/probes.txt),
[live archive/pin checks](evidence/14-mgs4-patriotfix-verifier/live-pins.txt) and
[source audit](evidence/14-mgs4-patriotfix-verifier/source-audit.md).
314 pytest tests passed; Ruff, compilation, framework check/status, Python 3.9
syntax, both v2.3.0 shortcut hashes/line endings and immutable framework comparison
passed (exit 0). All five live archive checksums match (exit 0). Advisory pin
check reports newer HDFix/M2Fix (exit 1); no upgrades authorized or made.
Four exact-delivery CI jobs passed, run 37792516531.
Desktop validator unavailable locally (lookup exit 1); Linux CI supplies validation.

## Failed or blocked

Initial framework clone used `4.0.0` instead of `v4.0.0` (exit 128); corrected.
Initial CI lookup used the upstream repository (404); corrected to this repository.
Evidence-only lint initially found three E402 imports; annotations added, rerun
passed. Native gates remain unavailable in this verifier seat.
