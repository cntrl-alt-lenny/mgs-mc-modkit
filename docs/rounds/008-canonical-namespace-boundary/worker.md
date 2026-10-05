<!-- fw-report
round: 008-canonical-namespace-boundary
role: worker
branch: worker/008-canonical-namespace-boundary
head: ab8e8d392a2f62b08e84f1c9984f0228e812ebea
os: macOS 27.0.1
python: 3.9.6
written: 2026-10-05T08:43:05Z
-->
## Verified

Final code/test/documentation commit: `7ee96a824adf51cc9d65a58a46619dc6bd2bd158`.
Evidence-only commit before this report: `ab8e8d392a2f62b08e84f1c9984f0228e812ebea`.
`git diff --exit-code 7ee96a824adf51cc9d65a58a46619dc6bd2bd158 HEAD -- tools tests docs/UPGRADING.md`
at that evidence commit produced no output, exit 0. All checks below use the
final code unless explicitly labelled prior. Full outputs, commands and exit
codes are in `attachments/final-local-checks.json`, `final-source-checks.json`,
`tail-checks.json` and `ci-checks.json`.

- Seat start: `python3 tools/fw.py start --role worker --round 008-canonical-namespace-boundary`
  at the fresh detached main worktree → exit 0:
  `seat ok: worker, round 008-canonical-namespace-boundary, branch worker/008-canonical-namespace-boundary at 2c7a0372cb25`.
  Baseline is `2c7a0372cb251b78b0c7ea75ad5581d04edf270d`.
  `git diff --exit-code 80709a01f28e0c716ab5e05ebaf5394b25d9c56a 2c7a0372cb251b78b0c7ea75ad5581d04edf270d -- tools/capture_settings_schema.py`
  → exit 0, empty output: prior tool is the round 007 delivered implementation.
- Before/after and regression sensitivity:
  `python3 docs/rounds/008-canonical-namespace-boundary/attachments/check_delivery.py <output-json>`
  at the final code commit → exit 0. It creates a temporary prior-tool checkout
  from the baseline and runs the same new tests there, without modifying this
  checkout. Prior focused suite → exit 1, `16 failed, 54 passed in 0.46s`.
  The decoy case and related outer contexts fail their rejection assertions;
  the prior tool also incorrectly treats namespace spelling inside a string
  as a declaration. Current focused suite → exit 0, `70 passed in 0.92s`.
- `python3 docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py --compile-cpp`
  → diagnostic command exit 0. Prior-tool run: API captures the old decoy key,
  CLI exit 0, stdout 1067 bytes, stderr empty. Corrected run:
  `API rejected: Unsupported source construct: header context before ConfigKeys namespace: namespace Decoy {; review the upstream source format`;
  `CLI exit: 1 stdout bytes: 0`, stderr contains the same actionable source-format
  error. Both generated C++11 probes: `Compile exit: 0 stderr: ''` and
  `Native C++ resolution exit: 0 stdout: 'Replacement Key\n'`.
  Only a generated synthetic probe was executed.
- Namespace regressions exercise API rejection and CLI exit 1/empty stdout for
  the exact decoy/alias header, named/anonymous/inline enclosing namespaces,
  qualified/inline/attributed canonical declarations, duplicate namespaces,
  aliases and other declarations before/after the body, macros, unreviewed
  includes/conditionals, and additions inside/after the reviewed tail. Supported
  preambles/tails, literal concatenation, string aliases, comments, strings and
  original byte hashes succeed. The original conditional canonical-string tests
  in both branch orders and the known game-flag union regressions still pass.
- `python3 docs/rounds/006-schema-capture-safety/attachments/check_sources.py <scratch> <output-json>`
  at final code → exit 0, real output:
  ```text
  4.1.0: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
  4.1.1: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
  4.1.2: CLI exit 0; 131 exact expected keys; constraints and ORIGINAL hashes match
  4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed
  ```
  Downloaded untouched source bytes at the three preserved immutable commits;
  their original hashes, exact fields and constraints match the prior evidence.
  Whole 4.1.0 JSON equals the protected fixture. Exact 4.1.2 union remains
  `kFirstPersonViewGameFlags: [MGS2, MGS3]`.
- Independently extracted each immutable header tail after the canonical body
  and compared its complete lexical tokens with the new offline fixture. All
  three token sequences are equal, SHA-256
  `8ade693eb22bd65377db0fed88492cb132ce0213af49d05d3b49fc00546e39fd`.
  Recorded in `attachments/tail-checks.json`; fixture whitespace cleanup
  preserves those tokens. The reviewed tail contains controller lists,
  language helpers and camera bounds, with no namespace redirection or macros.
