<!-- fw-report
round: 006-schema-capture-safety
role: worker
branch: worker/006-schema-capture-safety
head: 95c6cc7092f876d35f7e98011b3bcff09dd49475
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T20:07:26Z
-->
## Verified

Implemented the corrected round 006 brief. Static capture now resolves reviewed
flag aliases, traverses the whole reviewed initializer and rejects unsupported
constructs with an actionable error. This changes the developer capture tool;
no installed settings, mod pin or installer behavior changed.

Main baseline: `f28f9eaea634b71f5bb788794635304e0987a764`.
Brain-selected seat baseline: `018a18952cedc278b7443fc16d3e2f132ddf46fc`.
Implementation/check commit: `95c6cc7092f876d35f7e98011b3bcff09dd49475`.
Commands below refer to that literal implementation unless otherwise stated.
Temporary paths are written as `<scratch>` or `<source>`; no personal paths,
downloaded binaries or complete upstream source copies are committed.

### Start and scope

- `git fetch origin` → exit 0, no output.
- `git worktree add --detach .worktrees/worker-006 origin/main` → exit 0:
  `HEAD is now at f28f9ea Merge pull request #6 from cntrl-alt-lenny/verifier/003-product-integration`.
- `python3 tools/fw.py start --role worker --round 006-schema-capture-safety`
  → exit 0: `seat ok: worker, round 006-schema-capture-safety, branch worker/006-schema-capture-safety at 018a18952ced`.
- Read the project instructions, framework, Worker card, round 006 brief, round
  004 brief/reports/schema evidence, existing capture tool, baseline fixture,
  relevant settings tests and upgrade instructions. Round 006 explicitly permits
  starting on the reviewed baseline while the audit merge remains pending and
  supersedes round 005's dispatch condition. Round 005 was not resumed or edited.
- `git rev-parse HEAD` → exit 0: `95c6cc7092f876d35f7e98011b3bcff09dd49475`.
- `git diff --name-status 018a18952ced HEAD` → exit 0: exactly five implementation
  changes: capture tool, upgrading explanation, new focused test module, and
  this round's `attachments/check_sources.py` / `attachments/source-checks.json`.
  The report is the only subsequent change. Relative to main, inherited accepted
  audit and stopped-round records also appear; these are not implementation edits.
- Python comparison of every `git ls-tree -r --name-only 018a18952ced` path
  except `tools/capture_settings_schema.py` and `docs/UPGRADING.md`, using
  `git show 018a18952ced:<path>` versus working-tree bytes → exit 0:
  `69 existing files byte-identical to seat baseline`.
  This includes install.py, its template/schema/constraints, the original
  4.1.0 fixture, both shortcuts, pins/release files, all framework copies,
  role guidance and earlier round records.
- Independent shortcut byte/hash assertions → exit 0:
  both tags `v2.3.0`, both SHA-256s
  `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`
  match install.py; `Windows CRLF preserved`. No hashes were regenerated since
  install.py did not change. `git diff --check` → exit 0, no output.

### Before and after

Before implementation, immutable source bytes obtained with
`git show <literal-upstream-commit>:<source-path>` were captured with the original
tool at `018a18952ced`. The reproduction command loaded capture through
importlib and printed:

```text
4.1.0 128
4.1.1 128
4.1.2 128
UNKNOWN_FLAGS: success, 128 keys
```

Exit 0. The UNKNOWN_FLAGS case replaced only the three alias references in a
temporary 4.1.2 copy; it demonstrates misleading success, not original-source
compatibility. The original source copy was restored. No game files were touched.

The ten targeted regressions from the new test module were then executed against
`git show 018a18952ced:tools/capture_settings_schema.py`, loaded into
`sys.modules['tools.capture_settings_schema']` with importlib before
`pytest.main`. Command selections were
`tests/test_schema_capture.py::test_alias_keeps_all_three_exact_fields_and_original_hashes`
and `tests/test_schema_capture.py::test_unknown_or_malformed_flags_never_succeed_partially`,
with `-q --tb=line` → exit 1: `10 failed in 0.05s`.
Two failed with `KeyError: 'First Person Shooter Mode'`; eight failed with
`DID NOT RAISE <class 'RuntimeError'>`. Tests refer to the new test code at the
implementation commit while deliberately substituting the baseline tool.

