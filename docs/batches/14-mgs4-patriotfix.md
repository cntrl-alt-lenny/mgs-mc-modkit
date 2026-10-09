# 14-mgs4-patriotfix

## Done

Implemented MGS4 discovery, upfront settings, official PatriotFix 0.2.2 install,
repair/removal and individual outcomes from batch 14's original brief. Retained
all 28 settings, 24 runtime reads, hidden PW controls, conservative rendering
defaults and disabled update checks; custom values survive supported repairs.

Continued by fast-forwarding to pushed Verifier head `38ef1b6`; its review and
original evidence remain unchanged. Followed correction brief at `fbc360f`.
Legacy MGSM2Fix cleanup now requires an unambiguous MGS1 executable layout and,
when present, a validated matching record. Orphan/malformed/unknown records and
non-MGS1 roots cannot authorize legacy deletion. Tracked files use normal
restoration/removal, retaining oldest originals.

Authenticated inventory now includes `ConfigTool/pch.h`, `src/resources/stdafx.h`
and `src/resources/version.h`: 61 `.cpp`/`.hpp`/`.h` files under `src/` and
`ConfigTool/`. Fresh official checkout blobs plus upstream CRLF attributes were
independently compared against every hash; capture independently reproduces the
fixture. Only three hashes changed; archive/version, fields/runtime reads,
constraints and MGS1–3 pins/definitions remain unchanged. Build projects,
resources, external dependencies and binaries are outside this bounded capture.
Both shortcut hashes regenerated at unpublished 2.3.0.

## Checked

Correction implementation `1aebf38b82680cefe777b474921a19670a2d774a`:
**320 tests**, Ruff, compilation, framework check/status, Python 3.9 grammar,
shortcut tags/SHA-256/CRLF/LF, immutable framework comparison and unchanged
MGS1–3 definitions/pins pass. New regressions cover non-MGS1/ambiguous/no-record
removal, corrupt/unknown/orphan records, tracked removal/oldest restoration, and
header mutations, omissions and additions.
[Correction commands/output/exits](evidence/14-mgs4-patriotfix-correction/checks.txt)
and [source audit](evidence/14-mgs4-patriotfix-correction/source-audit.py) retain
literal commit/check results. All five live archive checksums match. The adapted independent actual-archive probe uses
a freshly downloaded official ZIP and disposable fixtures: unowned legacy bytes,
oldest settings/save bytes, interrupted repair, unsafe journal/linked settings
refusal and mixed cancellation verified. Original Verifier probes remain intact. Four exact-production CI jobs pass at
`1aebf38` ([run 37928302625](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37928302625));
final delivery CI is linked from PR #19.

## Not checked

Native Windows/Deck Config Tool exports, GUI rendering, ASI initialization,
licensed boots/gameplay, DS3, flashback behavior and real repair/removal remain
**NOT RUN**. [Native handoff](evidence/14-mgs4-patriotfix/native-handoff.md) remains
applicable. Desktop validation is unavailable locally; Linux CI supplies it.
Separate Verifier re-review at the delivery SHA and Brain disposition remain
required. No approval, merge, tag, release or publication performed.

## Failed or blocked

Historical failures remain in original evidence/summary history. Initial header
blob equality assertion ignored upstream CRLF checkout attributes; corrected
by authenticating literal blobs plus declared line endings. Plain diff-check
flags required Windows CRLF as whitespace; `core.whitespace=cr-at-eol` passes.
Advisory newer-upstream pins do not authorize upgrades. Native hardware gates
remain unavailable in this Worker seat.
