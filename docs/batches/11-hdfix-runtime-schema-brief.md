# 11-hdfix-runtime-schema

Checked: settings migration and runtime compatibility require independent review.
Send the Worker now; send the Verifier only after Brain supplies the literal
Worker delivery SHA. Both seats may prepare work on macOS; native checks remain
separate dependencies.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 11-hdfix-runtime-schema · Worker

Start with python3 tools/fw.py status. Read AGENTS.md, the framework,
your Worker card, docs/state.md, UPGRADING.md and RELEASING.md under docs/.

Use worker/11-hdfix-runtime-schema from latest main, in an isolated
.worktrees/worker-11-hdfix-runtime-schema checkout. Preserve other seats.
This seat runs on an M1 MacBook Pro; do not assume Windows/Deck access.

Read batch 10 evidence at
9a8d98661b40d702f0e9a43248f01d5b385c67d1.
Establish why MGSHDFix 4.1.0 requires MSX Skip Launcher Game in
Launcher and Splashscreens while our template/schema omit it. Authenticate
pinned source identity; examine Config Tool saving and runtime readers.
Audit every required field, including game-filtered omissions. Do not guess
defaults or fix only the first missing key.

Implement evidence-supported corrections to template, schema, constraints,
fixture and capture tooling/guidance. Preserve bounded source capture.
Add regressions exposing the omission and verifying complete requirements.
Safely migrate existing kit-generated settings while preserving supported
custom preferences and malformed-edit refusal. Protect saves, originals,
backups and recovery records. Correct affected unsupported compatibility claims.

Keep mod versions/checksums and unpublished kit version 2.3.0 unchanged.
No MGS4 integration, upstream upgrade, GUI redesign or framework update.
Regenerate both shortcut hashes with tools/pin_shortcuts.py; independently
verify tags/SHA256, Windows CRLF and Python/desktop LF.

Run python3 -m pytest tests/ -q; python3 -m ruff check .;
python3 -m py_compile tools/fw.py install.py; framework check/status;
relevant UPGRADING checks; desktop validation where available.
Record exact commits, commands, real output, exit codes and host details.

Unavailable native exports/boots remain NOT RUN. Identify any correction
that depends on unavailable evidence instead of inventing it. Prepare a
Windows/Deck handoff for exports, fresh install, repair/preservation,
MGS2/MGS3 initialization, gameplay and removal/restoration.

Commit docs/batches/11-hdfix-runtime-schema.md with Done, Checked,
Not checked, Failed or blocked; under 500 prose words, evidence in attachments.
Push, open a draft PR and return the literal delivery SHA. Technical questions
go to Brain. Never approve, merge, tag or publish.
```

## Verifier prompt

```text
MGS Master Collection Mod Kit · BATCH 11-hdfix-runtime-schema · Verifier

Start with python3 tools/fw.py status; read AGENTS.md, framework, your card
and this brief. Brain supplies the literal Worker delivery SHA before dispatch.
Check out that SHA in an isolated seat; read the diff before the summary.

Independently derive pinned runtime settings requirements and defaults from
authenticated upstream sources/exports. Challenge game filtering and fixture
assumptions. Review migration, malformed-edit refusal and preservation.
Re-run required checks and independently verify shortcut pins/line endings.
Distinguish reviewed hardware evidence from independently observed results;
missing native exports/boots remain unproven. No release approval follows.

Change only docs/batches/11-hdfix-runtime-schema-review.md on the Worker
branch: reviewed SHA, commands/results, each goal's judgment, findings and
verdict. Findings need severity, file/line and a concrete failure path.
Keep prose under 500 words. Commit, push and return the review SHA.
Never edit production, approve, merge, tag or publish.
```
