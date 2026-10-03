# 006-schema-capture-safety: Prevent incomplete settings capture

Tier: 2
Mode: implementation
Supersedes: 005-schema-capture-safety — its unnecessary prior-merge prerequisite stopped the Worker before implementation.

## Goal

Make the settings capture tool produce a complete, explicitly bounded static
schema for the reviewed declaration formats, or stop with an actionable error.
Unsupported declaration/flag syntax must not silently produce a successful
partial schema. This prepares reliable evidence for a future upgrade without
changing the installed mod set or game settings.

## Context

Round 004 audited the official upstream set and recommended retaining all current
pins. Read its brief, reports and schema evidence, tools/capture_settings_schema.py,
the baseline capture fixture, relevant tests and docs/UPGRADING.md.

Brain accepted round 004 at literal commit
371489943c5986c3ffe8f8c4ea9f4447f5fc4146. An independent official API check
reproduced four stable tags/source identities/README hashes, ten release-body
hashes and six official asset URLs/digests. All 58 baseline files were unchanged.
Local pytest reported "203 passed in 7.60s" (exit 0); Ruff, framework check and
compilation passed (exit 0). Direct CI run 37148244111 checked that literal
commit in every job: Linux Python 3.9/3.11/3.12 each passed 203 tests; Windows
3.12 passed 201 with two symlink privilege skips; Linux lint, compilation and
desktop validation passed. Complete-round PR #8 awaits owner approval.

Brain independently fetched immutable HD source files and reproduced the exact
union declaration comparison: 128 keys at 4.1.0 versus 131 at 4.1.2, with four
additions and one removal matching the round 004 attachment. Running the
unchanged capture function on 4.1.2 succeeded with 128 keys but omitted these
existing First Person Shooter Mode keys:

- Enable First Person Shooter Mode
- First Person Shooter - Movement Enabled By Default
- Toggle First Person Shooter Movement

Their declarations use kFirstPersonViewGameFlags. The source defines MGS2 in the
normal build and MGS2 | MGS3 when MGS3_FPS_DEV is defined. Static union membership
does not establish release-binary or per-game export applicability.

Reviewed source identities:
4.1.0 f4f662d67a2a033dee0877e436a0fe65eb719e0b;
4.1.1 0120a6b1116913733f4dc21c287813d4cb2bb659;
4.1.2 33e80bf4d2223f6866b0b92e06c3c9b85efab652.
Their exact file paths/hashes are recorded in round 004's schema-delta.json.
Use immutable source for independent checks; do not treat a mutable tag or the
count alone as sufficient evidence.

## Start readiness and correction

This round is ready to start now. It carries the accepted audit at literal
371489943c5986c3ffe8f8c4ea9f4447f5fc4146 and the prior brief/stop report in its
history. Round 004 changes only audit records; all 58 baseline files are
byte-identical to main f28f9eaea634b71f5bb788794635304e0987a764. Brain independently
rechecked that identity in the stopped seat. A pending audit merge therefore
does not block this implementation on the reviewed baseline.

The prior Worker stopped correctly at 3e9f8aaed5ecad1154fd25b4d828a5e04069aa10:
PR #8 was open and the prior brief explicitly required its merge before work.
Only the stop report was added. This corrected round replaces that dispatch
condition; its implementation scope and acceptance criteria are unchanged.
Preserve the old brief, stop report, branch and checkout. Do not resume or
rewrite round 005. Use fresh round 006 seats and the normal start/report commands.

No owner-reserved merge or release decision is waived. PR #8 remains open pending
owner approval, and any subsequent implementation merge also requires approval.
Verifier starts only after round 006's stamped implementation delivery is pushed;
a stop report does not establish completed implementation. If implementation
has not occurred, report that fact rather than treating freshness as completion.

## Scope and non-goals

Change tools/capture_settings_schema.py, focused offline tests/fixtures, the
capture-tool explanation in docs/UPGRADING.md if needed, and this round's records.
Keep fixtures compact and deterministic. Do not depend on live network access
for the offline suite; record separate immutable-source checks in the reports.

No changes to install.py, settings template/schema/constraints, the existing
4.1.0 capture fixture, shortcut pins/hashes, mod versions, release files,
framework copies or project roles. Do not migrate user settings, install mods,
run upstream binaries, obtain Nexus audio, merge, tag, publish or alter repository
settings. Actual per-game Config Tool exports and game boots stay prerequisites
for a future coordinated upgrade.

## Invariants

- Project invariants and role boundaries in AGENTS.md apply.
- Retain Python 3.9 and existing baseline capture/CLI use.
- Source identity/hash evidence must refer to original source bytes, rather than
  bytes rewritten to normalize an alias.
- Canonical fields must not be guessed from counts or key substrings.
- Supported static union extraction must say what conditional/build applicability
  it covers. It must not claim to represent a particular executable's export.
- Existing limitations for dynamic choices, float bounds/defaults and actual
  per-game exports must remain explicit. This task does not broaden those claims.

## Acceptance criteria

1. Capturing immutable 4.1.0 and 4.1.1 sources retains the existing baseline
   fields/constraints and expected source identities. The 4.1.0 capture remains
   exactly equal to the unchanged committed fixture.
2. For the reviewed 4.1.2 source, capture includes all 131 reviewed union keys,
   including the three alias-backed fields. Independent comparison checks exact
   names/types and the four additions/one removal, rather than just counts.
   Conditional applicability is represented or clearly documented as a bounded
   union; no MGS3 release FPS support is implied.
3. Unknown or unsupported flag/declaration syntax cannot silently remove eligible
   fields or return success with misleading partial output. Errors identify the
   offending construct and request source-format review. Known non-MGS2/MGS3
   fields are still intentionally excluded. Define the supported syntax boundary
   clearly; a general C++ parser or arbitrary preprocessor is not required.
4. Meaningful offline regression tests expose the current silent omission and
   misleading-success case, then pass after the change. Cover normal baseline,
   reviewed alias/conditional forms, unrelated game flags, malformed/unknown
   declarations and accurate original-source hash reporting.
5. Complete offline checks and final Linux/Windows CI pass. No protected product
   or framework files change. Reports distinguish static capture from actual
   generated settings and runtime compatibility.
6. Verifier makes a blind first pass, independently compares exact field sets
   against the immutable source, checks unsupported-input behavior and reviews
   every production/test change before reading worker.md.

## Required evidence

Record actual commands, output and exit codes at literal commits for:

- Baseline identity, final diff and preserved-file comparisons.
- A before/after reproduction of the alias omission and unsupported-input failure
  behavior, plus the focused regression tests.
- Capture CLI output against the three immutable sources, exact field/constraint
  comparisons, baseline fixture equality and original source hashes.
- python3 tools/fw.py check and python3 tools/fw.py status
- python3 -m pytest tests/ -q
- python3 -m ruff check .
- python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py
- Final CI URL and actual checkout identity from logs, with platform results;
  distinguish generated PR merges from literal branch runs.
- The round's report --push command and delivery freshness.
