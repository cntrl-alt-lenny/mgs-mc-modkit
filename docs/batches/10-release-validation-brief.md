# 10-release-validation

Path: Checked. Game, GUI, audio and restoration behavior cannot be established
by the offline suite. Worker, Verifier, then Brain; release remains a separate
owner decision. Candidate: `15d9277196e7bd1cfbd45fe280a230050b276bed`.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 10-release-validation · Worker

Start with python3 tools/fw.py status, then read AGENTS.md, the framework,
your role card, docs/state.md and docs/RELEASING.md. Use the isolated
.worktrees/worker-10-release-validation checkout and worker/10-release-validation.

Establish whether kit 2.3.0 at literal candidate commit
15d9277196e7bd1cfbd45fe280a230050b276bed meets the release checklist. Keep
installer, shortcuts, mod pins, schema and release version unchanged. Do not
tag, publish, merge, modify repository settings or redistribute Nexus audio.

Run the offline suite, Ruff, compilation and framework hygiene. Independently
verify both shortcuts' SHA-256/tag and Windows CRLF. Inspect CI checkout logs
at the candidate SHA. Record actual commands, output and exit codes, host OS,
Python and the commit each check used; distinguish CI from hardware results.

Inventory available validation hosts without opening unrelated chats or
reading credentials. This chat has a macOS shell and no configured SSH.
Brain is asking the owner about Windows/Deck availability; do not invent
access or treat installed synthetic fixtures as games. Send technical issues
to Brain. Do not modify existing game installations without a preserved,
reviewable baseline and agreed access.

Create a resumable results matrix for every docs/RELEASING.md smoke check:
fresh install, all three game boots, settings change/repair/preservation,
removal/stock boots, Deck launch options/audio/cancellation/GUI/logs,
large-audio Steam verification and repeat removal, and concurrent-installer
refusal. Record hardware, game builds, pins, payload identity and observations
for actual runs. Missing hardware/payloads mean NOT RUN with the dependency.

Commit docs/batches/10-release-validation.md with Done, Checked, Not checked,
Failed or blocked; keep prose under 500 words and raw evidence in attachments.
Retain unavailable checks as blocked, never release-ready. Push your branch
and report the exact delivery commit. Production fixes need a separate batch.
```

## Verifier prompt

Send this only after the Worker finishes.

```text
MGS Master Collection Mod Kit · BATCH 10-release-validation · Verifier

Start with python3 tools/fw.py status and read AGENTS.md, the framework and
your role card. Brain supplies the literal Worker delivery SHA. Review its
diff before the summary. Independently check candidate identity, CI checkout
evidence, shortcut pins and representative checks. Judge every smoke-test row
as met, not met or cannot tell; synthetic tests cannot establish hardware
behavior. Report unsupported claims and missing dependencies. Change only
docs/batches/10-release-validation-review.md on the Worker's branch, state the
reviewed SHA and actual command results, push, and return the delivery SHA.
Never approve release, merge, tag or edit production code.
```
