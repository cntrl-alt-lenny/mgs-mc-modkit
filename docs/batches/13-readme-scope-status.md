# 13-readme-scope-status

Path: Small (Brain; documentation only).

## Done

Clarified the README's implemented Volume 1 scope, identifying MGS4 as planned
and Peace Walker as unsupported. Replaced the unsupported Steam Deck verified
badge with validation pending and linked native release requirements. No product,
mod pin, framework or standing scope change.

Completed Brain review of batch 11 at Verifier delivery
`84e6737aa26c5f24e49312637cf49e76cc0bedb2`, whose only addition to reviewed Worker
`fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c` is its review document. No blocking
finding identified. Following explicit owner approval, PR #17 was merged at
`67d1406fafb8f6e68f61f182665a2e1d9fc6f6a0`. Native validation and publication
remain separate outstanding gates.
The [Brain disposition](evidence/13-readme-scope-status/brain-disposition.md)
records actual checks and limits.

Following the owner's clarification, supplied the missing concrete MGS4 Worker
and Verifier brief. MGS4 follows batch 11; the launcher foundation follows MGS4
and covers all four implemented games. Planning does not claim implementation.

## Checked

At the Verifier delivery, Brain reran all 283 tests, Ruff, compilation, framework
check, shortcut/tag/byte checks and whitespace checks. All passed. Reran the
Verifier's inspected independent enumeration/preservation probe and the
authenticated source audit; both passed. CI is green at this exact delivery.

Fetched origin and inspected installer GAMES definitions on every local and
remote branch; all contain only mgs1, mgs2 and mgs3. Latest published release is
v2.2.0; development 2.3.0 has not been published. Reviewed the README changes
against those facts, framework/Brain guidance and native release requirements.

At `3538f49e79e1dafcf832b0aba0f3154ad7fd4b51`, framework check and diff checks
passed. All six framework copies match immutable 4.0.0 source and manifest;
production is unchanged from that documentation commit's main base `90967b9`.
Commands/results are in the disposition and [merge record](evidence/13-readme-scope-status/merge-completion-11.md).

## Not checked

Native exports, corrected-candidate Windows/Deck initialization, gameplay,
audio and actual repair/removal remain NOT RUN. No MGS4 integration or external
implementation outside the fetched repository was reviewed. No release.

## Failed or blocked

No technical check failure. Nonmatching documentation patch contexts were
refused without writes; corrected contexts succeeded. Owner approval is
required before merging this documentation PR. The owner confirmed MGS4 was an integration request;
the earlier Brain handoff had omitted its implementation prompt. That planning
gap is corrected by the new brief; code integration remains future Worker work.
