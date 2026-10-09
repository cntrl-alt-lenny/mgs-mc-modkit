# 17-delivery-disposition — Brain

Path: Small; exact-commit review evidence and correction handoffs only.
This is Brain disposition, not an independent Verifier review of batches 12/16.

## Done

Reviewed batch 12 at `8297142978fc2b6932fc2c0af9485b4b074e09c5`, batch 16 at
`0e909f639f7687839c4fe3e3af37c551b3b36467`, and batch 14 production delivery
`48cfa4127a4f77080cec55263c2477166826b67b` plus Verifier/evidence head
`38ef1b6a679411d48b784a8142aed797ae170117`. The two later MGS4 commits change
only review/evidence; no production correction follows the Verifier findings.

Disposition: all three production/tooling candidates require focused correction.
No acceptance, merge, tag or release. Shipping pins remain unchanged in batch 16.

## Checked

Read real code diffs, Worker summaries, the independent MGS4 review and CI.
Reran full suites: batch 12 312 passed, batch 14 314 passed, batch 16 314 passed.
Ruff and compilation pass on all three; batch 12 embedding parity passes.
Batch 12's four CI jobs pass; batch 16's Linux jobs pass and Windows fails.
MGS4's production-delivery CI passed; docs-only review head has no new jobs.

Independently reproduced four findings:

| Severity | Batch | Finding |
|:--|:--|:--|
| P1 | 14 | MGS4 removal permanently deletes unowned root MGSM2Fix.asi with no backup, then reports success. |
| P2 | 14 | Changing compiled stdafx.h at the same source HEAD is accepted; .h files are outside capture inventory. |
| P2 | 12 | Audio bytes replaced after selection are newly hashed into the plan; missing-identity replacement installs without renewed uncertain-file confirmation. |
| P2 | 16 | Windows ZIP reader normalizes raw backslash names before the unsafe-path check; the validator can accept the normalized layout. Existing writer fixture also normalizes its name, causing red Windows CI. |

All five candidate archive hashes/layouts/CRCs and authenticated 134-field
source capture passed independent rerun. Existing shipping installer/shortcuts
are unchanged on batch 16. Checked both shortcut identities on installer branches.
[Reproductions and check evidence](evidence/12-14-16-brain-review/checks.txt)
state commits, commands, outputs and exits; fixtures are disposable.

## Not checked

Batches 12/16 lack independent Verifier review. Corrected commits need full
checks and exact-commit review. Cross-branch installer integration has not run.
Actual native exports, GUI, licensed game boots, user audio compatibility and
real repair/removal remain NOT RUN. No production conclusion follows from
Mac fixtures or green CI alone. Framework 4.0.1 is a separate Small update.

## Failed or blocked

Confirmed defects block acceptance; passing suites miss these scenarios.
Prepared correction briefs for existing batches 12, 14 and 16. They can proceed
independently in existing isolated seats; no review/documentation merge is a
start gate. Brain owns integration order; implementation conflict repairs and
hash regeneration remain Worker work. Native exports still gate adopting the
new QoL shipping set. No new feature scope is added by these corrections.
