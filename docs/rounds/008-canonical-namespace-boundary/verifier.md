<!-- fw-report
round: 008-canonical-namespace-boundary
role: verifier
branch: verifier/008-canonical-namespace-boundary
head: 228ff15b48d0dc269687ca71a7fec94a24cb9934
os: macOS 27.0.1
python: 3.9.6
written: 2026-10-05T09:28:40Z
-->
Reviewed commit: `228ff15b48d0dc269687ca71a7fec94a24cb9934`.
Prior round 007 delivery: `80709a01f28e0c716ab5e05ebaf5394b25d9c56a`.
Round 008 starting brief: `2c7a0372cb251b78b0c7ea75ad5581d04edf270d`.
Final implementation: `7ee96a824adf51cc9d65a58a46619dc6bd2bd158`.

## Findings

None blocking, requiring correction, or contradicting the Worker report.
The independent first pass below was completed before opening this round's
Worker report. This is review evidence for Brain, not merge approval.

### Independent first pass

Seat command `python3 tools/fw.py start --role verifier --round 008-canonical-namespace-boundary`
returned exit 0 and selected exactly the reviewed Worker delivery above.
Environment: `python3 --version` returned `Python 3.9.6`, exit 0;
`uname -s` returned `Darwin`, exit 0. Read the project instructions,
framework, Verifier card, both briefs, real parser/test/documentation diffs,
and preserved immutable-source checker. Did not read worker.md during this pass.

Commands and real results at the reviewed commit:

- `git rev-parse HEAD origin/main`, exit 0: reviewed SHA above and default
  branch `f28f9eaea634b71f5bb788794635304e0987a764`.
- `git diff origin/main HEAD --stat` and the scoped real diff, exit 0:
  cumulative history includes pending rounds 004 through 008. Reviewed the
  round-specific diff against the round 007 delivery separately; did not
  mistake all inherited work for round 008 changes.
- `git diff --stat 2c7a0372cb251b78b0c7ea75ad5581d04edf270d HEAD`, exit 0:
  `14 files changed, 1202 insertions(+), 25 deletions(-)`; scoped parser,
  tests, documentation, new tail fixture, and this round's evidence/report.
- `git diff --check 2c7a0372cb251b78b0c7ea75ad5581d04edf270d`, exit 0,
  no stdout/stderr.
- Independent `python3 -` byte comparison of every existing tracked file
  other than the three authorized parser/test/documentation edits, using
  `git ls-tree -r --name-only` and `git show <baseline>:<file>` against disk:
  `All 76 prior tracked files outside three allowed edits byte-identical`
  against round 007 delivery, exit 0. Consequently installer, settings,
  baseline fixture, pins, shortcuts, framework, CI, state, and earlier seat
  records are untouched. After the blind pass the same comparison against
  the round 008 starting brief, excluding its permitted attachments, returned
  `Protected against round 008 starting brief: 77 byte-identical files`, exit 0.
- `python3 -m pytest tests/test_schema_capture.py -q`, exit 0:
  `70 passed in 1.31s`.
- `python3 -m pytest tests/ -q`, exit 0:
  `273 passed in 6.13s`.
- `python3 -m ruff check .`, exit 0: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py`,
  exit 0, no stdout/stderr.
- Independent Python 3.9 AST parsing of changed tool/tests, exit 0:
  `Python 3.9 grammar: 2 changed Python files accepted`.
- `python3 tools/fw.py check`, exit 0: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status`, exit 0: `all project checks pass`, unchanged
  framework pin 3.1.0, current Worker report, Verifier started with no report
  yet. It also printed inherited round 004 stale-report warnings; they do
  not authorize editing those records and are not a round 008 defect.

### Before/after and independent namespace probes

`python3 docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py --compile-cpp`
returned diagnostic exit 0 at the reviewed commit:

```text
API rejected: Unsupported source construct: header context before ConfigKeys namespace: namespace Decoy {; review the upstream source format
CLI exit: 1 stdout bytes: 0 stderr: 'capture failed: Unsupported source construct: header context before ConfigKeys namespace: namespace Decoy {; review the upstream source format\n'
Compile exit: 0 stderr: ''
Native C++ resolution exit: 0 stdout: 'Replacement Key\n'
```

