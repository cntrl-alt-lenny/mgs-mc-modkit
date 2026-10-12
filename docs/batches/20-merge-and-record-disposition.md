# 20-merge-and-record-disposition — Brain

## Done

Owner explicitly approved PR #21 as tooling only. Rechecked unchanged delivery `e410523f34c82bf25266adba6e55c9c1616562ec` and all four green CI jobs, marked the reviewed draft ready and merged it at `bd8546524886614a04f5629b1fbbf1f741b73163`. Fast-forwarded clean main. Candidate tooling/docs/tests only; installed pins, schema, installer, shortcuts and framework remain unchanged. Finished Batch 16 seats/branch are retired after clean/merged-ancestry checks; review/evidence remain in main.

The final MGS4 Verifier report arrived concurrently at `b646a768e1e4c848b00aea090a73b905909dc4ed`, reviewing production `868bebf712a7c11edcecd8b3afc636291a379cc4`. Read its verdict and confirmed the single new BLOCKER independently. The earlier four findings remain corrected. PR #19 is still unmerged; dispatch one focused Worker correction, then re-review its new literal delivery.

## Checked

Post-merge main tree equals the independently reviewed Batch 16 delivery. Protected shipping files equal previous main `85697bd5a18ddb43acd3b121184b3624871781e4`. `python3 -m pytest tests/test_volume1_candidate.py -q`: 43 passed, exit 0; framework status/checks pass and main is clean.

MGS4 schema-1 records with `settings` equal to null, 42 or `["invalid"]` pass options collection/preparation. During replay, MGS1–3 commit; MGS4's constructor raises `CorruptManifestError` converting settings to a dict. MGS4 files stay unchanged. This violates all-game preflight of knowable record assumptions, without demonstrating save loss. Actual reproducer/output are in [evidence](evidence/20-merge-and-record-disposition/).

Handoff at `e9477fc`: 283 tests, Ruff, compilation, framework check, shortcut/line-ending/3.9 checks pass; see `handoff-checks.txt`.

## Not checked

Corrected manifest preflight is not implemented yet. Native exports, game boots, ASI initialization, real user audio and real-device restoration remain NOT RUN. Neither MGS4 merge nor shipping upgrades/releases are authorized.

## Failed or blocked

Initial merge attempt failed because the PR was still draft (exit 1); marking ready under explicit merge authorization resolved it. A premature post-merge test attempt on pre-merge main found no candidate test file (exit 4); the actual post-merge rerun passed. No checks were waived. MGS4 remains blocked by incomplete record validation. A second independent Worker task is not ready; do not duplicate already integrated engine fixes or invent occupancy work.
