# Batch 16: Windows ZIP path validation correction

Checked. Brain reviewed `0e909f639f7687839c4fe3e3af37c551b3b36467`; Windows CI run 37920207041 is red. Continue the existing candidate-preparation batch.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 16-volume1-qol-upgrade · Worker

Run framework status; read project rules/card, Brain's batch 17 review/probes and the actual failed Windows CI log. Fetch origin and continue worker/16-volume1-qol-upgrade in your isolated seat. Do not wait for MGS4, batch 12, documentation merges or native capture before correcting this tooling.

Correct both raw-name validation and the failing fixture. archive_check uses ZipInfo.filename; Python's Windows ZIP reader normalizes backslashes before this check. Brain's raw-backslash ZIP has orig_filename a\b but filename a/b; the validator accepts it when the expected normalized layout matches. Validate original member names and refuse unsafe/lossy normalization rather than relying on normalized names. Preserve full SHA/size, exact layout, CRC and payload checks without extraction; retain collision/traversal/link refusal. Reject truncation/hidden unsafe bytes that normalization would conceal.

The current unsafe-path test writes a string name a\b through Windows ZipInfo, which becomes a/b in the ZIP and fails only layout comparison. Construct a fixture whose actual serialized member retains the intended unsafe name, assert that raw identity before validation, and require the unsafe-path refusal. Do not weaken the regex or accept a layout-only failure as proof. Cover Windows reader normalization as well as native Linux/macOS behavior; require real Windows CI green.

Re-run official five-archive and authenticated source checks to prove legitimate candidates remain valid. Shipping install.py, shortcut pins, templates/schema/constraints and default mod versions stay unchanged. Real per-game Config Tool exports still gate adoption; keep that limitation and native handoff explicit. Do not add games/audio/migration or modify Worker 12's code.

Run full pytest, Ruff, compilation, framework check/status, applicable upgrade checks and existing shortcut/line-ending equality checks. Record actual outputs/exits at literal commits; update the current four-section summary and evidence, push PR #21 and return new delivery SHA plus green Linux/Windows CI. Then a separate Verifier reviews that SHA and source/archive/export boundary. Never accept, merge, tag or publish.
```
