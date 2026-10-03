<!-- fw-report
round: 006-schema-capture-safety
role: verifier
branch: verifier/006-schema-capture-safety
head: 0e083b27f83216762b0ed025a5293116782a1258
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T20:28:09Z
-->
Reviewed Worker commit: `0e083b27f83216762b0ed025a5293116782a1258`.
Main baseline: `f28f9eaea634b71f5bb788794635304e0987a764`.
Worker seat baseline: `018a18952cedc278b7443fc16d3e2f132ddf46fc`.
Host: macOS, Python 3.9.6. All checks below ran against the literal reviewed
Worker commit before this report was added. Only this report is changed by this seat.

## Findings

- **BLOCKER — `tools/capture_settings_schema.py:118-125` (called at line 145):
  canonical string declarations still permit misleading successful capture.**
  `constant_values` searches for matching declarations without validating the
  surrounding header syntax or preprocessor branches. A valid conditional
  changes a referenced setting's spelling in one branch, using the unsupported
  but valid C++ spelling `constexpr char const*`; the other branch uses
  `constexpr const char*`. Capture silently ignores the first branch and returns
  exit 0 with only the second branch's key. Thus unknown declaration syntax
  can hide an eligible key while producing authoritative-looking partial JSON.
  This violates acceptance criterion 3 and the documented unsupported-syntax
  rejection at `docs/UPGRADING.md:82-84`. It does not affect the three unchanged
  reviewed upstream sources, but stopping this class of misleading future-source
  success is the purpose of this round. Reject unreviewed conditional canonical
  declarations, with an actionable error and empty CLI stdout; a general C++
  parser or evaluating arbitrary preprocessing is unnecessary. Add a focused
  regression for this case before acceptance.

Reproduction from the seat root at the reviewed SHA (temporary files only):

```python
import json, runpy, subprocess, sys, tempfile
from pathlib import Path
fixture = runpy.run_path('tests/test_schema_capture.py')
make_source = fixture['source']
constants = fixture['CONSTANTS'].replace(
    'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";',
    '#if defined(NEW_FORMAT)\n'
    'constexpr char const* Demo_Setting = "Replacement Key";\n'
    '#else\n'
    'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";\n'
    '#endif')
with tempfile.TemporaryDirectory() as scratch:
    root = make_source(Path(scratch), constants=constants)
    result = subprocess.run(
        [sys.executable, 'tools/capture_settings_schema.py', str(root),
         '--tag', 'test', '--tree', 'tree'], capture_output=True, text=True)
    print(result.returncode, repr(result.stderr))
    print(list(json.loads(result.stdout)['fields']['First Person Shooter Mode']))
```

Actual output, wrapper exit 0:

```text
0 ''
['Enable First Person Shooter Mode', 'First Person Shooter - Movement Enabled By Default', 'Toggle First Person Shooter Movement']
```

With `NEW_FORMAT` defined the C++ declaration names the first setting
`Replacement Key`; a bounded union would also contain that spelling. The
supported-boundary response should instead be a source-format error because
this header conditional/declaration layout has not been reviewed. Neither
happens. This is an input-format failure, not a claim that current binaries use
this synthetic key.

### Blind first pass and acceptance criteria

Completed source/diff review, original-source captures, independent name/type
comparison, failure probes, local suite and exact-checkout CI inspection before
opening `worker.md`. Reviewed every implementation Python/test line and the
upgrading addition; also read the immutable-source helper and evidence.

1. **Met:** 4.1.0 JSON is exactly equal to the unchanged fixture. 4.1.1 has the
   same exact field/type and constraint maps, with its own supplied identity.
2. **Met for the reviewed static union:** 4.1.2 includes all 131 exact names/types,
   including the three FPS alias fields. Added Bool keys are `Fix Dropped Item
   Toss`, `Fix Emissive Textures`, `Fix Lighting Bounding Boxes` in `Bugfixes`,
   and `Blend Particle Effect Sprites` in `Model Quality && Level of Detail
   Enhancements`; removed Bool key is `Show Soft Particles` in that latter
   section. No common type or captured-constraint differences. The explicit
   `flag_unions` and documentation accurately distinguish development-macro
   union membership from release MGS3 FPS support.
3. **Not met:** tab initializer/flag validation rejects the probed unsupported
   formats, but the canonical-constant header hole above still returns success.
   Known MG-only fields remain excluded in the focused suite.
