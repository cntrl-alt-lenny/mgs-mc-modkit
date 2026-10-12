# Parallel Worker ownership

Owner direction: keep two Workers active when concrete independent work exists. Useful progress and fewer owner relays are the measures; avoid filler tasks.

| Worker | Batch | Ownership |
|:--|:--|:--|
| A | 12-install-plan-engine | New plan/preparation/execution module; thin orchestration adapter; planning tests. |
| B | 16-volume1-qol-upgrade | Coupled candidate manifest, upstream source/archive/export validation; mod-specific schemas/migration and upgrade checks. |

Both start from current main in isolated worker branches. Planning PR #16, banner approval and MGS4 PR #19 are not start gates. This explicitly supersedes the earlier batch 12 wait-for-14 instruction. The current recipes provide useful engine work now.

Keep adapter contracts compatible and read package identities from existing definitions. Do not copy candidate versions into the plan engine. Each Worker owns its own tests and summary; neither edits the other's module or framework copies. No game support or release claim follows from these branches.

Genuine dependencies:

- Adding MGS4 to the new engine requires accepted MGS4 implementation later; core MGS1–3 planning does not.
- Changing the coupled shipping pins/template/schema requires actual per-game Config Tool exports. Without them Worker B delivers source/archive validation and capture tooling while retaining shipping pins.
- Final combined validation requires both accepted changes. Both may alter install.py and shortcut hashes: Brain decides integration order and interface decisions; the affected Worker resolves production conflicts, regenerates both hashes and repeats full checks. Separate Verifiers review the resulting literal SHAs before owner-approved merges. No force-pushing shared branches.
- Native licensed game boots, real repair/removal and user-supplied audio require appropriate hardware/files; synthetic and Mac checks cannot establish release readiness.

MGS4 independent review can proceed separately. These enhancements do not create further prerequisites for reviewing and merging its current implementation. Workers send technical questions to Brain, keeping integration decisions out of owner relay work.
