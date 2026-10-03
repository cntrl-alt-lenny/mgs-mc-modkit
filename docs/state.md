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
