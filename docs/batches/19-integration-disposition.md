# 19-integration-disposition — Brain

## Done

Reviewed both independent Verifier reports and the combined MGS4/engine delivery. Inspected the integration diff, new regressions, exact-head CI and preservation comparisons. This is Small Brain disposition/evidence, not the combined candidate's independent acceptance.

| Batch | Current delivery | Brain rerun | Disposition |
|:--|:--|:--|:--|
| 12 | `73d7b4582e85ac6a0f358c8666553d83ad814f05` | 335 passed | Both Verifier blockers confirmed; keep PR #22 unmerged |
| 16 | `e410523f34c82bf25266adba6e55c9c1616562ec` | 326 passed | Accepted for candidate tooling only; owner approval required for PR #21 merge |
| 14 | `868bebf712a7c11edcecd8b3afc636291a379cc4` | 408 passed | Combined implementation passes Brain precheck; dispatch final independent Verifier |

Worker 14 already incorporated both Batch 12 findings. Do not ask Worker 12 to duplicate those fixes. PR #19 is the intended combined engine/MGS4 integration path; retain PR #22 and its review as evidence, then retire it as superseded after the accepted combined implementation lands. Only one Verifier handoff is useful now; no independent Worker batch is ready without native inputs or a demonstrated correction.

## Checked

[Actual commands, outputs and exit codes](evidence/19-integration-disposition/). Reproduced all three transaction-directory obstructions and cached-archive substitution on Batch 12. At combined delivery, obstructions refuse before any game writes; late cache mutation refuses before the affected transaction, and source replacement during extraction cannot change privately authenticated replay bytes.

Confirmed unchanged mod-specific recipes, transaction/removal correction, 61-input source capture, 28 fields/24 runtime reads, authoritative plan/embed source and selection-acceptance tests. Fresh official PatriotFix source reproduces the fixture; all three edited compiled headers refuse. Actual authenticated PatriotFix ZIP passes mixed preparation/replay/repair/removal while preserving oldest settings, saves and unowned ASI bytes in disposable fixtures. Both shortcut hashes/tags, line endings, Python 3.9, embedding, lint/compile/framework and exact-head Windows/Linux CI pass.

Candidate source/five authentic archives and independent raw-header refusal pass again. The Verifier's synthetic-provenance NOTE is valid: structural success explicitly retains independent native review and does not authorize adoption. Shipping values remain unchanged.

Handoff commit `dad60c882713fddb08075bf49d478807be67aefa`: 283 tests, lint, compilation, framework checks, production isolation and six-copy pinned-source comparisons pass; see `handoff-checks.txt` and `handoff-guidance-checks.txt`.

## Not checked

Final independent review of combined commit remains pending. Native exports, GUI/ASI initialization, licensed Windows/Deck boots/gameplay, real user audio and real-device repair/removal remain NOT RUN. No shipping upgrade or release is approved.

## Failed or blocked

Batch 12 is blocked as a standalone merge; both fixes are now in Batch 14. Initial reuse of an expired temporary check helper failed (exit 2); recreated it and all three reruns passed. Evidence-only lint initially flagged 18 formatting/import-placement errors (exit 1); formatted the probes and annotated their required dynamic imports, then reran. Framework 4.0.1 is separate Small work. No production changes, merge, closure, tag or publication performed.
