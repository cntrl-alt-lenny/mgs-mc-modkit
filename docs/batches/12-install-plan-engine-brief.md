# 12-install-plan-engine

Checked: preparation/execution changes touch protected transaction behavior. Start independently from current main; no dependency on batch 14 or any planning/banner merge. This replaces the earlier queue rule.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Worker

Run python3 tools/fw.py status; read AGENTS.md, the framework, your Worker card, docs/state.md and this brief. Fetch origin and use worker/12-install-plan-engine from latest main in an isolated seat. Start now alongside batch 16; do not copy its work or unmerged batch 14.

Build the installation-plan/preparation/execution foundation: collect choices upfront, validate, confirm once, then execute without routine prompts. Keep existing entry points and InstallTxn. Own the new plan module, thin orchestration adapter and planning tests; leave mod pins, templates, schemas, capture tools and mod-specific writers to Worker 16. Keep their existing contracts.

Make plans versioned and game-neutral, using current MGS1–3 recipes through an adapter rather than copying pinned values. Include paths, profile, exact packages/checksums, supplied archive identities/roles, settings, order and incompatibilities. Preparation must stage and validate every selected payload, settings, paths and required space before the first live game-file write. Recheck relevant inputs under locks; stale inputs and recovery that changes assumptions require replanning.

The executor performs no picking, confirmation or Config Tool interaction. Preserve per-game commits, rollback, cancellation, concurrent refusal, saves, backups and recovery records. Report completed, restored and unstarted games separately. Installed files do not establish playability.

Test invalid/incompatible plans, a bad last payload causing zero earlier-game mutation, stale inputs, cancellation/failure outcomes, absence of routine executor prompts and compatibility with existing repair/removal records. No full GUI, new game, profile, pin or release change. MGS4 adapter integration follows accepted batch 14 later; it does not block this foundation.

Run full pytest, Ruff, compilation, framework check/status and applicable UPGRADING checks. Regenerate and verify both shortcut hashes/tags for install.py edits; preserve Windows CRLF/Python LF; run desktop validation where available. Record actual commands/output/exits at exact commits and hardware checks NOT RUN. Commit docs/batches/12-install-plan-engine.md with the four required sections, push and open a draft PR. Return delivery SHA. Brain coordinates integration; the affected Worker resolves code conflicts and repeats checks before a new exact-commit review. Never merge, tag or publish.
```

## Verifier prompt

Send only after Brain supplies a literal delivery SHA.

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Verifier

Run framework status and read project rules/card. Review Brain's literal SHA in isolation. Trace preparation ordering, identity, locks, stale inputs and recovery; independently test late-payload failure, cancellation, old records, repair/removal and preservation. Re-run required checks and verify shortcuts and CI. Record native limits. Write only docs/batches/12-install-plan-engine-review.md, citing the reviewed SHA and actual results; commit and push. No production edits, merge or publication.
```
