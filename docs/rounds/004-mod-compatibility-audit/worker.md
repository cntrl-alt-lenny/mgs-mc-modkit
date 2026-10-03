<!-- fw-report
round: 004-mod-compatibility-audit
role: worker
branch: worker/004-mod-compatibility-audit
head: 5993e5c6693566c56289e59dcfc25a13d7d36d3f
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T19:14:46Z
-->
## Verified

Recommendation: keep the complete pinned set for now. This is an audit, not an
upgrade or a claim of real-game compatibility. MGSHDFix 4.1.2 offers relevant
fixes but requires a coordinated settings migration. MGSM2Fix v3.7.3 has the same
shipped INI and paths as v3.6, but that does not establish unchanged runtime
behavior. Both base compilations are already at their latest stable releases.

### Baseline and evidence identity

Main baseline: `f28f9eaea634b71f5bb788794635304e0987a764`.
The seat started from the Brain brief at
`ab1c0e7561c53e4439d6a544781747af99cd332f`. Local checks below ran at audit
attachment commit `cab17ae5a1ab7211cd46a65c20e0b5f3ab0cb9db`.
Temporary paths in commands are replaced by `<source>`, `<scratch>` and `<cache>`.
No archive contents were executed and no game directory was modified.

- Prerequisite: `gh pr view 6 --json state,mergedAt,mergeCommit` → exit 0:
  `state: MERGED; mergedAt: 2026-10-03T18:52:20Z; mergeCommit: f28f9eaea634b71f5bb788794635304e0987a764`.
- `python3 tools/fw.py start --role worker --round 004-mod-compatibility-audit`
  → exit 0: `seat ok: worker, round 004-mod-compatibility-audit, branch worker/004-mod-compatibility-audit at ab1c0e7561c5`.
- `git rev-parse HEAD` → exit 0:
  `cab17ae5a1ab7211cd46a65c20e0b5f3ab0cb9db`.
- `git diff --name-status f28f9eaea634b71f5bb788794635304e0987a764 HEAD`
  → exit 0: only eight additions: this round's brief and seven attachments
  (`archives.json`, `inspect_archives.py`, `inspect_schema.py`, `m2fix-ini.json`,
  `queries.json`, `releases.json`, `schema-delta.json`). No baseline file changed.
- A Python byte comparison using `git ls-tree -r --name-only <baseline>` and
  `git show <baseline>:<path>` versus `git show HEAD:<path>` → exit 0:
  `58 baseline tracked files byte-identical at HEAD`.
  This includes all product files, shortcuts, pins, tests, guidance and framework.
- `python3 --version` → exit 0: `Python 3.9.6`; `uname -s` → exit 0: `Darwin`.

### Official releases and sources

Retrieved 2026-10-03 UTC. `attachments/queries.json` retains each exact API
command, retrieval timestamp, exit code, release ID, resolved source commit,
immutable README URL and SHA-256. All latest-release, source-commit and README
queries exited 0. `attachments/releases.json` records intervening release
metadata and release-body hashes. Full API responses and source checkouts stayed
in temporary storage; the public queries reproduce them.

For each official repository the commands were
`gh api 'repos/<repository>/releases?per_page=100'`,
`gh api repos/<repository>/releases/latest`,
`gh api repos/<repository>/commits/<tag>`, and
`gh api 'repos/<repository>/contents/README.md?ref=<resolved-commit>'` → exit 0.
The advertised stable tags below exclude the moving nightly/preview prereleases.

| Component | Kit pin | Latest stable considered | Published UTC | Source commit |
|---|---|---|---|---|
| ShizCalev/MGSHDFix | 4.1.0 | 4.1.2 | 2026-09-18 10:45:29 | `33e80bf4d2223f6866b0b92e06c3c9b85efab652` |
| ShizCalev/MGS2-Community-Bugfix-Compilation | 3.0.0 | 3.0.0 | 2026-07-25 08:19:06 | `373bb5dd622148adf33818d1cfcfd913eadec1d9` |
| ShizCalev/MGS3-Community-Bugfix-Compilation | 2.0.1 | 2.0.1 | 2026-07-27 23:06:36 | `0dbc487bce554fb0b4863ac0f27c4fe21f870a5c` |
| nuggslet/MGSM2Fix | v3.6 | v3.7.3 | 2026-09-09 21:22:07 | `97172f569dbe518760438c847d0fc5d28e71dcd7` |

