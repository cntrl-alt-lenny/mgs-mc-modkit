# 14-mgs4-patriotfix

## Done

Built from main `67d1406` after Brain confirmed batch 11 merged; followed brief
`a1c9264b2ba803a0f05774bd3bc60dcdcbe013d2`. Implemented MGS4 discovery/manual
root selection, game choice, upfront settings, official pinned PatriotFix 0.2.2,
repair, removal and individual game outcomes. Authenticated Steam app 2492670,
root/executable/save layout, tagged source and independently hashed archive.
[Source review](evidence/14-mgs4-patriotfix/source-review.md) records derivation.

One transactional settings writer validates all 28 fields, hidden PW controls,
choices, types, numeric bounds and language pairs. Capture checks exact Git tree,
58 source-file hashes/inventory and all runtime readers independently of kit
settings. Conservative defaults preserve rendering/frame-rate behavior; explicit
visual changes are optional. Supported custom values survive; updates stay off.

Wrong payloads/destinations, unmanaged competing loaders, duplicate ASIs and
unsafe records refuse. Saves/game executables are protected; oldest backups,
pre-run snapshots, locks, cancellation and per-game commits remain intact.
Runtime log placeholders are skipped. MGS1–3 definitions/pins/behavior remain
unchanged; no PW/audio/FPS/ClarityFix/flashback component added. Guidance and
AGENTS scope updated; unpublished version stays 2.3.0, both shortcuts regenerated.

## Checked

Mac arm64 / Python 3.9.6: **314 tests**, Ruff, compilation, framework check/status,
Python 3.9 grammar, both shortcut hashes/tags/line endings, unchanged MGS1–3 pins
and comparison with immutable framework 4.0.0 pass. 31 MGS4 tests exercise source
completeness/refusal, destination/payload refusal, malformed settings,
preservation/reset, oldest backups, rollback/recovery, locks, cancellation,
mixed outcomes and removal. [Commands/output/exits](evidence/14-mgs4-patriotfix/checks.txt)
state checked implementation/evidence commits. Actual source capture equals the
committed fixture; two independent hashes match the official downloaded archive.
All five live archive checksums match.
Actual PatriotFix ZIP extraction/transaction/removal passes in a disposable
unlicensed game fixture; no Windows binaries were run.

## Not checked

Native Windows/Deck Config Tool exports, GUI rendering, ASI initialization,
licensed boots/gameplay, DS3, flashback behavior and real repair/removal are
**NOT RUN**. [Native handoff](evidence/14-mgs4-patriotfix/native-handoff.md) records
fresh install, settings/export/boot, repair, cancellation/recovery, mixed games,
locks and removal. Desktop validation is unavailable on this Mac.
Independent Verifier/Brain disposition and owner-approved release remain separate.

## Failed or blocked

Initial test expectations miscounted fields and misread uninstall's success flag;
corrected. Independent evidence helper initially mishandled existing URL
f-strings; corrected. Saved status/traceback account paths failed document hygiene;
normalized portable evidence, preserving commands/results/exits. Initial Windows
CI found backslash/POSIX mismatch in the capture inventory; fixed with as_posix.
Reruns pass;
[attempts](evidence/14-mgs4-patriotfix/attempts.txt) and logs retain failures.
No approval, merge, tag or publication performed.
