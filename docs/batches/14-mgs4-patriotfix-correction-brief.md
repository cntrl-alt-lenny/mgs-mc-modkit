# Batch 14: removal and source-authentication correction

Checked. Brain confirms the separate Verifier's findings at production `48cfa4127a4f77080cec55263c2477166826b67b`; current review head `38ef1b6a679411d48b784a8142aed797ae170117` has no production fix.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 14-mgs4-patriotfix · Worker

Run framework status and read project rules/card, the batch 14 Verifier review and Brain's batch 17 reproductions. Fetch origin; fast-forward your clean worker/14-mgs4-patriotfix seat to the pushed review head before continuing. Preserve the review/evidence and unrelated seats; no force-pushing or discarding. Do not wait for batch 12/16 or documentation merges.

Fix P1 removal first: _uninstall_game executes MGS1 legacy MGSM2Fix.asi deletion unconditionally, before ownership validation. With an unowned root MGSM2Fix.asi, MGS4 install preserves it and records no ownership/backup, but removal permanently deletes it and reports success. Limit legacy behavior to reliably identified appropriate-game cases. MGS4 and other non-MGS1 or ambiguous roots must preserve unrelated/unowned files; malformed records must not authorize destructive cleanup. Keep legitimate tracked-file restoration/removal, oldest backups, journals and saves intact.

Fix the P2 capture boundary: cpp/hpp inventory misses compiled headers including src/resources/stdafx.h and ConfigTool/pch.h. Extend the authenticated reviewed input inventory to cover the relevant compiled headers and reject additions, omissions and byte drift. Authenticate the official literal source, regenerate the fixture independently and state the actual bounded scope; do not claim complete build/binary reproducibility. Keep the same upstream version/archive SHA and audited settings/runtime field set unless source evidence requires a separately explained change.

Add regressions for unowned legacy-named files across MGS4 and other non-MGS1 removal, valid tracked restoration and corrupt/ambiguous records. Mutating each newly authenticated header at unchanged HEAD must refuse; clean official source must reproduce the fixture. Re-run the independent actual-archive removal probe in disposable fixtures.

Run full pytest, Ruff, compilation, framework checks/status, source/archive/settings checks and exact-commit CI. For install.py edits regenerate and verify both shortcut hashes/tags and CRLF/LF; desktop validation where available. Preserve Python 3.9 and unchanged MGS1–3 pins/recipe contracts. Update the existing four-section summary/evidence, push PR #19 and return the literal delivery SHA. Native exports/boots/gameplay/real restoration remain NOT RUN. A separate Verifier rechecks the new SHA. Never accept, merge, tag or publish.
```
