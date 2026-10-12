# Batch 24: MGS4 Windows native validation

Checked path: native compatibility and restoration require device evidence. Windows owns this batch; Deck owns Batch 25. Neither depends on the other's completion, planning-document merge or code-merge approval. Both use the reviewed candidate; release remains separate.

```text
MGS Master Collection Mod Kit · BATCH 24-mgs4-windows-native · Worker

Start with python3 tools/fw.py status (py -3 on Windows if needed), read AGENTS.md, framework/Worker card, docs/state.md, docs/RELEASING.md and docs/batches/evidence/14-mgs4-patriotfix/native-handoff.md. Fetch origin and create an isolated worker/24-mgs4-windows-native seat from exact candidate 2844fa25cfda89301def7996a93a2ab6f2dec403. Read the latest MGS4 review before testing. Own only docs/batches/24-mgs4-windows-native.md and its evidence directory; preserve historical Batch 10 evidence. No production, pins, shortcuts, framework or other-seat changes.

Establish whether the candidate works on an actual Windows host with licensed Steam games. Record host availability first. If hardware/access/games are unavailable, record the exact dependency and stop; do not substitute Mac or fixture results. Preserve and hash saves, originals, settings and recovery records before installation; exercise destructive failure cases only in disposable copies. Run the checkout directly with py -3 install.py; v2.3.0 is unpublished.

Follow the native handoff: capture real PatriotFix 0.2.2 Config Tool exports and compare all 28 fields, hidden values, types, choices, defaults and line endings; test review/change-settings/cancel, fresh installation, Steam launcher skipping on/off, ASI logs, gameplay/cutscenes/focus loss/flashback where accessible, custom-settings repair, removal and stock boot. Retest available MGS1–3 boots with shipping pins. Record independent mouse values and oldest-backup/save hashes. DS3, inaccessible scenes and missing user-supplied audio are NOT RUN, never guessed; do not redistribute audio.

Run full tests, Ruff, compilation, framework hygiene, embedding parity and both shortcut tag/hash checks at the tested SHA. Commit a sub-500-word Done/Checked/Not checked/Failed or blocked summary plus commands/exits, exports, logs and observations. Keep personal paths and saves out of Git. Report concrete failures to Brain; do not patch them. Push and return candidate/delivery SHAs. No acceptance, merge, tag or publication.
```

Send the Verifier prompt only after this Worker finishes, with its literal delivery SHA supplied by Brain; no need to wait for Batch 25.

```text
MGS Master Collection Mod Kit · BATCH 24-mgs4-windows-native · Verifier

Start with framework status and read AGENTS.md and your card. Review the literal Worker delivery SHA supplied by Brain in an isolated seat, diff before summary. Independently authenticate candidate, exports, game builds, logs, hashes and every native result; distinguish observed behavior from fixtures, CI and unavailable checks. Check preservation and restoration claims against before/after evidence. Change only docs/batches/24-mgs4-windows-native-review.md; record actual commands/exits, findings and reviewed SHA, commit/push and return review SHA. No production edits, acceptance, merge or release.
```