Independently constructed a disposable temporary checkout by obtaining the
round 007 parser with `git show 80709a01f28e0c716ab5e05ebaf5394b25d9c56a:tools/capture_settings_schema.py`,
and copied the current focused tests, new fixture and reproduction into it.
The main checkout and seat files were not changed. Running that reproduction
with `--source-root <temporary-checkout> --compile-cpp` returned diagnostic
exit 0, but API captured `Enable First Person Shooter Mode`; CLI exit 0,
1067 stdout bytes, empty stderr. C++ compilation exit 0, empty stderr;
execution exit 0, stdout `Replacement Key\n`. This establishes the actual
C++ namespace resolution independently of the parser and the report.
Only generated synthetic C++ was executed.

The current focused tests against that prior parser returned exit 1:
`16 failed, 54 passed in 0.54s`. Failures include the exact decoy/alias case,
enclosing scopes, inline namespace, outside declarations/macros/includes,
tail alterations, and namespace spelling in a quoted literal. Thus new
regressions expose prior behavior, rather than merely mirror the correction.
Four namespace cases already rejected by the prior parser still reject;
all original 42 cases and supported-header cases remain intact.

An independent `python3 -` fixture-driven probe also checked these eight
additional contexts. Each raised CaptureError through the API; each CLI
returned 1, zero stdout bytes, and `review the upstream source format`:

- `extern "C++" {` surrounding the canonical body.
- Trailing `namespace ConfigKeysAlias = ConfigKeys;`.
- Leading `using namespace Decoy;`.
- Leading `#define namespace X`.
- Trailing `namespace {}`.
- Alternative `namespace ::ConfigKeys {` spelling.
- Nested `namespace X [[deprecated]] {}` inside ConfigKeys.
- Completed `#if 1` wrapper around a preceding include.

No unexpected success was observed. The full focused suite additionally
covers both original conditional-key branch orders, conditional section and
choice values, unknown nested declarations, literals/aliases, comments and
strings, original source hashes, and known game-flag union behavior.

Code review at `tools/capture_settings_schema.py:119` confirms a unique
unquoted canonical namespace; lines 127-140 anchor all preceding context to
only reviewed wrappers. Lines 154-163 reject any nonempty trailing token
sequence except the reviewed fingerprint. The complete canonical body is
still validated. `docs/UPGRADING.md:85` accurately documents this conservative
allowlist and its requirement for source-format review of future tail changes.

### Immutable primary-source checks

`python3 docs/rounds/006-schema-capture-safety/attachments/check_sources.py /tmp/mgs-verifier-008-sources /tmp/mgs-verifier-008-source-checks.json`
returned exit 0 after fetching six immutable source files directly from
upstream GitHub. Actual output:

```text
4.1.0: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.1: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.2: CLI exit 0; 131 exact expected keys; constraints and ORIGINAL hashes match
4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed
```

Immutable upstream identities:

- 4.1.0: `f4f662d67a2a033dee0877e436a0fe65eb719e0b`.
- 4.1.1: `0120a6b1116913733f4dc21c287813d4cb2bb659`.
- 4.1.2: `33e80bf4d2223f6866b0b92e06c3c9b85efab652`.

For 4.1.0/4.1.1 the original tab source SHA-256 is
`4b7cec4708ae0fa4af6de06ec0244426ba67a826376f6a6d6e37b2aa1a2690c8`,
and header SHA-256 is
`2c06734d5c9ad2abcf7756dc09aa7cc72cce0cb6bc037d7594fbabd9edc40882`.
For 4.1.2 they are respectively
`4b2575f6075fb7a8534c73a0adc048a7b0515082e89da762ed79bfe441f65e2e`
and `8e03aa5d90662fcadd0ef729d5dfe36d6045545c1772be2cee6be12f28aa9c94`.
The checker compared exact fields and constraints, not only counts; whole
4.1.0 fixture equality was asserted. 4.1.2 adds Bool keys `Fix Dropped Item Toss`,
`Fix Emissive Textures`, `Fix Lighting Bounding Boxes`, and
`Blend Particle Effect Sprites`, removes Bool `Show Soft Particles`, and
preserves `kFirstPersonViewGameFlags: [MGS2, MGS3]`.

Independent tail extraction anchored to the first controller declaration in
each downloaded header, followed by comment/string-aware tokenization,
returned exit 0: each contains 512 tokens with SHA-256
`8ade693eb22bd65377db0fed88492cb132ce0213af49d05d3b49fc00546e39fd`.
Comparison with the new offline fixture also returned exit 0:
`New tail fixture: identical 512-token sequence to all three immutable headers`.
The reviewed tail contains no namespace redirection or macros.

