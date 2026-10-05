# 008-canonical-namespace-boundary: Reject ambiguous canonical namespace context

Tier: 2
Mode: implementation
Supersedes: 007-canonical-capture-guard — a nested namesake namespace can override the real canonical namespace during capture.

## Goal

A successful static capture must resolve the reviewed canonical namespace, or
reject unsupported header context with an actionable error and no JSON. Close
the demonstrated namespace-context gap while retaining the correct immutable
source captures and the original conditional-declaration rejection.

## Context

Read AGENTS.md, the framework and your role card, round 007's brief,
tools/capture_settings_schema.py, tests/test_schema_capture.py and the Static
capture boundary in docs/UPGRADING.md. Worker may read round 007's report.
Verifier must finish the independent first pass before reading this round's
Worker report. Preserve all earlier briefs, reports and evidence.

Brain reviewed Worker implementation 0166a057fa869546f0cc28ef715a9961d771fb6a,
delivered in 80709a01f28e0c716ab5e05ebaf5394b25d9c56a. Only worker.md differs
between those two commits. Local focused tests reported 42 passed in 0.22s,
and the full suite 245 passed in 4.99s, both exit 0. The original conditional
reproducer now exits 1 with zero stdout bytes and an actionable error. Those
checks do not resolve the independently reproduced namespace failure below.

constant_values searches the whole header for the spelling namespace ConfigKeys,
without proving that occurrence's enclosing scope or examining other header
declarations. A syntactically valid header can contain the old constants in
Decoy::ConfigKeys, different constants in Actual, and the global alias
namespace ConfigKeys = Actual. Config Tool references resolve to Actual, but
capture reads the nested decoy and returns successful incorrect schema JSON.

The committed reproduction builds that header from the existing test fixture.
Actual::Demo_Setting is Replacement Key; Decoy::ConfigKeys::Demo_Setting is
Enable First Person Shooter Mode. At the reviewed implementation, API output
contains the latter, CLI exits 0 with 1067 stdout bytes and empty stderr.
Compiling the generated header and a small independent C++11 probe succeeds
with empty stderr; executing that synthetic probe prints Replacement Key
and exits 0. No upstream binary, installer or game was executed.

## Start readiness

Start from this pushed brief, which carries the complete round 007 delivery.
No prior merge is required. Use fresh round 008 seats; do not restart round 007.
Round 004's accepted audit remains pending its separate owner merge decision.
Earlier report-staleness warnings on descendant branches do not authorize
rewriting old reports. Verifier starts only after a completed Worker report is
pushed. A stop report is not completed implementation.

## Scope and non-goals

Change the canonical-header context boundary, focused offline regressions,
related static-capture documentation and this round's supporting evidence.
Supporting general C++ namespaces, namespace aliases or preprocessing is not
required: deterministic rejection of unreviewed forms is acceptable.

Do not alter installer, settings schema/template/constraints, baseline fixture,
mod pins, shortcuts, release/CI policy, framework copies or earlier seat files.
Do not install mods, run upstream binaries, acquire Nexus audio, merge, tag,
publish, change repository settings or remove existing branches/checkouts.
Open a new corrective draft PR referencing PR #10; Brain decides the disposition
of prior candidates. Do not close or edit those prior candidates.

## Invariants

- All AGENTS.md invariants and role boundaries apply; retain Python 3.9 support.
- Unknown canonical declarations and enclosing namespace/preprocessor contexts
  must not produce authoritative-looking output from a namesake or decoy scope.
- Preserve reviewed literal concatenation, string aliases, comments/strings,
  benign directives and wrappers, plus known conditional game-flag union behavior.
- Preserve untouched source-byte hashes and exact fields/constraints.
- Static capture is not a Config Tool export or proof of runtime applicability.

## Acceptance criteria

1. The committed decoy/alias reproduction raises an actionable API source-format
   error. CLI exits nonzero with empty stdout. It must not capture the decoy.
2. Establish and enforce the complete reviewed header context. Unsupported
   enclosing/nested namespaces, namespace aliases, alternative namespace
   declarations and other declarations outside the selected body cannot evade
   validation and redirect canonical references while capture succeeds. A bounded
   parser may reject these forms; document the actual enforced success boundary.
3. Meaningful offline regressions fail against round 007's tool and pass after
   correction. Cover the exact decoy/alias case, relevant namespace variations,
   API and CLI failure semantics, and benign supported header success cases.
4. The original conditional-key reproductions in both branch orders and all prior
   focused regressions still pass. Independently compare immutable 4.1.0/4.1.1/
   4.1.2 captures: whole baseline fixture equality, exact fields and constraints,
   exact 131-key 4.1.2 delta/union evidence and original hashes are preserved.
5. Protected files and all prior seat records remain byte-identical. Required
   local checks and final Linux/Windows CI are green at stated exact commits.
6. Verifier independently reproduces before/after failures, probes related
   namespace contexts, checks regression sensitivity and exact upstream captures
   during a blind first pass, then compares the Worker report.

## Required evidence

Record actual commands, outputs and exit codes at literal commits for:

- Baseline identity, real diff and protected-file comparisons.
- python3 docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py
  --compile-cpp (C++ compilation is optional where no compiler is available;
  report that limitation, but API/CLI checks are required).
- Before/after namespace reproductions, API errors, CLI exit/stdout/stderr and
  regression failures against the prior tool.
- Focused tests and immutable comparisons using the preserved round 006
  check_sources.py attachment; write any new output only under this round.
- python3 tools/fw.py check and python3 tools/fw.py status
- python3 -m pytest tests/ -q
- python3 -m ruff check .
- python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py
- Final CI URL, literal checkout SHA from logs and all platform outcomes;
  distinguish direct branch runs from generated PR merge checkouts.
- The round's report --push command and delivery freshness.
