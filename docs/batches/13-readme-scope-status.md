# 13-readme-scope-status

Path: Small (Brain; documentation only).

## Done

Clarified the README's implemented Volume 1 scope, explicitly identifying MGS4
and Peace Walker as not integrated. Replaced the unsupported Steam Deck verified
badge with validation pending and linked native release requirements. No product,
mod pin, framework or standing scope change.

Completed Brain review of batch 11 at Verifier delivery
`84e6737aa26c5f24e49312637cf49e76cc0bedb2`, whose only addition to reviewed Worker
`fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c` is its review document. No blocking
finding identified; source/offline correction is acceptable for owner-approved
merge. Native validation and publication remain separate outstanding gates.
The [Brain disposition](evidence/13-readme-scope-status/brain-disposition.md)
records actual checks and limits.

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
production remains byte-identical to main. Commands/results are in the disposition.

## Not checked

Native exports, corrected-candidate Windows/Deck initialization, gameplay,
audio and actual repair/removal remain NOT RUN. No MGS4 integration or external
implementation outside the fetched repository was reviewed. No merge or release.

## Failed or blocked

No technical check failure. One documentation patch used a nonmatching context
and was refused without writes; corrected context succeeded. Owner approval is
required before merging. A clarification
about the user's reference to implemented MGS4 support was requested; the
README draft reports only the repository evidence available here.