4. **Met for added regressions, with a coverage gap:** the 32 new tests pass and
   30 fail against the old tool. They meaningfully expose alias omission and
   unknown-field/flag success. They do not probe guarded canonical strings.
5. **Automated/platform checks met:** full offline suite, lint, compilation,
   framework checks and exact-final-SHA Linux/Windows CI pass. Protected files
   are unchanged. Runtime compatibility is not established.
6. **Met:** independent blind pass completed before Worker comparison.

### Commands and actual evidence

- `git fetch origin`, `git worktree add --detach .worktrees/verifier-006 origin/main`
  and `python3 tools/fw.py start --role verifier --round 006-schema-capture-safety`
  each exit 0. Start selects `origin/worker/006-schema-capture-safety` at
  `0e083b27f83216762b0ed025a5293116782a1258`, on the isolated Verifier branch.
- `git rev-parse HEAD` exit 0 prints that full SHA.
  `git diff origin/main HEAD --stat` and the real production/test diff were read.
  `git diff 018a18952cedc278b7443fc16d3e2f132ddf46fc HEAD --name-status` exit 0
  lists only capture tool, upgrading explanation, new tests, two source-check
  attachments and Worker report. Inherited audit/stopped-round records are
  additional relative to main. `git diff --check` exit 0, no output.
- Independent Python byte comparison using `git ls-tree -r --name-only` and
  `git show <baseline>:<path>` against working files exits 0:
  `All 58 baseline files compared; only authorized UPGRADING and capture tool changed`.
  Against the Worker seat baseline: `69 existing seat baseline files unchanged`.
  This covers installer, pins, shortcuts, fixture, settings/schema/constraints,
  release/CI files, framework copies, roles and previous round records.
- Independent SHA/tag assertions exit 0: both shortcuts contain `v2.3.0` and
  installer SHA-256 `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`.
  Windows shortcut bytes are identical to baseline, preserving CRLF.
- `python3 docs/rounds/006-schema-capture-safety/attachments/check_sources.py <scratch>/sources <scratch>/source-checks.json`
  exit 0. All six underlying immutable official source downloads and three CLI
  invocations exit 0. Output:

```text
4.1.0: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.1: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match
4.1.2: CLI exit 0; 131 exact expected keys; constraints and ORIGINAL hashes match
4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed
```

Original bytes came from `raw.githubusercontent.com/ShizCalev/MGSHDFix` at
literal source commits, not normalized alias copies:

| Tag | Commit | tab_data.cpp SHA-256 | config_keys.hpp SHA-256 |
|---|---|---|---|
| 4.1.0 | `f4f662d67a2a033dee0877e436a0fe65eb719e0b` | `4b7cec4708ae0fa4af6de06ec0244426ba67a826376f6a6d6e37b2aa1a2690c8` | `2c06734d5c9ad2abcf7756dc09aa7cc72cce0cb6bc037d7594fbabd9edc40882` |
| 4.1.1 | `0120a6b1116913733f4dc21c287813d4cb2bb659` | `4b7cec4708ae0fa4af6de06ec0244426ba67a826376f6a6d6e37b2aa1a2690c8` | `2c06734d5c9ad2abcf7756dc09aa7cc72cce0cb6bc037d7594fbabd9edc40882` |
| 4.1.2 | `33e80bf4d2223f6866b0b92e06c3c9b85efab652` | `4b2575f6075fb7a8534c73a0adc048a7b0515082e89da762ed79bfe441f65e2e` | `8e03aa5d90662fcadd0ef729d5dfe36d6045545c1772be2cee6be12f28aa9c94` |

- A separate scratch Python parser reads literal ConfigKeys string declarations
  and canonical field declarations using regexes rather than the new structural
  parser. It checks the actual two `kFirstPersonViewGameFlags` branches, then
  independently builds exact section/key/type maps. Running it exits 0:
  `4.1.0 independent exact-name/type reference matches 128`,
  `4.1.1 independent exact-name/type reference matches 128`,
  `4.1.2 independent exact-name/type reference matches 131`;
  all original byte hashes match. No count-only assertion was used.
  Comparison to committed source-checks.json excluding only retrieval timestamp
  exits 0: `Committed live-source evidence reproduced excluding timestamp`.