### Final exact-commit CI and second pass

During the blind pass:
`gh run list --commit 228ff15b48d0dc269687ca71a7fec94a24cb9934 --json databaseId,headSha,status,conclusion,url,name`
returned exit 0 and completed successful runs. Independently inspected
`gh run view 37285406055 --json headSha,event,conclusion,jobs,url` and
`gh run view 37285406055 --log`, both exit 0.
CI URL: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37285406055`.
This is a direct branch workflow_dispatch run. All four checkout logs show
literal `228ff15b48d0dc269687ca71a7fec94a24cb9934`, rather than a generated
PR merge commit. Every platform job succeeded:

- Linux Python 3.9: `273 passed in 8.29s`.
- Linux Python 3.11: `273 passed in 4.80s`.
- Linux Python 3.12: `273 passed in 6.07s`.
- Windows Python 3.12: `271 passed, 2 skipped in 19.97s`.

Linux lint, compilation and desktop validation steps succeeded. Existing
Windows privileged symlink skips are not claimed as executed tests.

Only after this independent first pass did I read worker.md. Its load-bearing
claims agree with my reproduction, sensitivity, exact-source comparisons,
protected-file comparisons and full-suite results. No unproven claim affecting
this round's acceptance was found. Worker CI at final code commit and its
separately labelled generated PR merge checkout are supplemented here by
independently observed CI at the complete literal delivery commit.

`git diff --exit-code 7ee96a824adf51cc9d65a58a46619dc6bd2bd158 HEAD -- tools tests docs/UPGRADING.md`
returned exit 0, no output, confirming that intervening evidence/report commits
do not change the tested code. `gh pr list --head worker/008-canonical-namespace-boundary --json number,url,isDraft,baseRefName,headRefName,body`
returned exit 0: corrective PR `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/11`
is draft, targets main, and references prior candidate #10.
`python3 tools/fw.py delivery --round 008-canonical-namespace-boundary`
returned exit 0 with `delivered` and the fresh Worker report describing
`ab8e8d392a2f`. No old records were repaired.

### Acceptance criteria

1. Met: demonstrated decoy/alias rejects through API and CLI with no JSON.
2. Met: complete reviewed header context enforced by the bounded allowlist.
3. Met: 16 prior-tool failures versus 70 passing focused cases; API/CLI and
   supported-header success evidence included.
4. Met: both conditional-key orders remain rejected; immutable exact fields,
   constraints, whole baseline, four-addition/one-removal delta, union and hashes
   remain unchanged.
5. Met: protected files/records byte-identical; required local checks and all
   Linux/Windows jobs green at the exact reviewed delivery.
6. Met: blind first pass included independent before/after reproduction,
   additional namespace contexts, sensitivity and upstream capture checks;
   Worker comparison followed afterwards.

## Not verified

No real Config Tool exports, upstream binaries, installer execution, game
boots, GUI rendering, audio compatibility, licensed hardware, repair/removal,
or release-build MGS3 FPS applicability were checked. The synthetic C++ probe
establishes only the reproduction's namespace resolution. The tail fixture is
lexical evidence, not a standalone compilable upstream translation unit.
Static flag union does not establish runtime macro selection or per-game exports.

Future unreviewed upstream formats are deliberately rejected; exhaustive
support for general C++, preprocessing and namespaces is outside the brief.
Local checks ran on macOS; native Linux/Windows evidence is from exact-commit
CI logs, with the two existing Windows skips stated above. No production code,
prior reports, framework files, settings, pins or release artifacts were edited.
No merge, tag, publication, repository setting or owner approval action occurred.

## Verdict

The reviewed exact delivery satisfies round 008's bounded namespace-context
correction. Independent reproduction proves the prior wrong-key success now
fails closed, meaningful tests expose the old bug, and immutable reviewed
captures remain exact. I found no blocker or correction to request, with high
confidence within the documented static boundary. Brain must independently
judge this commit and the owner retains the merge decision. This Verifier
writes only this report and publishes it with
`python3 tools/fw.py report --role verifier --round 008-canonical-namespace-boundary --push`;
publication success and freshness are established by that command and the
subsequent delivery check, not inferred from the verdict.
