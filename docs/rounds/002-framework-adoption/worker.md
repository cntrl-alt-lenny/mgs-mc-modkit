<!-- fw-report
round: 002-framework-adoption
role: worker
branch: worker/002-framework-adoption
head: 615a7f3ecf53f95299f8e02ecd78f2488d940149
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T16:52:37Z
-->
# Worker report: 002-framework-adoption

## Verified

Evidence below was run at implementation commit `615a7f3ecf53f95299f8e02ecd78f2488d940149` unless identified
as bootstrap evidence. Absolute bootstrap directories are replaced with
`<framework>` and `<seat>` to keep this record portable; output is otherwise
retained. The seat was isolated under `.worktrees/worker-002`, initially at
`origin/main`; external start selected the Brain brief and Worker branch.

Bootstrap commands (each exit 0):

```text
git -C <framework> rev-parse HEAD
eca1306dc43cb81f0df3ee42f841812da68e8b1e

python3 <framework>/tools/fw.py --cwd <seat> start --role worker --round 002-framework-adoption
seat ok: worker, round 002-framework-adoption, branch worker/002-framework-adoption at 37df03e79dd1
  brief: docs/rounds/002-framework-adoption/brief.md
  finish with: write docs/rounds/002-framework-adoption/worker.md, then python3 tools/fw.py report --role worker --round 002-framework-adoption --push
```

The clean temporary clone used `git clone --branch v3.1.0 --depth 1` from the
framework repository named in the brief. The annotated tag resolved to the
commit above. Read the entire pinned `framework/FRAMEWORK.md` and all three
role cards before adoption.

Adoption dry run: `python3 <framework>/tools/adopt.py <seat> --project "MGS Master Collection Mod Kit" --workers worker --verifier --dry-run` → exit 0.

```text
adopt: <seat> -> agentic-framework 3.1.0
  create  docs/agents/FRAMEWORK.md
  create  docs/agents/roles/brain.md
  create  docs/agents/roles/worker.md
  create  docs/agents/roles/verifier.md
  create  tools/fw.py
  create  tests/test_framework.py
  create  AGENTS.md
  create  docs/state.md
  create  docs/rounds/README.md
  beside  .gitattributes.framework
  create  .worktrees/.gitignore
  record  docs/agents/framework.json

Edited framework files were left alone. Review each difference, move any
project-specific content into AGENTS.md or docs/agents/local/, then replace the
file with its .framework copy:
  .gitattributes  <-  .gitattributes.framework

dry run: nothing written
```

Actual adoption: same command without `--dry-run` → exit 0. The plan's create,
beside and record output was identical, followed by:

```text
Next: fill in AGENTS.md (what the project is, roles, invariants, evidence,
what is enforced), then commit this as the project's first round.
```

The generic .gitattributes sidecar was inspected and removed; existing rules
already force Python LF and preserve Windows shortcut bytes. No hook needs the
generic wildcard rule. Original .gitattributes remains unchanged, as required
by the focused brief. Installed framework commands were used thereafter.

Byte comparison and manifest fingerprint validation → exit 0. The Python
check compared each manifest `kind: copy` to its source in the pinned clone,
then compared SHA-256 with the manifest:

```text
source and manifest match: docs/agents/FRAMEWORK.md
source and manifest match: docs/agents/roles/brain.md
source and manifest match: docs/agents/roles/verifier.md
source and manifest match: docs/agents/roles/worker.md
source and manifest match: tests/test_framework.py
source and manifest match: tools/fw.py
```

`python3 --version` → exit 0

```text
Python 3.9.6
```

`uname -srm` → exit 0

```text
Darwin 27.0.0 arm64
```

`python3 tools/fw.py check` → exit 0

```text
0 error(s), 0 warning(s)
```

`python3 tools/fw.py status` → exit 0

```text
Framework
  pinned to agentic-framework 3.1.0 (https://github.com/cntrl-alt-lenny/agentic-framework)
  up to date with the latest release (3.1.0)
Merge rule
  owner-approves
Rounds
  in flight: 002-framework-adoption (Tier 2)
    worker: started on worker/002-framework-adoption, no report yet
    verifier: not started
This machine
  on worker/002-framework-adoption; no uncommitted changes
  not on GitHub yet: worker/002-framework-adoption (1 commit(s))
  safe to leave this machine: NO -- push or deal with the items above first
Checks
  all project checks pass
Command form on this machine: python3 tools/fw.py <command>
next: wait for the Worker of round 002-framework-adoption to finish; if its chat has stopped, send it the same prompt again as message 2
```

`python3 -m pytest tests/ -q` → exit 0

```text
........................................................................ [ 47%]
........................................................................ [ 94%]
........                                                                 [100%]
152 passed in 2.86s
```

`python3 -m ruff check .` → exit 0

```text
All checks passed!
```

`python3 -m py_compile tools/fw.py install.py` → exit 0

```text
(no output)
```

`python3 tools/fw.py prompt --role worker --round 002-framework-adoption` → exit 0

```text
mgs-mc-modkit · ROUND 002 · WORKER

You are the Worker for mgs-mc-modkit, round 002-framework-adoption. Work inside this project's folder on this machine (clone https://github.com/cntrl-alt-lenny/mgs-mc-modkit if it is not here): from its main checkout run git worktree add --detach .worktrees/worker-002 origin/main and work in that folder, never in a copy beside the project. In a cloud workspace, work in the clone it gives you.

In that folder, first run python3 tools/fw.py start --role worker --round 002-framework-adoption (use py -3 or python if python3 is not found) and stop if it fails. Then read AGENTS.md, docs/agents/FRAMEWORK.md, docs/agents/roles/worker.md and docs/rounds/002-framework-adoption/brief.md, and carry out the brief.

Finish, even if you stop early, by writing docs/rounds/002-framework-adoption/worker.md and running python3 tools/fw.py report --role worker --round 002-framework-adoption --push. End your final reply with exactly one line: mgs-mc-modkit · ROUND 002 · WORKER · DONE — report pushed at <commit>, or STOPPED or BLOCKED with the reason.
```

