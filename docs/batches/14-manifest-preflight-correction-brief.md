# Batch 14: complete record assumptions before live replay

Checked correction. Send the Worker prompt now. The final Verifier found one concrete preflight omission, reproduced by Brain; prior findings are corrected. PR #21 tooling is merged and does not block this work.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 14-mgs4-patriotfix · Worker

Start with python3 tools/fw.py status. Read AGENTS.md, framework/Worker card, docs/state.md, original/integration briefs, Batch 20 disposition and the final combined review. Fetch origin; continue the existing isolated branch and PR #19 by fast-forwarding to preserved review head b646a768e1e4c848b00aea090a73b905909dc4ed. Do not discard the review or historical evidence.

Fix the demonstrated all-game record-preflight omission. At production 868bebf712a7c11edcecd8b3afc636291a379cc4, valid MGS4 schema-1 game/file/mod lists with settings null, 42 or ["invalid"] pass collection/preparation, then the live constructor's dict conversion fails after MGS1–3 commit. Validate all record assumptions consumed by InstallTxn before any selected game's live files change, especially settings. Inspect constructor versus preflight systematically so another omitted record field does not require a further corrective batch.

Keep validation non-mutating: never construct a live transaction during preparation. Preserve absent-settings compatibility, valid schema-1/schema-2 records, supported custom values, records/backups/saves and existing transaction/recipe contracts. Refuse malformed records rather than discarding settings, deleting records or silently replacing them with defaults. Keep all prior removal, source-header, audio-acceptance, transaction-directory and private replay-identity fixes. No pin/schema/profile, native-evidence or release change.

Prove null, scalar and malformed-list settings on a late selected game refuse before any earlier game commits; cover MGS1–4 as appropriate. Each rejection must preserve complete selected-game snapshots and records/backups. Cover missing settings and valid old/new records through successful preparation/replay/repair/removal and custom-value preservation. Add meaningful regressions around any further constructor/preflight mismatch you actually identify. Do not broaden into a transaction redesign.

Run full pytest, Ruff, compilation, framework check/status, embedding parity/isolated standalone checks, Python 3.9 and applicable UPGRADING checks. Regenerate and independently verify BOTH unpublished v2.3.0 shortcut tags/SHA256/CRLF/LF. Require green exact-delivery Linux/Windows CI; native checks remain NOT RUN unless performed. Update the existing four-section Batch 14 summary with literal commits, actual commands/output/exits and limitations; push and return the new delivery SHA. Never accept, merge a PR, tag or publish. Technical questions go to Brain.
```

## Verifier prompt

Send only after the Worker finishes and Brain supplies the new literal delivery SHA.

```text
MGS Master Collection Mod Kit · BATCH 14-mgs4-patriotfix · Verifier

Start with framework status and read project rules/card. Review Brain's new literal delivery SHA in isolation. Reproduce malformed manifest settings through real collection/preparation, and compare every field consumed by the transaction constructor against non-mutating preflight. Require refusal before all selected-game writes while preserving valid/missing settings compatibility and complete snapshots. Recheck prior findings, combined-game behavior, shortcuts, required checks and exact-head CI. Native limits remain explicit. Change only the existing Batch 14 review; commit/push and return reviewed/review SHAs. No production changes, acceptance, merge or release.
```
