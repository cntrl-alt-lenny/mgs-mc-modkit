<!-- fw-report
round: 004-mod-compatibility-audit
role: verifier
branch: verifier/004-mod-compatibility-audit
head: 6105156a4749334f6ac03c9b78a948be948324f3
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T19:28:11Z
-->
# Verifier report: 004-mod-compatibility-audit

Reviewed delivery: `6105156a4749334f6ac03c9b78a948be948324f3`.
Baseline: `f28f9eaea634b71f5bb788794635304e0987a764`.
Independent retrievals: 2026-10-03 UTC, with the final official API comparison
at `2026-10-03T19:24:39.960862+00:00`. Local host: macOS, Python 3.9.6.
All code/test/source comparisons below refer to the literal reviewed delivery.
Only this report is written or committed by the Verifier.

## Findings

None. No BLOCKER, SHOULD FIX or contradictory Worker claim was found.

### Blind first pass and acceptance criteria

The required start command selected the literal delivery above. Read the project
rules, framework, Verifier card, brief, actual diff, baseline pin/layout/config
code and compact attachments before opening this round's Worker report.
Independently queried official sources, downloaded and listed all six official
archives, compared schema declarations, ran the complete checks and inspected
actual CI checkout logs. Only then read the Worker report and compared it.

1. Met. The baseline is literal and all four pin/latest comparisons reproduce.
   Official latest-release queries and resolved commits match queries.json:

| Component | Kit pin | Latest stable observed | Resolved source commit |
|---|---|---|---|
| MGSHDFix | 4.1.0 | 4.1.2 | `33e80bf4d2223f6866b0b92e06c3c9b85efab652` |
| MGS2 Community Bugfix Compilation | 3.0.0 | 3.0.0 | `373bb5dd622148adf33818d1cfcfd913eadec1d9` |
| MGS3 Community Bugfix Compilation | 2.0.1 | 2.0.1 | `0dbc487bce554fb0b4863ac0f27c4fe21f870a5c` |
| MGSM2Fix | v3.6 | v3.7.3 | `97172f569dbe518760438c847d0fc5d28e71dcd7` |

2. Met. The ten official release bodies represented in releases.json and four
   immutable READMEs match fresh API retrievals and their recorded hashes.
   HD's intervening controller, performance and restoration changes are relevant
   leads, not kit boot results. MGS2 3.0.0's removed hair/wall/title/GCX fixes and
   HD 4.1.0's reliance on restored NTSC row files establish a real coupling.
   M2's intervening notes concentrate on Volume 2/flashback support and a Proton
   crash reported for Volume 2; no demonstrated Volume 1 benefit was inferred.
   Upstream game-title/official-patch statements are distinguished from tested
   current Konami-build compatibility. The lack of an exhaustive patch matrix
   and lack of a dedicated removal procedure are explicitly recorded.
3. Met. The six downloads reproduce all recorded hashes, file counts, configs,
   listing hashes and layout/collision summaries. Exact schema and INI evidence
   reproduce, with actual Config Tool output correctly left unverified.
4. Met. Keeping all four existing pins now is supported. A separately authorized
   HD 4.1.2 slice with unchanged base compilations/M2 is a reasoned investigation,
   conditional on per-game exports, an explicit custom-setting migration policy,
   ownership/removal checks and real Windows/Deck tests. It is not ready based
   on schema counts, same paths or green audit CI alone.
5. Met for delivered scope and Worker freshness; Verifier publication completes
   the report set. All 58 baseline tracked files are byte-identical. The nine
   additions are this round's brief, Worker report and seven compact attachments.
   No product, pins, shortcuts, tests, framework, state or guidance changes.
6. Met. Important version/layout/schema/runtime-source claims were independently
   re-derived before reading worker.md. No earlier review was substituted for
   review of this literal delivery. Pass two found agreement rather than a
   narrative-versus-source discrepancy.

### Independent compatibility evidence

Official primary identities are the repositories and exact release/source URLs
recorded in attachments/queries.json and releases.json. The actual queries used
`gh api repos/<repo>/releases/latest`, `gh api repos/<repo>/commits/<tag>`,
`gh api repos/<repo>/releases/tags/<tag>` and
`gh api 'repos/<repo>/contents/README.md?ref=<literal-commit>'`.
Each subprocess exited 0. Independent assertions compared tag, commit, release
ID, release-body hash, README hash, asset URL and official API digest.
The final rerun printed four `LATEST/SOURCE MATCH` rows, followed by
`10 official release identities/body hashes and 6 asset URLs/API digests MATCH`.
The public attachment queries make these checks reproducible without local cache.

