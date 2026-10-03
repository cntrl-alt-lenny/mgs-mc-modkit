# 003-product-integration: Integrate the reviewed installer with the adopted workflow

Tier: 2
Mode: implementation
Supersedes: none

## Goal

Produce one reviewed installer delivery that includes the accepted recovery,
settings and cancellation improvements alongside the adopted framework, with
committed reports and accurate release limitations.

## Context

Round 002 established the workflow. Brain independently checked the complete
delivery at 8d3c94a361fb7c3d40667f1779d3c51a6153ffc3: 152 offline tests passed,
all six copied files matched the pinned source and manifest hashes, lint and
compilation passed, and all four CI jobs were green on the complete-round PR.
Adoption merge still requires owner approval. PR #4 holds both seat reports;
PR #3 is the earlier Worker-only candidate.

The separate product change in PR #2 was reviewed at
7630a81a04abf4e7f96dd75663bae70ba31c4f2e. It adds durable recovery, configuration
preservation, responsive installation and release gates. Brain independently
reproduced the original Zenity cancellation and post-reset selection bugs, then
verified both fixes and the additional recovery probes. That review did not
establish real game boots, native GUI interaction or Nexus audio compatibility.
Its earlier informal exchange is historical evidence, not a stamped framework
round. This round creates a formal delivery for integrating that accepted delta.

Read AGENTS.md, docs/state.md, both prior adoption reports, the actual product
diff against e6aed3da73c3d02ed7f2795d2c6567ceabae55a9, and the product's upgrade,
settings, audio, troubleshooting and release documentation.

## Scope and non-goals

Bring the exact reviewed product delta into the adopted project and verify the
combined tree. Preserve its reviewed file contents unless an integration problem
requires a focused correction, which must be explained and independently reviewed.
Keep the framework copies and owner-approves rule unchanged. Open a new PR for
this formal delivery and link the earlier product candidate; do not close or
modify the earlier PRs yourself.

Do not upgrade upstream mods, invent new features, redesign the installer,
publish v2.3.0, tag a release, merge into main, change repository settings or
claim hardware checks have run. This is integration and evidence collection,
not authorization for a release. Do not obtain or redistribute Nexus audio.

## Prerequisite

The owner must approve round 002's merge and Brain must confirm that adoption
has merged before the Worker starts this round. These prompts are queued until
that confirmation. If sent early, explain that prerequisite and wait; do not
bootstrap another adoption, perform integration or claim delivery.

Once allowed to start, use the installed framework commands and isolated seats.
Preserve the other linked checkouts and the original product branch. The Verifier
starts only after the Worker's stamped delivery is pushed.

## Invariants

- All project invariants and role boundaries in AGENTS.md apply.
- Adoption files and pinned framework fingerprints remain unchanged.
- Mod versions, download hashes and supported-game scope match the reviewed
  product source; upstream update tracking remains advisory.
- Both launchers pin the same kit version and the exact installer SHA-256;
  preserve Windows CRLF bytes.
- Previous setups, originals and recovery records survive failed repairs and
  cancellations; failures and partial outcomes are reported accurately.
- Explicit choices after Reset agree with the review screen, written settings,
  launcher data and persisted preferences.
- Native CI and synthetic tests do not prove real game/audio compatibility.

## Acceptance criteria

1. The combined tree includes the reviewed product delta, framework adoption and
   this round's complete, current reports. Account for every integration change.
2. The full offline suite includes the framework hygiene test and the seven
   cancellation/reset regression cases; the combined suite should collect 203
   tests unless a justified change alters that count.
3. Independent source comparisons show preserved mod pins, configuration schema,
   shortcut metadata and framework fingerprints.
4. Linux Python 3.9/3.11/3.12 and Windows Python 3.12 CI pass on the final delivery,
   including lint, compilation and desktop validation where applicable.
5. The PR and reports accurately distinguish automated checks from the remaining
   real Windows/Deck boot, GUI, audio and restoration checks in docs/RELEASING.md.
6. No merge, release, tag, upstream pin bump or repository-setting change occurs.

## Required evidence

Record actual commands, output and exit codes at literal commits for:

- The baseline, reviewed source and combined diff, including an accounting of
  files that differ from the reviewed product source.
- python3 tools/fw.py check and python3 tools/fw.py status
- python3 -m pytest tests/ -q
- python3 -m ruff check .
- python3 -m py_compile tools/fw.py install.py
- Both launcher tag/SHA checks and Windows CRLF verification.
- All framework-owned file/source and manifest fingerprint comparisons.
- Final CI run URL, tested commit and platform results.
- The round's report --push command and delivery freshness.

Verifier makes a blind first pass before reading worker.md, independently checks
the combined delivery and source comparisons, and distinguishes unverified claims
from proven failures. Brain will review both reports and re-derive the result.
