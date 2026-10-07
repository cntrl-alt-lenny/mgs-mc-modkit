# 10-release-validation

## Done

Prepared durable readiness evidence for kit 2.3.0 at candidate
`15d9277196e7bd1cfbd45fe280a230050b276bed`. Production files, pins, schema,
shortcuts and release version remain unchanged. A read-only shortcut check and
[resumable smoke matrix](evidence/10-release-validation/smoke-matrix.md) record
the prerequisites and every real-machine release scenario.
Added a portable [access update](evidence/10-release-validation/access-update.md)
after Verifier review, recording owner authorization and Brain's observations.

## Checked

On Darwin/macOS with Python 3.9.6, candidate code passed 273 offline tests,
Ruff, compilation of `tools/fw.py`/`install.py`, and framework hygiene (zero
errors/warnings). Both shortcuts pin `v2.3.0` and installer SHA-256
`a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`;
Windows shortcut has CRLF only, Python and desktop files have LF only.
Commands, outputs and exit codes are in
[local-checks.txt](evidence/10-release-validation/local-checks.txt).

[Candidate CI run 37525559856](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37525559856)
succeeded. Checkout logs explicitly show the candidate SHA in all four jobs.
Linux Python 3.9/3.11/3.12 each passed 273 tests, lint, installer compilation
and desktop validation. Native Windows Python 3.12 passed 271 tests and
skipped two tests; the candidate's skip decorators identify privileged
symlink creation as the reason. CI does not prove game or GUI behavior.
[CI excerpts](evidence/10-release-validation/ci-excerpts.txt) and
[original job metadata](evidence/10-release-validation/ci-run.json) retain
checkout/results and step conclusions. Remote per-command exit values are
not separately exposed by those logs.

## Not checked

All real Windows/Deck game installs, three-title modded/stock boots,
settings preservation, native GUI/cancellation, Proton options, actual
upstream archives, user-supplied audio, large-audio Steam restoration and
concurrent-installer refusal remain NOT RUN. Hardware/game builds/payload
identities are unknown. Desktop validator is unavailable locally; candidate
Linux CI covers it. Static shortcut matching does not verify runtime downloads:
latest published is 2.2.0 and v2.3.0 is unavailable (see
[release queries](evidence/10-release-validation/discovery-and-release.txt)).
Resume with the exact candidate's local installer. No release/tag workflow ran.

## Failed or blocked

**Release readiness is BLOCKED** on working host access, licensed games,
user-supplied audio and a preserved baseline. Owner authorizes installing
missing licensed titles through Steam's default library on the Windows PC.
Brain's existing Moonlight connection still reports that PC Offline after
Wake PC; no Windows/Steam session was reached. Deck is currently unavailable
per owner. Brain is resolving access. No game installation was changed. Two filename
discovery probes used absent filenames before correcting to `.cmd` and
`tests/test_safe_extract.py`; they were not failed candidate checks.
Framework status also flags unrelated recovery work and linked seats; those
were preserved and reported to Brain. This batch supplies evidence for
independent review, not release approval.
