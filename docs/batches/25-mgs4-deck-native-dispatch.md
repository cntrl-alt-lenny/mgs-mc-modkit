# Batch 25: MGS4 Deck native validation

Checked path: Proton/gameplay and restoration require real-device evidence. Deck owns this batch; Windows owns Batch 24. There is no dependency between their runs; target availability is the only prerequisite for native testing. Both pin the same reviewed candidate.

```text
MGS Master Collection Mod Kit · BATCH 25-mgs4-deck-native · Worker

Start with python3 tools/fw.py status, read AGENTS.md, framework/Worker card, docs/state.md, docs/RELEASING.md and docs/batches/evidence/14-mgs4-patriotfix/native-handoff.md. Fetch origin and create an isolated worker/25-mgs4-deck-native seat from exact candidate 2844fa25cfda89301def7996a93a2ab6f2dec403. Read the latest MGS4 review before testing. Own only docs/batches/25-mgs4-deck-native.md and its evidence directory. No production, pins, shortcuts, framework or Windows-seat changes.

Establish whether the candidate works on an actual Steam Deck with licensed games. Record availability, SteamOS/hardware, Proton version and game builds first. If the device, access or games are missing, record that dependency and stop; Mac fixtures cannot establish Proton compatibility. Preserve and hash saves, originals, settings, recovery records and existing launch options before installation. Use disposable copies for interrupted/cancelled-write tests. Run python3 install.py from the candidate checkout; the v2.3.0 release asset is unpublished.

Follow the native handoff for internal/secondary-library discovery, manual root selection, readable GUI/controller interaction, review/change-settings/cancel, installation, WINEDLLOVERRIDES="winmm=n,b" %command%, Steam boot, launcher skipping on/off, ASI logs, accessible gameplay/cutscenes/focus loss, Config Tool exports through ProtonTricks, custom-settings repair, removal and stock boot. Compare settings, save/original hashes and oldest backups before/after. Retest available MGS1–3 with their existing launch requirements. Preserve unrelated launch-option arguments. DS3, inaccessible flashback scenes and missing user-supplied audio remain NOT RUN; do not redistribute audio.

Run full tests, Ruff, compilation, framework hygiene, embedding parity and both shortcut tag/hash checks; use desktop-file-validate where available. Commit a sub-500-word Done/Checked/Not checked/Failed or blocked summary and actual commands/exits, exports, logs and observations. Keep personal paths and saves out of Git. Report failures to Brain without production patches. Push and return candidate/delivery SHAs. No acceptance, merge, tag or publication.
```

Send the Verifier prompt only after this Worker finishes, with its literal delivery SHA supplied by Brain; no need to wait for Batch 24.

```text
MGS Master Collection Mod Kit · BATCH 25-mgs4-deck-native · Verifier

Start with framework status and read AGENTS.md and your card. Review the literal Worker delivery SHA supplied by Brain in an isolated seat, diff before summary. Independently authenticate candidate, Proton/device/game identities, Config Tool exports, ASI/game logs and preservation/restoration hashes. Judge every goal as observed, failed or unavailable; CI and synthetic checks cannot prove native loading or gameplay. Change only docs/batches/25-mgs4-deck-native-review.md; retain actual commands/exits, concrete findings and reviewed SHA, commit/push and return review SHA. No production edits, acceptance, merge or release.
```