- `git show origin/main:tools/capture_settings_schema.py` supplies the before
  implementation in scratch. Its captures return 128 for all three immutable
  sources. Exact missing 4.1.2 keys are `Enable First Person Shooter Mode`,
  `First Person Shooter - Movement Enabled By Default`, `Toggle First Person
  Shooter Movement`. A synthetic `UNKNOWN_FLAGS` input succeeds with just
  `System Specific Fixes` and `Window Settings` before the change. The reviewed
  CLI instead exits 1, stdout empty:
  `capture failed: Unsupported source construct: game flags UNKNOWN_FLAGS; review the upstream source format`.
- A scratch copy of the new tests importing the old capture module:
  `python3 -m pytest <scratch>/test_before.py -q` exit 1:
  `30 failed, 2 passed in 0.34s`. The CLI tests also resolve the old tool path.
- `python3 -m pytest tests/test_schema_capture.py -q` exit 0:
  `32 passed in 0.18s`.
- `python3 -m pytest tests/ -q` exit 0: `235 passed in 6.87s`.
- `python3 -m ruff check .` exit 0: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py`
  exit 0, no output. `ast.parse(..., feature_version=(3,9))` on both changed
  Python modules exits 0: `Python 3.9 grammar accepted for both changed Python modules`.
- `python3 tools/fw.py check` exit 0: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status` exit 0: pinned/latest framework 3.1.0,
  `all project checks pass`, clean Verifier seat; round 006 Worker reported,
  round 005 superseded. It reports stale round 004 reports as the Worker noted;
  this is prior-round freshness for Brain to address, not implementation damage.

### Final exact-commit CI

`gh run list --branch worker/006-schema-capture-safety --limit 10 --json databaseId,event,headSha,status,conclusion,url`,
`gh run view 37150498729 --log`, `gh run view 37150470736 --log`, and
`gh run view 37150498729 --json status,conclusion,jobs` each exit 0.
Direct final run `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37150498729`
is `completed`, `success`. Every job's checkout log actually prints
`0e083b27f83216762b0ed025a5293116782a1258` after `git log -1 --format=%H`.

| Job | Actual suite result |
|---|---|
| Linux 3.9 | `235 passed in 13.24s` |
| Linux 3.11 | `235 passed in 4.74s` |
| Linux 3.12 | `235 passed in 4.48s` |
| Windows 3.12 | `233 passed, 2 skipped in 18.06s` |

Linux lint prints `All checks passed!` in each job; compilation and the
installation step containing `desktop-file-validate Install-MGS-Mods.desktop`
are successful. Native Windows archive-tool confirmation is successful.
The two Windows skips are the existing symlink privilege cases.
The PR run `37150470736` checked generated merge
`408c7e15c73fad6dfd5d3d86f89f4d1eba8a1e41`, not the literal Worker SHA;
its matching headSha metadata was not used as exact-commit proof.

### Worker comparison

Read `worker.md` only after the blind checks above. Reproduced its baseline,
immutable-source equality, original hashes, exact union delta, meaningful
regression behavior and automated results. The claim that capture
`rejects unsupported constructs with an actionable error` and that unsupported
`conditional forms ... or canonical key syntax stop capture` is too broad:
the canonical-string counterexample exits 0 without any error. The reported
limitations for exports, dynamic choices, float bounds/defaults and release
applicability are accurate. Final direct CI independently confirms the
report-only delivery SHA, beyond the report's earlier implementation CI.

## Not verified

No actual Windows/Steam Deck game boots, generated per-game Config Tool exports,
upstream release-binary macro applicability, Nexus audio smoke tests, native GUI
or controller rendering, performance, or live repair/removal. No upstream binary
was executed, mod installed or Nexus audio obtained. Static union extraction and
synthetic regression success cannot establish these outcomes. Real exports and
runtime checks remain requirements before a future coordinated mod upgrade.
Float bounds/defaults, dynamic choices and reviewed opaque camera bounds retain
the tool's documented limits. Supplied CLI tag/tree labels are not authenticated
by capture itself; immutable downloads and hashes provided identity in this audit.
Local desktop-file-validate is unavailable; actual Linux CI ran it successfully.
No repository protection/settings audit or merge/release action was performed.

## Verdict

Recommend **do not accept/merge this delivery** until the canonical-string
conditional omission is addressed and independently reverified at a new exact
commit. The reviewed upstream captures are correct, the initial flag omission
is fixed, automated/platform checks are green and protected product files are
preserved. Confidence is high in those bounded results and in the reproduced
remaining failure. Acceptance criterion 3 remains unmet despite passing tests;
this report informs Brain's decision and does not approve or merge anything.
