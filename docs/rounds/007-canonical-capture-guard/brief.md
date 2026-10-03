# 007-canonical-capture-guard: Reject unsupported canonical key declarations

Tier: 2
Mode: implementation
Supersedes: 006-schema-capture-safety — conditional canonical string declarations can still produce successful incomplete capture.

## Goal

Close the remaining canonical-header parsing gap so unsupported declarations
cannot produce authoritative-looking partial schema JSON. Preserve the correct
reviewed-source captures and the bounded static extraction contract established
in round 006. This is a focused correction, not a new mod upgrade.

## Context

Read AGENTS.md, the framework/Worker card, round 006's brief and both reports,
tools/capture_settings_schema.py, tests/test_schema_capture.py, the immutable
source-check attachment and docs/UPGRADING.md's Static capture boundary.

Brain reviewed complete round 006 commit
f1303e413e5e15d6e9e91efdb62c8a009ec06377, whose implementation is Worker delivery
0e083b27f83216762b0ed025a5293116782a1258. Only the Verifier report differs from
that Worker delivery. Brain independently reproduced the Verifier blocker:
constant_values searches for selected declaration spellings without validating
surrounding header syntax or conditional branches. A valid conditional declaration
using constexpr char const* in one branch and constexpr const char* in the other
silently discards the first key spelling and exits 0 with the second.

The prior report contains the full reproduction. Its synthetic Demo_Setting is
"Replacement Key" in the NEW_FORMAT branch and "Enable First Person Shooter Mode"
in the other branch. Current CLI output is exit 0, empty stderr and JSON with
only the latter spelling. Unsupported header syntax must instead stop capture
with an actionable source-format error and empty stdout. A general C++ parser
or arbitrary preprocessor evaluation is not required.

Brain also independently checked immutable 4.1.0/4.1.1/4.1.2 captures: exact
fields, captured constraints and original byte hashes agree with reviewed source
and fixtures, with 128/128/131 keys. All 69 protected prior seat files are
unchanged. The complete delivery's local suite reported "235 passed in 7.11s";
Ruff, compilation and framework checks passed, all exit 0. Worker exact-commit
CI run 37150498729 is green; Brain checked its checkout logs and platform results.
Those successful checks do not resolve the reproduced unsupported-header failure.

The three immutable source commits and hashes remain recorded in round 004's
schema-delta.json and round 006's source-checks.json. Treat source identity and
exact fields as evidence; counts alone are insufficient.

## Start readiness

Start now from this pushed brief. It carries the complete rejected delivery,
its implementation and both reports. No prior merge is required to correct this
reviewed code. Round 004's accepted audit remains unchanged and pending its own
owner merge decision. Preserve round 005's stop record and round 006's reports.
Use fresh round 007 seats. Do not resume round 006 or rewrite earlier reports.
Verifier starts only after the Worker's completed implementation report is pushed.
A stop report is not completed implementation.

## Scope and non-goals

Change the canonical constant/header capture boundary, focused offline regression
tests, related capture documentation and this round's source-check evidence if
necessary. Reuse the already correct flag/initializer behavior unless a tightly
related defect requires a justified correction. Do not reduce the fail-on-unknown
acceptance requirement or merely narrow the wording to excuse silent omissions.

No installer, settings template/schema/constraints, baseline 4.1.0 fixture,
shortcut/pin/hash, mod version, release/CI policy or framework changes. Do not
install mods, execute upstream binaries, obtain Nexus audio, merge, tag, publish,
change settings or remove old branches/checkouts. Open a new corrective PR and
reference draft PR #9; Brain decides what happens to the prior candidate.

## Invariants

- All AGENTS.md invariants and role boundaries apply; Python 3.9 stays supported.
- Original-source hashes must describe untouched source bytes.
- A successful capture must satisfy the reviewed syntax boundary; unexpected
  canonical declarations or preprocessor context must not be ignored.
- Baseline literal concatenation/string aliases and reviewed namespace/header
  wrappers must keep working. Known conditional flag-union behavior remains
  distinct from unreviewed canonical-string conditions.
- Static capture remains separate from actual per-game exports and release
  applicability. Existing dynamic-choice/float/default limitations stay explicit.

## Acceptance criteria

1. The exact prior conditional canonical-string reproduction raises an actionable
   source-format error through the API; CLI exits nonzero with empty stdout.
2. Define and enforce the bounded canonical-header syntax. Unknown declaration
   spellings and unreviewed conditional/namespace contexts cannot hide referenced
   section/key/choice constants while returning partial success. Support of those
   new forms is unnecessary; deterministic rejection is acceptable. Preserve
   benign reviewed directives/wrappers and string/comment handling.
3. Add meaningful offline regressions that fail against round 006's tool and pass
   after correction. Cover both branch orders, alternate section/key declarations,
   relevant canonical aliases/choices, unsupported header context, and the
   documented success forms. Exercise API and CLI error behavior, not just counts.
4. All prior focused regressions and the full suite pass. Independent immutable
   checks preserve whole 4.1.0 fixture equality, 4.1.1 fields/constraints, exact
   4.1.2 131-key map/delta/union evidence and original-source hashes.
5. Protected files and earlier records are unchanged. Final Linux/Windows CI is
   green; reports accurately state the supported boundary and runtime limitations.
6. Verifier makes a blind first pass, independently reproduces the original defect,
   probes related unsupported header cases, and compares exact upstream captures
   before reading worker.md.

## Required evidence

Record actual commands, output and exit codes at literal commits for:

- Baseline identity, real diff and protected-file comparisons.
- Before/after original and related header reproductions, including API failure,
  CLI exit/stdout/stderr, and regression failures against the prior tool.
- Focused tests and immutable-source capture comparisons described above.
- python3 tools/fw.py check and python3 tools/fw.py status
- python3 -m pytest tests/ -q
- python3 -m ruff check .
- python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py
- Final CI URL, actual checkout SHA from logs and all platform results. Distinguish
  literal branch runs from generated PR merge checkouts.
- The round's report --push command and delivery freshness.