Inspected release pages include:
`https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.2`,
`https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation/releases/tag/3.0.0`,
`https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation/releases/tag/2.0.1`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.3`.

HD's update instructions say `Delete d3d11.dll from your game folder.`
That is upstream advice, not authorization to remove unrelated DLLs. The kit's
MGS1 loader has the same filename in a different game directory. The immutable
READMEs and release notes retain the HD and M2 Proton overrides used by the kit;
compilations recommend HD, then audio, then the base pack. AI addon files are
outside the vanilla-faithful assessment. New HD restoration defaults still need
an explicit policy; the kit's Solidus difficulty and FPS enable toggles remain
disabled in its unchanged template.

Independently downloaded archive results (curl and bsdtar each exit 0):

| Archive | SHA-256 | Regular files |
|---|---|---|
| MGSHDFix_4.1.0.zip | `413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523` | 11 |
| MGSHDFix_4.1.2.zip | `fbac84acc36bd395ab649beb576cf60e861fb43d3b36c26057fe900f5fa38e1d` | 11 |
| MGSM2Fix_3.6.0.zip | `a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d` | 7 |
| MGSM2Fix_3.7.3.zip | `0dabbe0b74bd1844d9f03d864949534ca3c29ea7bd9cf109f877963186e4aa80` | 7 |
| MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip | `a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003` | 10348 |
| MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip | `a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769` | 4449 |

Both HD versions contain the required loaders and ASI/Config Tool paths, but no
.settings export. Both M2 versions retain required paths and identical shipped
INI bytes: `ba708ee49fcb95ad3c81623088f5f94d3de00bcaf6b533cc60e95aaa4ebd8417`,
ten sections and 31 keys. Independent zip reads and install.parse_ini reproduce
m2fix-ini.json, including Launcher StartGame and update-notification values.
The two compilation layouts contain the required ASIs. No HD/base exact-path
intersection or HD/M2 path migration appears. Six MGS2 audio replacements and
three French MGS3 codec replacements do appear; empty HD/base intersections do
not prove compatibility with owner-supplied audio. Compilation INIs retain
independent shipped update-notification flags, not covered by M2/HD suppression.

HD sources at 4.1.0/4.1.1/4.1.2 were independently fetched. The baseline source
and fixture agree; 4.1.1's two schema-source hashes equal 4.1.0. At 4.1.2 an
independent declaration parser, separate from the capture helper, resolves the
exact key constants and flag aliases and finds 128 -> 131 union keys:

- Added Bugfixes: `Fix Dropped Item Toss`, `Fix Emissive Textures`,
  `Fix Lighting Bounding Boxes`.
- Added Model Quality && Level of Detail Enhancements:
  `Blend Particle Effect Sprites`; removed `Show Soft Particles`.
- Game applicability also changes: menu confirm/cancel and broken PS2 VFX extend
  to MGS3; three FPS declarations move behind a conditional alias. A raw count
  of 128 from the existing helper silently misses those alias declarations.

The attachment helper's static-union correction is reproducible and explicitly
limited. It does not prove a per-game export. Reading the real source diff
confirms the particle Boolean default changes from true to false, the three new
bugfix declarations default true, and the captured common-key explicit choices
and supported integer constraints have no delta. Dynamic choices, float ranges,
per-build flags and actual generated output remain outside that captured claim.

Candidate config.cpp independently confirms missing-section/key errors invoke
FatalConfigError and `FreeLibraryAndExitThread(baseModule, 1)` (source lines
142-153, 189-197); candidate reads use the newly required keys. This supports
unsafe configuration initialization after a numeric-only bump, not proof that
an entire game process exits. Primary source:
`https://github.com/ShizCalev/MGSHDFix/blob/33e80bf4d2223f6866b0b92e06c3c9b85efab652/src/resources/config.cpp`.
M2 registry handling is present at v3.6 src/mgs1.cpp and v3.7.3
src/m2fix/m2utils.cpp; independent API source reads confirm the same
DISABLEDXMAXIMIZEDWINDOWEDMODE add/remove string. Its shipped switch is false.
That state is outside the kit file manifest if opted into; it is not established
as a new candidate regression. Current game-build compatibility is unverified.

### Commands, actual output and exit codes

Except the advisory exit explicitly noted, these commands exited 0. Temporary
paths are written as `<source>`, `<cache>` and `<scratch>`; no personal paths,
archives or binaries are committed in this report.

- `git fetch origin`; `git worktree add --detach .worktrees/verifier-004 origin/main`:
  `HEAD is now at f28f9ea Merge pull request #6 from cntrl-alt-lenny/verifier/003-product-integration`.
- `python3 tools/fw.py start --role verifier --round 004-mod-compatibility-audit`:
  `seat ok: verifier, round 004-mod-compatibility-audit, branch verifier/004-mod-compatibility-audit at 6105156a4749`;
  `reviewing exactly 6105156a4749334f6ac03c9b78a948be948324f3 from origin/worker/004-mod-compatibility-audit`.
- `git rev-parse origin/main HEAD`: the two literal identities at the top.
- `git diff --stat origin/main HEAD` and `git diff --name-only origin/main HEAD`:
  nine round-only additions. Independent git ls-tree/git show byte assertions:
  `All 58 baseline tracked files byte-identical; only round004 records added`.
  All six framework copy fingerprints match the unchanged manifest.
- Inspected tools/check_pins.py before running it. `python3 tools/check_pins.py`
  exited 1, with two UPDATE rows (HD 4.1.2, M2 v3.7.3), two current base rows,
  and `2 update(s) available. These are NOT drop-in bumps`.
  This advisory result is neither a failed network query nor a test failure.