- Protected-file and real-diff checks: `check_delivery.py` compares every
  pre-existing tracked file except the three scoped code/test/doc files and
  this round's attachments against the baseline. Output:
  `Protected tracked files byte-identical: 77`. Installer, settings schema,
  constraints/templates, original fixture, shortcuts/pins, CI/release policy,
  framework copies and every earlier seat record are untouched.
  `git diff --check 2c7a0372cb251b78b0c7ea75ad5581d04edf270d`
  → exit 0, no output after normalizing the copied fixture's trailing whitespace.
  Reviewed actual diff: only scoped parser/tests/documentation, new tail fixture
  and this round's evidence/report are changed.
- `python3 -m pytest tests/ -q` → exit 0, `273 passed in 5.48s`.
- `python3 -m ruff check .` → exit 0, `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py`
  → exit 0, no output. Python 3.9 AST syntax parsing also succeeds for changed
  tool/tests. Environment commands: `python3 --version` → exit 0,
  `Python 3.9.6`; `uname -s` → exit 0, `Darwin`.
- `python3 tools/fw.py check` → exit 0, `0 error(s), 0 warning(s)`.
  `python3 tools/fw.py status` → exit 0, `all project checks pass`, framework
  3.1.0 unchanged; round 008 Worker started, Verifier not started. Earlier
  round 004 stale-report warnings remain unchanged and were not repaired.
- Direct branch CI: `gh run view 37284947709 --json status,conclusion,headSha,event,jobs,url`
  and `gh run view 37284947709 --log` → exit 0.
  URL: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37284947709`.
  Workflow-dispatch result `success`; all four checkout logs show literal
  `7ee96a824adf51cc9d65a58a46619dc6bd2bd158`.
  Linux 3.9: `273 passed in 5.81s`; Linux 3.11: `273 passed in 6.06s`;
  Linux 3.12: `273 passed in 8.49s`; Windows 3.12:
  `271 passed, 2 skipped in 26.88s`. All platform jobs succeed, including
  Linux lint, compilation and desktop validation.
- PR CI: `gh run view 37284950677 --json status,conclusion,headSha,event,jobs,url`
  and `gh run view 37284950677 --log` → exit 0.
  URL: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37284950677`.
  Result `success`; head is final code commit but all checkout logs show
  generated merge commit `11a492504f4f3a85f18162539ee5559e34cb656d`.
  Linux 3.9/3.11/3.12: respectively `273 passed in 6.63s`,
  `273 passed in 5.50s`, `273 passed in 6.48s`; Windows:
  `271 passed, 2 skipped in 20.92s`. This is integration evidence, separately
  identified from the direct branch checkout.
- Corrective draft PR created with `gh pr create --draft --base main --head worker/008-canonical-namespace-boundary ...`
  → exit 0, `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/11`.
  References prior draft PR #10; no prior candidate was edited or closed.

## Not verified

No real Config Tool exports, upstream binaries, installer execution, game boots,
GUI rendering, audio compatibility, licensed hardware, repair/removal or
release-build MGS3 FPS applicability were checked. Static conditional flag union
is unchanged and is not a runtime claim. Windows CI skips the two existing
privileged symlink tests; this delivery does not claim those tests ran there.

Independent Verifier/Brain acceptance and owner merge approval remain pending.
No merge, tag, release or repository-setting action was performed. CI above
covers the exact final code and its generated PR merge checkout; subsequent
supporting-evidence/report commits do not alter code, tests or product docs.

An intermediate repeated full suite failed with `1 failed, 272 passed` because
the first evidence JSON contained local home paths. The evidence serializer now
redacts those paths. The final exact-code suite and framework checks above are
green; the failed attempt is recorded in `attachments/hygiene-correction.txt`.

## Changed

- `tools/capture_settings_schema.py`: ignore quoted namespace spelling, require
  the complete reviewed global preamble, and validate all trailing context
  against the exact reviewed token sequence (or an empty minimal header tail).
- `tests/test_schema_capture.py`: add 28 offline cases proving namespace rejection
  through API/CLI and supported-header/literal/hash success. Preserve prior tests.
- `tests/fixtures/hdfix-reviewed-header-tail.hpp`: new offline copy of the shared
  reviewed upstream tail; original baseline fixture is unchanged.
- `docs/UPGRADING.md`: document the enforced whole-header allowlist and its
  intentionally conservative requirement for review of any tail change.
- This round's attachments: reproducible old/new tool checks, source/tail
  equality and hash evidence, final local and direct/PR CI outputs, and the
  evidence-hygiene correction record. Existing Brain evidence is unchanged.
- This round's `worker.md`: exact-commit Worker report. `docs/state.md` unchanged.

## Open questions

None blocking Worker delivery. New upstream includes, guards, tail tokens,
namespaces or other header declarations deliberately require source-format
review. Verifier and Brain decide whether the conservative allowlist satisfies
round acceptance. Owner controls any merge decision.
