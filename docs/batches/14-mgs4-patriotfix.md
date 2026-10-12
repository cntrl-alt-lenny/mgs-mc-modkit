# 14-mgs4-patriotfix

## Done

Followed Brain correction brief at `9202bd82ca20c5b25eca9cb33c2af76ca2215710`.
Fast-forwarded PR #19 from production `868bebf712a7c11edcecd8b3afc636291a379cc4`
to review-only `03c58903d386c1c9bc0c9671e8c4b60c69ae30b6`; preserved the latest
Verifier report byte-for-byte and all historical evidence.

Correction production: `a6f3e0a4587482220483b51e7bddb012a49f5dda`. Present manifest
settings must be a JSON object during non-mutating preparation. Missing settings
retain the legacy default. Null, scalar and list settings refuse before any
selected game opens a live transaction. No settings are discarded or replaced to
make a malformed record pass.

[Constructor/preflight audit](evidence/14-manifest-preflight/assumptions.md)
compares every consumed record assumption; no additional mismatch found.
Only `_plan_validate_record` changes. InstallTxn, recovery, removal, original
recipes/writers, engine/embedding, audio acceptance, replay authentication,
transaction-directory fixes, 61 authenticated C++ inputs, 28 fields/24 reads,
MGS1–3 pins and PatriotFix 0.2.2 remain intact. Regenerated both unpublished
v2.3.0 shortcut hashes, preserving CMD CRLF and Python/desktop LF.

## Checked

[Actual commands, output and exits](evidence/14-manifest-preflight/checks.txt)
state the literal production SHA. **439 pytest tests**, Ruff, compilation, framework
check/status, embedding parity/isolated standalone, Python 3.9 runtime/grammar,
independent shortcut tags/hashes/line endings, pinned framework copies and
preserved-production audit pass.

Twenty-eight malformed mapping regressions put each MGS1–4 game last after real
options collection, forbid transaction construction and compare complete
selected-game file bytes/directory membership, including records/backups.
Four schema-1/schema-2 all-game lifecycle variants exercise present/missing
settings, replay, repair, removal, custom metadata/settings, saves and oldest
backups. Official authenticated PatriotFix archive lifecycle/source checks and
all five live archive checksum comparisons pass. Earlier [integration checks](evidence/14-mgs4-plan-integration/checks.txt),
[attempts](evidence/14-mgs4-plan-integration/attempts.txt) and original correction
records remain historical evidence. Exact-delivery CI is checked after push and
reported with the literal delivery SHA.

## Not checked

Native Windows/Deck Config Tool exports, GUI, ASI initialization, licensed
boots/gameplay, DS3/flashbacks, real user audio and real-device repair/removal
remain **NOT RUN**. The [native handoff](evidence/14-mgs4-patriotfix/native-handoff.md)
still applies. Desktop validator unavailable locally; Linux CI supplies it.
Brain dispatches independent re-review. No acceptance, merge, tag or publication.

## Failed or blocked

Required production checks pass. Extra origin/main ancestry probe exited 1: main
contains PR #21 candidate tooling, explicitly non-blocking in Brain’s brief. The
check runner’s blanket ancestry assertion consequently failed; actual results
are preserved. No unrelated integration performed. Advisory newer upstream versions
are not authorization to change pins. Historical failed attempts remain linked
above. The old integration audit is historical: it compares the original review
bytes; the new audit explicitly authenticates the preserved latest review.
Native gates remain unavailable.
