# 002-framework-adoption: Establish the Brain, Worker and Verifier workflow

Tier: 2
Mode: documentation
Supersedes: none

## Goal

A fresh clone can discover this project's Brain, Worker and Verifier instructions,
run the framework commands, and resume this round using committed reports rather
than chat history or temporary files.

## Context

The owner asked this project's Brain to follow agentic-framework and provide both
seat messages after reviewing completed work. The previous prompts were informal:
this project has no AGENTS.md, framework manifest, tools/fw.py or stamped reports.
Do not describe those earlier conversations as framework-delivered rounds.

Use agentic-framework release v3.1.0 from
https://github.com/cntrl-alt-lenny/agentic-framework. Its tag resolves to
eca1306dc43cb81f0df3ee42f841812da68e8b1e. Read its entire FRAMEWORK.md and role cards.
The product's README, docs/UPGRADING.md, install.py and existing CI define its
current scope and required checks. Existing product PR #2 remains separate; do
not merge it, change its branch, or claim its real-machine checks are complete.

## Scope and non-goals

Adopt the pinned framework with Worker and Verifier seats, fill the project-owned
AGENTS.md and docs/state.md using established project facts and owner instructions,
and create this round's stamped reports. Use the default owner-approves merge rule.
Codex needs no adapter. Do not install optional adapters or git hooks.

Do not change installer behavior, mod versions, checksums, shortcuts, release
workflows, licensing, repository settings or product documentation unrelated to
adoption. Do not start a product release or rewrite history. Keep framework copies
unaltered; project-specific instructions belong in project-owned documents.

## Bootstrap instructions

This is first adoption, so the installed start command is initially absent. Obtain
a clean temporary checkout of the framework at the pinned release. Create an
isolated seat checkout inside the project's .worktrees directory, or use the
cloud tool's separate clone. Run the pinned framework's external command before
working: python3 <framework>/tools/fw.py --cwd <seat> start --role worker --round
002-framework-adoption. The Verifier uses the same external command with role
verifier, only after the Worker has pushed its report. These external commands
are the explicit bootstrap exception for this round; do not fake a missing tool.

After start has selected the seat branch, the Worker runs the pinned adopt.py
against that seat checkout with --project "MGS Master Collection Mod Kit"
--workers worker --verifier --dry-run, reviews the plan, then runs without
--dry-run. Neither a hook nor an adapter is required. Read the installed files and
finish all subsequent commands with the project's installed tools/fw.py. The
Verifier's start selects the delivered Worker commit, which contains that tool.

## Invariants

- Brain judges and merges; Worker and Verifier never merge their own work.
- Only the owner approves a merge or release. The framework's default applies.
- The kit targets Master Collection Volume 1 on Windows and Steam Deck/Linux.
- Pinned mod versions and matched configuration are reviewed together; no
  independent numeric bumps (docs/UPGRADING.md).
- User saves, originals and recovery records must remain protected (install.py).
- Nexus audio is user-supplied and must not be redistributed (README.md).
- Synthetic tests and CI do not establish real game boot or audio compatibility.
- No personal paths or account details in tracked framework documents.
- Preserve all unrelated files and the previous product work.

## Acceptance criteria

1. The framework manifest pins 3.1.0 and the installed copies match its source.
2. AGENTS.md declares Brain, Worker and Verifier, owner-approves, the project's
   existing invariants, evidence commands and honest enforcement limitations.
3. docs/state.md records durable decisions and parked work, not live PR status,
   commit identifiers or invented owner decisions.
4. Framework check and the complete offline suite pass. Python 3.9 remains supported.
5. Both reports are committed and pushed; delivery judges their exact commits.
6. Worker and Verifier prompts can be generated, and status gives a concrete next
   action without needing chat history.
7. The diff is limited to adoption, project-owned guidance and round records.

## Required evidence

Keep real output and exit codes in the report for:

- The pinned framework tag/commit, adoption dry run and actual adoption.
- python3 tools/fw.py check
- python3 tools/fw.py status
- python3 -m pytest tests/ -q
- python3 -m ruff check .
- python3 -m py_compile tools/fw.py install.py
- Both fw.py prompt commands for this round, and the final report --push command.

The Verifier makes a blind first pass over the diff and acceptance criteria before
reading worker.md, independently reruns the relevant checks, and checks what a
fresh clone can discover. State unavailable platform or hardware checks plainly.

Open or update one PR for the adoption round. Do not merge, tag or publish.