Official release sources:
`https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.0`,
`https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.1`,
`https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.2`,
`https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation/releases/tag/3.0.0`,
`https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation/releases/tag/2.0.1`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.6`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.1`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.2`,
`https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.3`.

Observed release claims, paraphrased; these are upstream claims, not kit boot tests:

- HD 4.1.1 fixes MGS3 throwing with a DualShock 3. HD 4.1.2 moves shader
  compilation earlier to address cutscene stutter/audio sync, fixes an MGS2
  title-screen-related even-numbered NG+ crash, RAY eyes, codec backgrounds,
  tanker fog overhead and Snake Tales selection audio. It adds codec/stinger
  visual restorations and item-toss correction, exposes MGS3 lighting/emissive
  switches and extends menu confirm/cancel selection to MGS3. The optional
  Solidus choking restoration also changes health drain/regain timing; retain
  the kit's disabled gameplay-altering choices. Performance-heavy restorations
  need hardware measurement, particularly on Deck.
- MGS2 3.0.0 removed asset fixes for Snake's hair, W42A walls, tanker title card
  and GCX typos because their fixes moved into MGSHDFix. HD 4.1.0 explicitly
  couples some MGS2 restorations to the compilation's NTSC row files. Keeping
  these as a set matters even with no common archive filenames. MGS3 2.0.1
  repairs The Pain cave water textures. Neither pack has a newer stable release
  in the retrieved list.
- M2 v3.7 adds Volume 2 bonus/Ghost Babel and MGS4-flashback support; v3.7.1
  addresses the flashback title, v3.7.2 the lingering MGS4 process, and v3.7.3 a
  Proton crash reported for Volume 2 bonus content. Its latest README still
  lists Volume 1 MGS1 (Steam app 2131630). It says official MGS1 patches 3.0.0
  and 1.5.0 supplied resolution and analog-input features respectively. These
  statements do not prove kit behavior on those game patches. The source has
  been substantially reorganized; identical INI bytes cannot prove binary
  equivalence. No compelling Volume 1-specific need to adopt v3.7.3 was
  established by these intervening notes.

### Archives, paths, ordering and removal

`attachments/archives.json` records the exact six asset URLs, asset/release IDs,
actual SHA-256s, bytes, file counts, listing digests, compact control paths and
config digests. All four pinned downloads match install.py's pinned hashes;
the two candidate downloads match their official API SHA-256 digests. No large
archive, binary or full asset listing is committed.

Actual audit command (exit 0):
`python3 docs/rounds/004-mod-compatibility-audit/attachments/inspect_archives.py docs/rounds/004-mod-compatibility-audit/attachments/releases.json <cache> <scratch>/archives.json`.
The helper ran each `curl -fL --retry 2 --max-time 300 -sS <exact-url> -o <cache>/<name>`
→ exit 0, computed SHA-256 with Python hashlib, and ran
`bsdtar -tf <cache>/<name>` → exit 0. The compact attachment represents the
subsequently slimmed output (full lists remained in cache). Independent
`shasum -a 256 <cache>/*.zip` → exit 0 reproduced these hashes:

| Archive | SHA-256 | Files |
|---|---|---|
| MGSHDFix_4.1.0.zip | `413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523` | 11 |
| MGSHDFix_4.1.2.zip | `fbac84acc36bd395ab649beb576cf60e861fb43d3b36c26057fe900f5fa38e1d` | 11 |
| MGSM2Fix_3.6.0.zip | `a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d` | 7 |
| MGSM2Fix_3.7.3.zip | `0dabbe0b74bd1844d9f03d864949534ca3c29ea7bd9cf109f877963186e4aa80` | 7 |
| MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip | `a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003` | 10348 |
| MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip | `a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769` | 4449 |

Actual helper output: `layout delta: {'MGSHDFix': {'added': [], 'removed': []}, 'MGSM2Fix': {'added': [], 'removed': []}}`;
`candidate HD/base collisions: {'MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip': [], 'MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip': []}`.

The kit's required paths exist: HD `winhttp.dll`, `wininet.dll`,
`plugins/MGSHDFix.asi`; both packs' corresponding
`plugins/MGS*-Community-Bugfix-Compilation.asi`; M2 `dinput8.dll`, `d3d11.dll`,
`MGSM2Fix64.asi`, `MGSM2Fix32.asi`, `MGSM2Fix.ini`. Neither HD archive ships a
`.settings` file; both ship `plugins/MGSHDFix Config Tool.exe`. No path migration
was observed, but the same paths replace existing bytes. Root M2 `d3d11.dll`
belongs to MGS1; HD's deletion advice concerns the separate MGS2/MGS3 folders.
Do not conflate them or remove unowned third-party DLLs.

Immutable README installation/load-order sources are recorded in queries.json.
HD directs extraction into the game folder, removal of old HD files and
`d3d11.dll` before updates, launcher resolution/upscaling set to Original, and
Config Tool use. Its Proton override remains `wininet,winhttp=n,b`.
M2 directs extraction into MGS1 and Proton overrides `dinput8=n,b;d3d11=n,b`.
Both compilations recommend HD, then Better Audio, then base compilation, then
optional additions. The kit's order agrees. AI addons stay excluded; the MGS3
optional 4K addon was not inspected or proposed.

The compilation archives contain audio replacements: six MGS2 `.sdt`/`.xxs`
paths under `us/demo`/`us/movie`, and three MGS3 `.sdt` paths under `fr/codec`.
`rg '\.(sdt|sdx|xxs)$' <cache>/*.files.txt` → exit 0 listed those nine paths.
Thus audio overlap is a real ordering concern, even though HD/base intersections
are empty. No Nexus archive was obtained; exact Better Audio intersections and
playback remain unverified. The compilation INIs expose only update-notification
flags, shipped true; the kit's M2/HD update suppression should not be assumed to
suppress these independent flags.

No dedicated removal procedure was established in the inspected READMEs.
The kit's tracked-file restoration is its own policy, not proof of upstream
uninstallation. Existing user files must be backed up/preserved during any
future replacement. Large audio originals can require Steam verification;
Steam verification can also replace compilation files, so repair/load-order
verification is part of the hardware check. M2's fullscreen-optimization registry
handling exists in both inspected source versions (`git grep -n DISABLEDXMAXIMIZEDWINDOWEDMODE v3.6`
→ exit 0, `src/mgs1.cpp`; candidate `src/m2fix/m2utils.cpp`). Its shipped flag is
false; opted-in registry state is outside the kit's game-file manifest and needs
separate removal assessment, not a claim of a new regression.

### Exact settings comparison

Official HD source checkouts: shallow clone at 4.1.2 and fetches of 4.1.0 and
4.1.1 → exit 0. Official M2 clone at v3.7.3 and fetch of v3.6 → exit 0.
`git show <tag>:ConfigTool/tab_data.cpp` and
`git show <tag>:src/resources/config_keys.hpp` supplied the compared HD sources.
Exact commits and file SHA-256s are in `attachments/schema-delta.json`.

At `cab17ae5a1ab7211cd46a65c20e0b5f3ab0cb9db`,
`python3 docs/rounds/004-mod-compatibility-audit/attachments/inspect_schema.py <source>/MGSHDFix <scratch>/schema-review <scratch>/rederived-schema.json`
→ exit 0: `baseline_fixture_equal: true`; 4.1.0 and 4.1.1:
`27 sections, 128 reviewed union keys`; 4.1.2:
`27 sections, raw_keys: 128, reviewed_union_keys: 131, flag_alias_substitutions: 3`.
The whole 4.1.0 capture equals `tests/fixtures/hdfix-4.1.0-schema.json`.

The old parser silently excludes three existing fields when 4.1.2 puts them
behind `kFirstPersonViewGameFlags`. Both conditional alias declarations include
MGS2. The attachment helper asserts those declarations and normalizes only
scratch text to the MGS2/MGS3 union; baseline capture code remains unchanged.
This explains why raw count equality is misleading. Static union extraction is
not an actual generated, per-game settings export.

Exact Boolean additions under `[Bugfixes]`:
`Fix Dropped Item Toss`, `Fix Emissive Textures`, `Fix Lighting Bounding Boxes`.
Under `[Model Quality && Level of Detail Enhancements]`,
`Show Soft Particles` is replaced by `Blend Particle Effect Sprites`.
Source defaults switch that particle setting from true to false; the three new
bugfix declarations default true. No common-key type changes or differences in
captured explicit choices/known integer bounds were observed.

For example `[System Specific Fixes] Audio Output Mode` retains exactly
`Stereo (2.0)` and `Surround Sound (5.1)`;
`[Controller Settings] Set Menu OK && Cancel Button` retains
`Default`, `East for OK`, `South for OK` (now applicable to MGS3 as well).
Captured bounds remain window/render dimensions 0..16384, rumble 0..200,
anisotropic filtering 0..16, caption size 1..100 and opacity 0..100.
Kit button choices remain `Steam Deck`, `Xbox One`, `PlayStation 5`,
`PlayStation 2`, `PlayStation 4`, `Nintendo Switch`, `Keyboard / Mouse`;
the helper does not exhaustively verify the dynamic button/language/hotkey
choices or float bounds. Those require actual candidate exports and UI checks.

The kit still emits `Show Soft Particles=1` and lacks the three new bugfix keys.
Candidate `src/resources/config.cpp` reads these candidate keys and its missing
key/parse error path invokes `FatalConfigError`, logging the Config Tool advice
and calling `FreeLibraryAndExitThread(baseModule, 1)`. This establishes unsafe
mod configuration initialization after a numeric-only bump; it does not prove
that the whole game process exits. Immutable source:
`https://github.com/ShizCalev/MGSHDFix/blob/33e80bf4d2223f6866b0b92e06c3c9b85efab652/src/resources/config.cpp`.

Both M2 INIs are byte-identical (SHA-256 in archives.json), ten sections and
31 keys; exact names/defaults are in `attachments/m2fix-ini.json`.
`[Launcher] StartGame=false` and `[Update Notifications] CheckForUpdates=true`
remain addressable by the kit's existing patcher, which disables update checks
and sets StartGame to the user's launcher choice. Gameplay/debug/stage-select
options are not enabled by the proposed audit. INI equality does not cover
compiled runtime behavior or existing custom settings.

### Local validation

All commands below ran at `cab17ae5a1ab7211cd46a65c20e0b5f3ab0cb9db`:

- `python3 -m pytest tests/ -q` → exit 0: `203 passed in 9.73s`.
- `python3 -m ruff check .` → exit 0: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py` → exit 0, no output.
- `python3 tools/fw.py check` → exit 0: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status` → exit 0: framework pinned/latest 3.1.0;
  `owner-approves`; round 004 in flight; Worker started, no report yet;
  Verifier not started; `all project checks pass`; one unpushed audit commit.
  Its personal-path cleanup suggestion is omitted here. This was the actual
  pre-report state, not a claim of final delivery freshness.
- `python3 tools/check_pins.py` → exit 1:

```text
[UPDATE] MGSHDFix (MGS2/MGS3)                   pinned 4.1.0  ->  4.1.2
[  ok  ] MGS2 Community Bugfix Compilation      pinned 3.0.0
[  ok  ] MGS3 Community Bugfix Compilation      pinned 2.0.1
[UPDATE] MGSM2Fix (MGS1)                        pinned v3.6  ->  v3.7.3

2 update(s) available. These are NOT drop-in bumps — read docs/UPGRADING.md before changing anything.
```

This is a successful advisory query reporting updates, not a network or code
failure. It was inspected before execution and authorizes no pin change.

### Published report and CI evidence

- `python3 tools/fw.py report --role worker --round 004-mod-compatibility-audit --push`
  → exit 0: `report committed: docs/rounds/004-mod-compatibility-audit/worker.md at 5993e5c66935; it describes cab17ae5a1ab on worker/004-mod-compatibility-audit`;
  `pushed worker/004-mod-compatibility-audit to origin`.
- `python3 tools/fw.py delivery --round 004-mod-compatibility-audit` → exit 0:
  `origin/worker/004-mod-compatibility-audit (5993e5c66935): delivered`;
  `worker: report describes cab17ae5a1ab (written 2026-10-03T19:12:21Z on macOS 27.0)`.
- `gh pr create --base main --head worker/004-mod-compatibility-audit --title <audit-title> --body-file <scratch>/pr-body.md`
  → exit 0: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/7`.
  PR is an audit review candidate; it has not been accepted or merged.
- `gh workflow run ci.yml --ref worker/004-mod-compatibility-audit` → exit 0:
  `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37147081459`.
- `gh run view 37147081459 --log` → exit 0. Each of four checkout logs prints
  literal `5993e5c6693566c56289e59dcfc25a13d7d36d3f` after
  `git log -1 --format=%H`. Linux 3.9: `203 passed in 5.53s`;
  3.11: `203 passed in 5.41s`; 3.12: `203 passed in 4.59s`;
  Windows 3.12: `201 passed, 2 skipped in 16.83s`.
  All three Linux lint steps print `All checks passed!`; compilation and
  desktop-file validation steps succeed. `gh run view 37147081459 --json status,conclusion`
  → exit 0: `status: completed; conclusion: success`.
- `gh run view 37147068769 --log` → exit 0. PR run checkout logs instead print
  synthetic merge `3f594eac14637745871b17ded7a512729164b7be` in all four jobs,
  merging the report head into main. Linux 3.9/3.11/3.12: respectively
  `203 passed in 5.62s`, `203 passed in 6.25s`, `203 passed in 4.62s`;
  Windows: `201 passed, 2 skipped in 25.02s`. Linux lint, compilation and
  desktop validation succeed. `gh run view 37147068769 --json status,conclusion`
  → exit 0: `status: completed; conclusion: success`.
  Metadata headSha is not being presented as the PR checkout identity.

This appended evidence changes only the report. The report is being restamped
and pushed after this addition; its generated stamp gives that delivery commit.
CI on that final stamp will be inspected and recorded on PR #7 without moving
this branch again. The independent Verifier must review the final stamped
commit rather than carrying an earlier review forward.

## Not verified

No licensed game boots, Config Tool exports, native GUI rendering, controller
behavior, Deck performance, audio playback or hardware removal/repair tests.
No downloaded binary was run. Exact current Konami build compatibility is not
established by upstream's game-title support statements or the offline tests.
No exhaustive supported-game-patch matrix was established in the inspected
release notes/READMEs. No Nexus payload was obtained, redistributed or inspected.
Archive listing proves paths, not correct data or execution. Existing
"known-good" descriptions cover the pinned synthetic schema/checksum/transaction
checks; they must not be interpreted as licensed Windows/Deck boot evidence.
The CI evidence above concerns the named literal report commit and named PR
merge commit. It does not establish real-machine compatibility.

## Changed

- This round's `worker.md`: assessment, evidence, recommendation and limitations.
- `attachments/releases.json` and `queries.json`: compact official identities,
  dates, commands, URLs and source hashes.
- `attachments/archives.json` and `inspect_archives.py`: compact static download,
  hash, path and intersection evidence with a reproducible inspection command.
- `attachments/schema-delta.json` and `inspect_schema.py`: exact source delta
  and explicit flag-alias/parser limits; no production parser change.
- `attachments/m2fix-ini.json`: exact shipped M2 section/key/default comparison.

No installer, pins, shortcuts, tests, framework, guidance or product documentation
changed. The Brain-authored brief was already on the selected seat. Main and
other seats were preserved. No merge, tag, publication or issue closure.

## Open questions

Keep all four pins now. A subsequent brief could propose one coordinated slice:
HD 4.1.2 plus unchanged MGS2 3.0.0, MGS3 2.0.1 and M2 v3.6. The relevant HD fixes
justify investigating that slice; M2 v3.7.3 should remain deferred until a
Volume 1 benefit and compatibility evidence justify its additional runtime
change. Re-query stable releases at that future round's start.

Named prerequisites for that future slice:

1. Obtain actual 4.1.2 Config Tool exports for MGS2 and MGS3; compare every exact
   name/type/default/allowed value, including dynamic choices and build flags.
   Repair the capture helper's alias handling in that separately authorized
   round; preserve custom settings and migrate the renamed particle key with
   an explicit policy rather than silently adopting upstream defaults.
2. Couple template, schema fixture, constraints, pin and checksum changes;
   retain all gameplay-altering toggles disabled. Validate fresh install,
   reset then explicit choices, preservation, repair, cancellation rollback,
   review/manifest agreement and removal against those exports.
3. Re-audit ownership of obsolete loaders and replaced files; do not implement
   upstream's broad DLL deletion advice blindly. Confirm saves/backups and
   user mod files survive; state exactly which audio originals require Steam
   verification and which runtime-created/registry files are outside removal.
4. On licensed Windows and Deck/Proton machines, record game build and Proton
   version; boot MGS1 with both launcher choices and MGS2/MGS3 with PS2 buttons,
   stereo/5.1 and default/custom render sizes. Test relevant cutscenes, DS3
   throwing, frame pacing and Deck performance. With owner-supplied audio,
   verify base-last replacements, conversations/music and repair/removal.
5. Independently verify this audit at its stamped commit before Brain acceptance.
   A green audit PR is documentation evidence, not approval to upgrade or merge.
