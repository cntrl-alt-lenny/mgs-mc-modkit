# Windows / Steam Deck handoff — NOT RUN on this Worker seat

Use Brain's literal delivery SHA and retain exact installer/settings hashes,
hardware/OS/Proton details, Steam builds, mod pins, commands, outputs and exits.
Never infer initialization from installer completion or ASI injection alone.
No release authorization follows from this handoff.

1. Preserve existing saves, userdata, settings, originals/backups and recovery
   records privately, with byte inventories before any write. Keep licensed games
   and Steam verification available. Close games; confirm no interrupted journal.
2. Authenticate official MGSHDFix 4.1.0 archive against the unchanged kit checksum.
   In separate test copies for MGS2 and MGS3, launch the pinned Config Tool,
   save fresh settings and capture the files. Compare exact sections/keys/types
   and all three MG-only defaults to the fixture, not UI visibility or counts.
   Retain language/controller/hotkey choices and distinguish defaults from kit
   overrides. This Worker audited source saving behavior, not native exports.
3. Fresh install with the exact candidate installer. Capture settings, manifest,
   archive hashes and launcher/game logs. Start MGS2 and MGS3 through launcher
   and boot-straight choices. Require completed MGSHDFix configuration parsing,
   no missing-key consoles, rendered title and playable/save-loading scenes.
   Diagnose independent stock failures separately; do not label them fixed.
4. Prepare complete legacy 128-key kit settings with independent custom language,
   resolution, hotkey, buttons and launcher preferences. Repair each game without
   resetting. All original supported preferences must survive, three default
   fields must appear, and updates must stay off. Compare saves/original backups
   and recovery records. Also repair a complete new file with custom MG1/MG2
   choice/booleans and exercise an explicit option change and explicit reset.
5. Negative cases: missing original key, partial new-key presence, invalid choice,
   duplicate/unknown key and malformed value must refuse before replacement;
   prove settings/save/backup bytes remain unchanged. Do not delete interrupted
   recovery records to bypass an error. Test cancellation rollback and lock
   refusal on real hardware; retain failed attempts.
6. Repeat initialization/playable observations after repair. On Deck confirm
   Proton launch options and use installed language packs; capture per-game
   native exports via Proton where supported. Optional audio remains separate
   and user supplied, and is not needed to prove this schema correction.
7. Remove through the installer, compare saved inventories and stock starts.
   Original large audio without permanent backup needs Steam verification then
   a second removal; do not claim exact restoration without byte evidence.

All native exports, Windows/Deck fresh/repair/boot/gameplay/removal tests above
remain NOT RUN for batch 11. Batch 10 observations belong to its earlier
candidate and are evidence of the defect, not validation of this correction.