`python3 tools/fw.py prompt --role verifier --round 002-framework-adoption` → exit 0

```text
mgs-mc-modkit · ROUND 002 · VERIFIER

You are the Verifier for mgs-mc-modkit, round 002-framework-adoption. Work inside this project's folder on this machine (clone https://github.com/cntrl-alt-lenny/mgs-mc-modkit if it is not here): from its main checkout run git worktree add --detach .worktrees/verifier-002 origin/main and work in that folder, never in a copy beside the project. In a cloud workspace, work in the clone it gives you.

In that folder, first run python3 tools/fw.py start --role verifier --round 002-framework-adoption (use py -3 or python if python3 is not found) and stop if it fails. Then read AGENTS.md, docs/agents/FRAMEWORK.md, docs/agents/roles/verifier.md and docs/rounds/002-framework-adoption/brief.md, and carry out the brief.

Finish, even if you stop early, by writing docs/rounds/002-framework-adoption/verifier.md and running python3 tools/fw.py report --role verifier --round 002-framework-adoption --push. End your final reply with exactly one line: mgs-mc-modkit · ROUND 002 · VERIFIER · DONE — report pushed at <commit>, or STOPPED or BLOCKED with the reason.
```

`git diff origin/main -- install.py Install-MGS-Mods.cmd Install-MGS-Mods.desktop .github .gitattributes README.md docs/UPGRADING.md` → exit 0

```text
(no output)
```

## Not verified

- Verifier delivery and blind review: the separate Verifier seat has not run;
  its report and Brain's exact-commit acceptance remain required.
- Real Windows/Linux execution was not run locally; the measured host is Darwin
  arm64 with Python 3.9.6. Platform CI is separate evidence when available.
- Real licensed game boots, GUI rendering/cancellation and Nexus audio payloads
  were not exercised. Adoption makes no claim that product hardware checks are complete.
- Repository branch-protection settings and shared-account role enforcement
  were not inspected or changed.
- A separate fresh-clone execution is left to the independent Verifier; this
  seat confirmed committed discovery documents and generated both prompts.

## Changed

- `docs/agents/` and `tools/fw.py`: unmodified pinned framework and manifest.
- `tests/test_framework.py`: framework's unmodified hygiene regression test.
- `AGENTS.md`: project scope, three seats, owner-approves, invariants, evidence
  commands and honest enforcement limits grounded in the brief and product files.
- `.worktrees/.gitignore`: framework seed keeps seat directories out of git.
- `docs/rounds/README.md`: framework seed explains durable round records.
- `docs/rounds/002-framework-adoption/brief.md`: inherited Brain brief, unedited.
- `docs/rounds/002-framework-adoption/worker.md`: this evidence and stamped delivery.
- Installer, pins, shortcuts, workflows, product README and upgrade guide remain
  byte-identical to origin/main, confirmed by the empty diff above.
- Existing product checkout and recovery/usability branch were not switched,
  edited or pushed during this round. No merge, tag or publication was performed.

`docs/state.md` is a new project-owned file. No pre-existing sentences were
removed. Every added sentence and pointer is reproduced below (template
placeholders were filled, not treated as prior project decisions):

```text
# State

Live work and delivery status come from `python3 tools/fw.py status` and git.
This file records standing decisions and parked work, not branch or PR status.

## Where we are going

Maintain a vanilla-faithful installer for Master Collection Volume 1 on Windows
and Steam Deck/Linux, with repair and removal through the same shortcut.

## Owner decisions

- Use the pinned agentic framework with Brain, Worker and Verifier seats to
  make work resumable from committed briefs and reports.
- Keep owner-approves as the merge rule; only the owner approves merging or release.
- Codex needs no optional adapter or git hook for this adoption.
- Preserve existing product work independently of framework adoption.

## Parked, and why

- Product recovery and usability work stays separate from framework adoption
  so its behavior changes receive their own review.
- Mod upgrades require a coordinated assessment of the coupled pins and
  settings schema, rather than an automatic version bump.
- Real Windows and Steam Deck/Linux game boots and Nexus audio checks require
  suitable hardware, licensed games and user-supplied payloads; synthetic
  fixtures cannot establish those results.
- Tagging and publication require a separate owner-approved release decision.

## Pointers

- `AGENTS.md` defines project roles, invariants and evidence requirements.
- `docs/agents/FRAMEWORK.md` and `docs/agents/roles/` define the pinned workflow.
- `docs/rounds/` holds briefs and stamped reports for framework rounds.
- README.md defines product scope, optional audio and user restoration steps.
- docs/UPGRADING.md explains coordinated mod and configuration upgrades.
- .github/workflows/ defines the existing platform and release checks.
```

## Open questions

- Tier 2 completion requires the separate Verifier report, followed by Brain's
  review and owner approval under owner-approves; Worker delivery does not accept the round.
- On first adoption, origin/main lacks fw.py until this adoption is merged.
  The brief's external pinned start exception is still necessary for an initial
  seat; generated installed-tool prompts describe the normal adopted workflow.
- No optional adapter or git hook was installed.