After implementation, `python3 -m pytest tests/test_schema_capture.py -q`
→ exit 0: `32 passed in 0.21s`. Coverage includes exact synthetic baseline
names/types/choices/bounds, conditional and unconditional aliases, alias chains,
parenthesized unions, MG-only exclusion, unknown names/operators/functions,
malformed rows/types/keys/bounds/choices, missing constants, cycles, unsupported
conditionals, CLI success/failure and original BOM/CRLF source-byte hashes.

A separate subprocess CLI reproduction on the temporary UNKNOWN_FLAGS copy
→ underlying CLI exit 1, wrapper assertion exit 0:

```text
CLI exit: 1 stdout bytes: 0
capture failed: Unsupported source construct: game flags UNKNOWN_FLAGS; review the upstream source format
```

Capture accumulates privately and prints JSON only on success. Source-format
failures cannot emit partial CLI JSON. Exceptions identify the construct and
request review; known MG-only fields remain intentionally excluded.

### Immutable source comparisons

`attachments/check_sources.py` is a separate live check, never invoked by the
offline test suite. It downloads both original source files from official raw
GitHub URLs containing the literal commits below, checks their hashes against
accepted round 004 evidence, invokes the real capture CLI, and compares exact
field/type maps and constraints. It reconstructs the expected 4.1.2 map by
applying the four reviewed additions and one removal to the baseline fixture,
rather than inferring correctness from counts.

Actual command at the implementation commit:
`python3 docs/rounds/006-schema-capture-safety/attachments/check_sources.py <scratch>/final-source <scratch>/final-source-checks.json`
→ exit 0. Every underlying `curl -fLsS --retry 2 <immutable-url> -o <source-file>`
and capture CLI subprocess exited 0. The committed source-checks.json retains
all six exact URLs, source hashes, identities and comparison outcomes. A JSON
comparison excluding only retrieval timestamp reproduced the attachment
→ exit 0: `Immutable check reproduces committed evidence excluding retrieval timestamp`.

```text
4.1.0: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.1: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.2: CLI exit 0; 131 exact expected keys; constraints and ORIGINAL hashes match
4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed
```

CLI arguments were `<source> --tag <version> --tree <literal-commit>`.
Source identities:

| Version | Literal commit | tab_data.cpp SHA-256 | config_keys.hpp SHA-256 |
|---|---|---|---|
| 4.1.0 | `f4f662d67a2a033dee0877e436a0fe65eb719e0b` | `4b7cec4708ae0fa4af6de06ec0244426ba67a826376f6a6d6e37b2aa1a2690c8` | `2c06734d5c9ad2abcf7756dc09aa7cc72cce0cb6bc037d7594fbabd9edc40882` |
| 4.1.1 | `0120a6b1116913733f4dc21c287813d4cb2bb659` | `4b7cec4708ae0fa4af6de06ec0244426ba67a826376f6a6d6e37b2aa1a2690c8` | `2c06734d5c9ad2abcf7756dc09aa7cc72cce0cb6bc037d7594fbabd9edc40882` |
| 4.1.2 | `33e80bf4d2223f6866b0b92e06c3c9b85efab652` | `4b2575f6075fb7a8534c73a0adc048a7b0515082e89da762ed79bfe441f65e2e` | `8e03aa5d90662fcadd0ef729d5dfe36d6045545c1772be2cee6be12f28aa9c94` |

Exact 4.1.2 Boolean additions:
`[Bugfixes] Fix Dropped Item Toss`, `Fix Emissive Textures`,
`Fix Lighting Bounding Boxes`, and
`[Model Quality && Level of Detail Enhancements] Blend Particle Effect Sprites`.
Removed: `[Model Quality && Level of Detail Enhancements] Show Soft Particles`.
No common type or captured-constraint delta. All three FPS alias fields are
present by exact names/types: `Enable First Person Shooter Mode` (Bool),
`First Person Shooter - Movement Enabled By Default` (Bool),
`Toggle First Person Shooter Movement` (Hotkey).
The entire 4.1.0 JSON remains exactly equal to the unchanged original fixture;
4.1.1 fields/constraints also exactly equal it with their own identity labels.

### Bounded extraction contract

The tool supports the reviewed braced kTabs/tab/field layout and canonical
ConfigKeys section/setting constants, not a general C++ parser. It checks each
initializer, field kind/argument layout, exact game tokens and declarations.
Aliases support OR/parentheses/chains and the reviewed single-alias
`#if defined(NAME)` / `#else` / `#endif` form. Both branches are unioned without
rewriting source. `flag_unions` records the resolved alias sets when present;
no new output property changes the baseline 4.1.0 fixture.

