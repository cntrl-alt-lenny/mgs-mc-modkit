# MGS Master Collection Mod Kit

Instructions for every agent, in every tool. Read `docs/agents/FRAMEWORK.md`
and your card in `docs/agents/roles/`; these project rules take precedence.
Every session starts with `python3 tools/fw.py status`.
On Windows, use `py -3` or `python` if `python3` is unavailable.

Merge rule: owner-approves

## What this project is

The kit installs vanilla-faithful fixes and restorations for Metal Gear Solid
Master Collection Volume 1 (MGS1, MGS2 and MGS3) on Windows and Steam Deck/Linux.
It automates official upstream mod downloads and optional user-supplied audio,
with repair and removal through the same installer (README.md).

## Roles

| Seat | Card | Scope |
|---|---|---|
| Brain | `docs/agents/roles/brain.md` | Plans batches, writes prompts, reviews exact commits, and merges only after owner approval. |
| Worker | `docs/agents/roles/worker.md` | Does one batch on its `worker/<batch>` branch, runs the checks and commits its summary in `docs/batches/`; never accepts or merges its own work. |
| Verifier | `docs/agents/roles/verifier.md` | Reviews a Checked batch at one exact commit and writes findings; never writes production code or merges. |

Use isolated seats under `.worktrees/` or separate clones. Preserve unrelated
checkouts, branches and uncommitted work. Do not reinterpret informal earlier
conversations as framework batches (adoption brief).

## Invariants

- Only the owner approves a merge or release; Brain alone merges accepted work.
  Workers and Verifiers never merge, tag or publish (owner instructions and framework).
- Keep the vanilla-faithful scope: fixes and restorations, excluding AI-upscaled
  textures and gameplay changes (README.md).
- Review mod pins, archive checksums and the matched configuration schema as a
  coupled set; never make isolated numeric bumps (docs/UPGRADING.md).
- Protect user saves, original files, backups and recovery records during
  installation, repair, cancellation and removal (install.py and adoption brief).
  Some large audio originals require Steam verification rather than backup;
  do not claim exact restoration without evidence (README.md).
- Nexus audio remains user-supplied and must not be redistributed (README.md).
- Preserve Python 3.9 support and native Linux/Windows archive handling
  (.github/workflows/ci.yml).
- Changes to install.py require regenerating both shortcut hashes and matching
  release tags; preserve Windows CRLF and Python LF (.gitattributes and release workflow).
- Synthetic tests and CI never establish real game boots or audio compatibility;
  report unavailable hardware checks plainly (adoption brief).
- Keep framework copies unaltered. Put project guidance here or in
  `docs/agents/local/`; omit personal paths and account details from tracked
  framework documents (framework and adoption brief).

## Evidence

Keep actual commands, output and exit codes at a stated commit in batch summaries.
Run the prompt's required checks in addition to the relevant rows below.

Checked path (Worker, Verifier, then Brain): changes to install.py's handling
of saves, originals, backups or removal; mod pins, archive checksums or the
settings schema; and release tags or shortcut hashes. The offline tests cannot
catch these mistakes. Everything else is Normal; notes and framework updates
are Small.

| Changed | Required evidence |
|---|---|
| Framework adoption or project guidance | `python3 tools/fw.py check`; `python3 tools/fw.py status`; compare copies to pinned source and review the diff. |
| Python or framework adoption | `python3 -m pytest tests/ -q`; `python3 -m ruff check .`; `python3 -m py_compile tools/fw.py install.py`; maintain Python 3.9 syntax. |
| Installer, settings, archives or pins | Complete offline suite and lint; checks in docs/UPGRADING.md; verify BOTH shortcut tags and SHA-256 against install.py; `desktop-file-validate Install-MGS-Mods.desktop` where available. |
| Every batch | Commit work and `docs/batches/<batch>.md` (Done, Checked, Not checked, Failed or blocked), then push; report limitations, not guessed success. |

Framework hygiene cannot prove guidance is accurate; review its sources and
precedence independently. Installer tests do not prove GUI rendering, real
upstream archive compatibility or licensed game boot behavior. Live pin checks
are advisory and do not authorize upgrades.

## What is actually enforced

The installed framework checks document hygiene, the state budget and the
length of batch summaries; its status command lists unmerged batches and
changed framework copies.
The installed framework test runs those hygiene checks in the offline suite.
Existing CI runs tests on Linux Python 3.9/3.11/3.12 and Windows Python 3.12;
Linux also runs Ruff, compilation and desktop validation. Release CI checks both
shortcut pins before publication. No adapter or pre-push hook is installed.
The existing .gitattributes already keeps Python and desktop files LF and
Windows shortcuts byte-preserved; the generic adoption sidecar is not applied.

Owner approval, role separation and scope are rules agents keep, not permission
locks. Shared GitHub credentials cannot distinguish seats. Repository branch
protection and required-check settings have not been inspected, and no claim
about host enforcement is made. No framework command runs the full suite or
lint: the Worker must run and report them explicitly.

## Where to look

- Decisions and parked work: `docs/state.md`.
- Batch summaries and reviews: `docs/batches/`. Earlier 3.x rounds stay in `docs/rounds/` as history.
- Product scope and user instructions: README.md.
- Coupled upgrades and release checks: docs/UPGRADING.md and .github/workflows/.
