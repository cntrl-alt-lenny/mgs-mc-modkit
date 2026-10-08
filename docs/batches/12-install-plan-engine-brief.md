# 12-install-plan-engine

Checked: separating preparation from execution touches protected transaction
behavior. Queue until batch 11 is reviewed and owner-approved for merge.
This foundation precedes the desktop interface, coordinated upgrades and MGS4.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Worker

Start with python3 tools/fw.py status; read AGENTS.md, framework, your
Worker card, docs/state.md and this brief. Start only after Brain confirms
batch 11 is merged. Use worker/12-install-plan-engine from latest main in
.worktrees/worker-12-install-plan-engine. Preserve other seats.

Build the foundation for one setup application: collect choices, validate
a fixed installation plan, confirm once, then execute without routine prompts.
Develop on the M1 Mac; native Windows/Deck results remain separate.

Separate planning/preparation/execution from UI orchestration incrementally.
Keep existing UI entry points working. Do not replace the transaction engine.
Create a versioned plan containing selected games/paths, profile, exact pinned
packages/checksums, per-game settings, supplied archive identities/roles and
component order. Start with the existing curated MGS1–3 recipes.
Express dependencies/conflicts explicitly; do not permit incompatible choices.

Preparation must download and stage every selected payload, validate paths,
archive contents, generated settings and required space across relevant volumes
before the first live game-file write. Resolve user choices before execution.
Recheck relevant inputs under game locks before mutation; materially changed
inputs stop safely for replanning. Interrupted recovery must preserve history
and invalidate any assumptions it changes.

The executor takes a validated plan and emits progress/results; it performs
no file picking, confirmation or interactive Config Tool automation. Preserve
per-game commits, rollback, cancellation, concurrent refusal, saves, original
backups and recovery records. Report completed, restored and unstarted games
separately. Installed-file success must not imply playable-game success.

Add meaningful tests: invalid/incompatible plans rejected before live writes;
bad final payload causes zero earlier-game mutation; stale inputs stop safely;
per-game failure/cancellation preserves documented outcomes; executor requires
no UI prompts; normal repair/removal remain compatible with existing records.

Keep mod pins/version unchanged; no new games, profiles or desktop UI redesign.
Regenerate both shortcut hashes for install.py changes and verify tags/SHA256
and line endings. Run full pytest, Ruff, compilation, framework check/status,
relevant UPGRADING checks and desktop validation where available. Record actual
commands/output/exits at exact commits; mark hardware checks NOT RUN.

Commit docs/batches/12-install-plan-engine.md with the four required sections,
under 500 prose words, evidence in attachments. Push, open a draft PR and
return the delivery SHA and native validation handoff. Technical questions
go to Brain. Never approve, merge, tag or publish.
```

## Verifier prompt

Send only after Brain supplies the literal Worker delivery SHA.

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Verifier

Start with python3 tools/fw.py status; read project/framework rules, your
card and this brief. Review Brain's literal Worker delivery SHA in isolation,
diff before summary. Trace plan identity, preparation ordering, dependencies,
stale-input checks and recovery. Independently exercise late-payload failure,
cancellation, per-game outcomes and preservation. Check old install records
and repair/removal compatibility. Ensure executor paths need no routine UI.

Re-run required checks, verify both shortcut pins/line endings and inspect CI.
Native Windows/Deck behavior remains unproven without actual observations.
Change only docs/batches/12-install-plan-engine-review.md on the Worker branch.
Record reviewed SHA, commands/results, goal judgments and concrete findings;
under 500 prose words. Commit, push, return review SHA. No production edits,
approval, merge, tag or publication.
```