4.1.2 records `kFirstPersonViewGameFlags: [MGS2, MGS3]`. MGS3 membership derives
from the development-macro branch; neither release-binary FPS support nor a
particular per-game export is asserted. Unsupported operators, identifiers,
conditional forms, changed wrappers or canonical key syntax stop capture.
Spacers and the reviewed inline achievement Safety Switch remain outside the
canonical fixture. Original bytes are hashed before comment parsing; no
normalization is passed off as original-source evidence.

### Complete local validation

At `95c6cc7092f876d35f7e98011b3bcff09dd49475`:

- `python3 -m pytest tests/ -q` → exit 0: `235 passed in 7.61s`.
- `python3 -m ruff check .` → exit 0: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py`
  → exit 0, no output (host Python 3.9).
- `python3 tools/fw.py check` → exit 0: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status` → exit 0: pinned/latest framework 3.1.0;
  owner-approves; round 005 superseded by 006; Worker 006 started with no report
  yet, Verifier not started; clean seat with one unpushed implementation commit;
  `all project checks pass`. It also reports round 004 Worker/Verifier records
  stale and directs Brain to address that earlier delivery. Personal-path
  cleanup suggestions are omitted. No earlier report was rewritten to alter
  that state. The corrected brief explicitly permits this implementation now.

### Implementation CI

- `git push origin worker/006-schema-capture-safety` → exit 0, pushed
  `018a189..95c6cc7` without force.
- `gh workflow run ci.yml --ref worker/006-schema-capture-safety` → exit 0:
  `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37150153707`.
- `gh run view 37150153707 --log` → exit 0. All four checkout logs print
  `95c6cc7092f876d35f7e98011b3bcff09dd49475` after `git log -1 --format=%H`.
  Linux Python 3.9: `235 passed in 5.92s`; 3.11: `235 passed in 4.76s`;
  3.12: `235 passed in 4.63s`; Windows 3.12:
  `233 passed, 2 skipped in 14.98s`. All Linux lint steps print
  `All checks passed!`; compilation and desktop validation succeed.
  `gh run view 37150153707 --json status,conclusion` → exit 0:
  `completed`, `success`. This is direct branch checkout evidence.
- `gh pr create --draft --base main --head worker/006-schema-capture-safety --title <capture-title> --body-file <scratch>/pr.md`
  → exit 0: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/9`.
  It remains a draft pending independent verification/Brain review. No merge
  or release decision is implied.
- `python3 --version` → exit 0: `Python 3.9.6`.

The report stamp will add only this report. Final-stamp direct and PR CI logs
will be checked and recorded on PR #9 without making a claim that metadata
headSha identifies a generated PR merge checkout.

## Not verified

No actual per-game Config Tool export, compiled upstream build applicability,
licensed game boot, native GUI/controller behavior, Deck performance, audio or
real removal/repair test. No upstream binary was run, mod installed or Nexus
audio obtained. Static capture does not establish runtime compatibility.
Dynamic language/button/hotkey choices, float bounds/defaults, empty/dynamic
choice lists and the reviewed opaque third-person camera-distance bounds remain
outside its constraint evidence. Tag/tree CLI labels are caller-supplied;
this live check authenticates the source through immutable URLs and expected
original-byte hashes, while the tool itself does not verify checkout identity.
No claim of arbitrary C++ or arbitrary preprocessor support is made.

## Changed

- `tools/capture_settings_schema.py`: bounded structural field traversal,
  declared flag-union resolution, actionable failures and original-byte hashes.
- `tests/test_schema_capture.py`: 32 focused offline regressions.
- `docs/UPGRADING.md`: capture syntax, union applicability, original-byte identity
  and existing constraint/export limits. No other upgrade policy changes.
- This round's `attachments/check_sources.py` and `source-checks.json`: separate
  reproducible official immutable-source checks, not offline network dependencies.
- This round's `worker.md`: implementation and actual validation evidence.

All protected files and prior records remain unchanged. No merge, tag,
publication, repository-setting change or acceptance decision by this seat.

## Open questions

Independent Tier 2 verification must review the final stamped delivery, compare
exact fields against immutable sources and exercise unsupported input before
reading this report. Future upstream syntax changes require explicit review;
an error must not be bypassed by guessing keys or a count. Actual per-game
exports and licensed hardware checks remain prerequisites for any coupled mod
upgrade. Prior round 004 delivery freshness/merge decisions remain Brain/owner
work and are not changed here.