- `python3 tools/fw.py check`: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status`: pin/latest 3.1.0; owner-approves;
  Worker reported at 5993e5c66935; Verifier started without report;
  `all project checks pass`; next action waits for this Verifier.
- `python3 -m pytest tests/ -q`: `203 passed in 14.23s`.
- `python3 -m ruff check .`: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py`: no output.
- `python3 --version`: `Python 3.9.6`; Ruff version: `0.15.12`.
- `git diff --check origin/main HEAD`: no output.
- `python3 docs/rounds/004-mod-compatibility-audit/attachments/inspect_archives.py docs/rounds/004-mod-compatibility-audit/attachments/releases.json <cache> <scratch>/archives.json`:
  all six curl/listing exits 0, hashes/counts as above; both layout deltas and
  HD/base collision sets empty. The fresh JSON equals archives.json after
  removing only its retrieval timestamp. No downloaded binary was executed.
- `shasum -a 256 <cache>/*.zip`: independently reproduced all six hashes above.
- `git clone --filter=blob:none --no-checkout --single-branch --branch 4.1.2 <official-HD-repository> <source>`;
  `git -C <source> fetch --depth 1 origin tag 4.1.0 tag 4.1.1`:
  succeeded. `git diff 4.1.0 4.1.2 -- ConfigTool/tab_data.cpp src/resources/config_keys.hpp`
  was read independently, including defaults and game flags.
- `python3 docs/rounds/004-mod-compatibility-audit/attachments/inspect_schema.py <source> <scratch>/schema <scratch>/schema.json`:
  `baseline_fixture_equal: true`, reviewed counts 128/128/131, four additions,
  one removal, no common type/captured-constraint delta. Fresh JSON equals
  schema-delta.json. Independent constant/declaration parsing also printed
  `Independent declaration counts 128 131` and the same exact added/removed keys.
- `git show 4.1.2:src/resources/config.cpp`, plus official M2 content API reads:
  source evidence and limitations described above.
- Both unchanged shortcut pins match v2.3.0 and installer SHA-256
  `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`;
  Windows CRLF independently asserted.
- `python3 tools/fw.py delivery --round 004-mod-compatibility-audit`:
  `origin/verifier/004-mod-compatibility-audit (6105156a4749): delivered`;
  `worker: report describes 5993e5c66935`.
  Only worker.md changed after that described commit; no stale audit code.
- `gh run view 37147204728 --json headSha,status,conclusion`:
  literal reviewed head; completed/success. `gh run view 37147204728 --log`
  confirms literal `6105156a4749334f6ac03c9b78a948be948324f3` after checkout
  in all four direct-run jobs. Actual results:

```text
Linux Python 3.9: 203 passed in 5.70s
Linux Python 3.11: 203 passed in 4.58s
Linux Python 3.12: 203 passed in 5.92s
Windows Python 3.12: 201 passed, 2 skipped in 28.42s
```

  All Linux lint steps: `All checks passed!`; compilation and desktop validation
  completed successfully. Windows skips concern privileged symlink creation.
  Direct run: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37147204728`.
- `gh run view 37147198719 --log`: the final PR run actually checks out
  synthetic merge `93914618072f51cd021c4fba31c7699edea63ac7`, not metadata
  headSha. It is kept separate from the direct evidence above.
- `gh pr view 7 --json headRefOid,state`: reviewed delivery, OPEN. No PR text,
  issue, repository setting, merge, tag or release was changed by this seat.

### Pass two comparison

The Worker report agrees with the independent release/source/archive evidence,
schema deltas and limits, unchanged baseline bytes, advisory exit interpretation,
and automated-versus-hardware distinction. Its final direct CI is correctly
attributed and distinct from PR merge CI. The recommendation to keep the complete
current set and defer M2 is justified as an audit judgement, not a compatibility
certification. No contradictory or unsupported readiness claim was found.

## Not verified

No actual Config Tool export, licensed game boot, current Konami patch matrix,
native Windows/Deck GUI/controller test, Deck performance measurement, Nexus
payload/playback or real hardware repair/removal was obtained. No downloaded
binary was executed and no game directory modified. Official README patch claims
were checked as upstream statements, not independently verified Konami behavior.
No archive listing/hash or passing CI proves those outcomes. Dynamic settings,
float bounds/defaults, build-conditional output and current custom settings need
actual per-game exports and hardware checks in a separately authorized upgrade.
Registry/runtime-created files and exact owner-audio intersections remain outside
this static audit. Repository protections and historical owner approval chats
were not audited. Brain acceptance and owner approval remain outside this seat.

## Verdict

No findings prevent Brain from accepting this audit at the literal reviewed
Worker delivery. The important external claims reproduce, the baseline remains
unchanged, and the report accurately states what static evidence cannot prove.
Keep the current pins now; any future HD-focused coordinated slice requires the
named schema/migration, ownership/removal and real-machine prerequisites. This
is an assessment, not approval to upgrade, merge or release. Confidence is high
in the reproduced source/layout evidence and explicitly limited for runtime
compatibility. Only this report is committed by the Verifier.
