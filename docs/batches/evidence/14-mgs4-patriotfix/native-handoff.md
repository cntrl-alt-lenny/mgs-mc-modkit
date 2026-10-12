# Batch 14 Windows / Steam Deck handoff

Candidate: use the literal Worker delivery SHA supplied with the draft PR.
Unpublished kit 2.3.0; MGS1–3 pins unchanged, MGS4 PatriotFix 0.2.2.
All native checks below are **NOT RUN** on the Mac arm64 development seat.
Record exact SHA, OS/hardware, Steam game build, mod versions, commands/exits,
settings exports, game/mod logs and screenshots. Source and offline evidence do
not establish native loading, gameplay or exact real-machine restoration.

1. On an isolated checkout at delivery SHA run offline tests, Ruff, compilation
   and both shortcut checks. Use `py -3` on Windows if needed. Run the candidate
   directly with `py -3 install.py` / `python3 install.py`; the release asset for
   2.3.0 is unpublished. Do not tag or publish.
2. Close Steam downloads and games. Make a separate backup of licensed saves,
   game originals, current mod settings and recovery records. Identify Steam app
   2492670, root `METAL GEAR SOLID 4`, `MGS4/mgs4.exe`,
   `Launcher/launcher.exe`, and `mgs4_savedata_win`. Snapshot file hashes outside
   reviewed mod destinations so changes to originals/saves can be detected.
3. Fresh install: validate internal/secondary library discovery and manual root
   selection; selecting `MGS4/` alone, mixed PW layout, links and conflicting
   manual loaders must refuse. Confirm correct stable official MGS4 archive/hash,
   game/launcher ASIs/loaders and root settings, with no savedata/asset edits.
4. Before installing, exercise Change settings and cancel at review. Confirm no
   game mutation. Then install conservative defaults: original blur/dynamic
   resolution/shadows, filtering 8, pause-on-focus-loss on, AUTO buttons,
   eu/en, skipping launcher/in-game logos, update checks off. No FPS unlocker.
5. Open the shipped 0.2.2 Config Tool, export/save, and compare all 28 exact keys,
   hidden PW fields, types, choices, language codes and values against source.
   Preserve the before/after exports. Check CRLF, Float formatting and independent
   mouse sensitivity values. Config Tool may write Windows fullscreen compatibility
   registry flags; record these separately (the kit doesn't manage them).
6. Windows: boot through Steam with launcher skipping enabled and disabled; boot
   direct game as supported upstream. Verify both ASI loads and logs, gameplay,
   cutscenes, focus loss and MGS1 flashback. Change one explicit visual override
   and demonstrate the effect, then return to conservative settings. Test DS3 only
   if available; install drivers separately, per upstream, and record NOT RUN if not.
7. Deck/Linux: use `WINEDLLOVERRIDES="winmm=n,b" %command%`. Verify Steam boots,
   launcher skipping, Config Tool through ProtonTricks, GUI legibility and controls.
   Optional DS3 setup uses upstream's extended launch option and controller order;
   the kit neither installs drivers nor enables it by default.
8. Repair: customize supported language/buttons/mouse sensitivity/visual/hidden PW
   values. Verify all custom values survive except update checks remain off, and
   oldest original backups stay byte-identical. Malformed/missing/unknown keys,
   non-finite floats or invalid language pairs must refuse without replacement.
   Verify explicit reset is separate and accurately previewed.
9. Cancel extraction/writing; simulate interrupted repair in a disposable copy.
   Confirm pre-run setup restored, saves/originals unchanged, failed recovery keeps
   journal/snapshots/backups, and a second process lock refuses. Do not corrupt live
   licensed saves to test these paths.
10. Mixed MGS1–4 run: fail/cancel a later game after an earlier commit; confirm
    individual results and earlier success preserved. Boot MGS1–3 with unchanged
    pins/configuration. Static regression tests do not establish these boots.
11. Remove: fresh and repaired candidates must remove tracked files, restore
    oldest backed originals, preserve game/save hashes and leave runtime logs.
    Native game boots stock afterward. Missing/corrupt records must refuse/retain
    backups and report action required; do not delete them manually to get green.

Send evidence to Brain for independent disposition. Unavailable tests remain
NOT RUN. No acceptance, merge, tag or publication is implied by this handoff.
