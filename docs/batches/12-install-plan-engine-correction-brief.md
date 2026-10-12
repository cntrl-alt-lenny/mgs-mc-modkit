# Batch 12: audio acceptance identity correction

Checked. Brain reproduced this at delivery `8297142978fc2b6932fc2c0af9485b4b074e09c5`. Continue the same batch; do not create a new feature batch.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Worker

Run framework status; read project rules/card and Brain's batch 17 review/probes. Fetch origin and continue worker/12-install-plan-engine from its current delivery in your isolated seat. Preserve unrelated seats, source history and the standalone/sandbox design. Do not wait for batches 14/16, banner approval or planning merges.

Fix selection-time audio acceptance identity. At present _accept_audio_file classifies one archive, but the choice stores only its path. _plan_packages later hashes whatever bytes are now at that path, and prepare accepts missing_identity/unknown_mod/ambiguous without proof that these exact bytes and role received the necessary confirmation.

Capture the accepted digest, game, role and classification/explicit acceptance as part of upfront selection. Verify a stable identity across classification and any confirmation, then carry it into plan creation and later rechecks. Replacing bytes after selection, including while changing settings/rebuilding the review screen, must invalidate acceptance and require selection/reconfirmation before any game writes. Do not silently rebind the choice to a new digest. Preserve confident matches and unchanged explicitly accepted uncertain files without additional executor prompts. Preserve independently selectable components and existing hard rejects. Brain assigns this input-collection/acceptance metadata to Worker 12; leave mod writers/pins/schema and Worker 16 tooling alone.

Use the committed Brain audio probe as a failing scenario and add meaningful end-to-end coverage for a confident file replaced by missing-identity bytes, a confirmed uncertain file replaced by different uncertain bytes, changes during review/settings loops and unchanged accepted files. Assert rejection before every selected game is mutated. Existing no-executor-interaction, rollback/recovery, cancellation, old-record and standalone/parity checks must remain green.

Run full pytest, Ruff, compilation, embedding check, framework check/status and applicable UPGRADING checks. Regenerate and independently verify both shortcut tags/SHA256 and line endings; desktop validation where available. Preserve Python 3.9. Record exact commits, actual commands/output/exits and unavailable native checks. Update the existing four-section batch summary/evidence, push to PR #22 and return literal delivery SHA plus exact-commit CI. Never accept, merge, tag or publish.
```

## Verifier handoff

After correction, Brain supplies a literal new SHA. A separate Verifier must independently review selection/confirmation identity through collection, review loops, preparation and execution; repeat the counterexamples and transaction/standalone checks, verify shortcuts/CI, and record findings only. The old delivery must not be accepted on green CI alone.
