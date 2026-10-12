# 14-mgs4-patriotfix

Checked: new upstream archive/settings and installation/removal require independent review. The owner requested MGS4 integration; the earlier handoff omitted its concrete implementation batch. This brief closes that gap. Start after batch 11 is merged. Batch 12 can independently start from current main; its later MGS4 adapter depends on accepted batch 14. Source authentication supports planning, not native compatibility.

## Worker prompt

```text
MGS Master Collection Mod Kit · BATCH 14-mgs4-patriotfix · Worker

Start with python3 tools/fw.py status. Read AGENTS.md, the framework, your Worker card, docs/state.md, docs/UPGRADING.md and docs/RELEASING.md. Begin only after Brain confirms batch 11 is merged. Use worker/14-mgs4-patriotfix from latest main in an isolated .worktrees/worker-14-mgs4-patriotfix seat. This is an M1 Mac development seat; native Windows/Deck checks remain separate.

Implement the owner's requested MGS4 support in the existing installer: game discovery and selection, official MGSPatriotFix installation, upfront settings selection, repair, removal and per-game results. Authenticate MGS4's Steam identity, executable/root layout and original/save locations. Reject wrong-game payloads and ambiguous destinations.

Pin stable MGSPatriotFix 0.2.2, official MGS4_MGSPatriotFix_0.2.2.zip, and its independently computed SHA256 as one reviewed archive/settings set. Authenticate tagged source c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de at https://github.com/ShizCalev/MGSPatriotFix. Audit archive layout, Config Tool saving and every runtime reader, including hidden Peace Walker fields. Derive complete settings, defaults, types and constraints independently of your template; keep bounded capture/refusal behavior. Do not assume MGSHDFix's schema or paths apply.

Use vanilla-faithful bug fixes and QoL. Preserve original rendering and frame-rate behavior by default; visual overrides must be explicit. Keep automatic upstream updates disabled. Use one authoritative settings writer and preserve supported custom values. Do not add Peace Walker, ClarityFix, FPS unlockers, textures, MGS4 audio or standalone MGSM2Fix flashback integration. Existing MGS1–3 pins and behavior remain unchanged.

Protect saves, originals, oldest backups and recovery records through fresh install, repair, cancellation and removal. Preserve transaction locks and per-game rollback/commit. Supply the authenticated MGS4 Proton launch option; DS3 drivers remain optional user-managed setup.

Update README, settings/troubleshooting/upgrade guidance, AGENTS.md's product description and standing scope to accurately include implemented MGS4 while distinguishing pending native validation. Preserve framework copies, Python 3.9 and Windows/Linux archive handling. Keep unpublished kit version 2.3.0; regenerate and independently verify both shortcut tags/SHA256 and CRLF/LF.

Add meaningful tests for discovery, correct payload/schema, existing-game regression, preference preservation, malformed-edit refusal, backup lineage, rollback/recovery, cancellation, mixed-game outcomes and removal. Run full pytest, Ruff, compilation, framework check/status, relevant UPGRADING checks and desktop validation where available. Record exact commits, commands, output and exits. Source-unproven settings must not be guessed. Missing native exports/boots/gameplay remain NOT RUN; provide a Windows/Deck fresh-install, repair and removal handoff.

Commit docs/batches/14-mgs4-patriotfix.md with Done, Checked, Not checked, Failed or blocked, below 500 prose words. Push, open a draft PR and return the literal delivery SHA. Technical questions go to Brain. Never approve, merge, tag or publish.
```

## Verifier prompt

Send only after Brain supplies the literal Worker delivery SHA.

```text
MGS Master Collection Mod Kit · BATCH 14-mgs4-patriotfix · Verifier

Start with python3 tools/fw.py status. Read project/framework rules, your Verifier card and this brief. Check Brain's literal Worker SHA in an isolated seat; read the diff before the summary.

Independently authenticate MGS4 identity, upstream tag/archive/checksum and layout. Derive required settings and conservative defaults from runtime readers and Config Tool saving, including hidden fields. Challenge fixture assumptions, wrong-game detection, conflicting ASI loaders, existing manual settings, original rendering defaults and unsupported compatibility claims.

Exercise settings preservation/refusal, original backup lineage, rollback/recovery, locks, cancellation, mixed-game outcomes and removal. Verify MGS1–3 regression coverage, unchanged existing pins, both shortcut tags/hashes, line endings, Python 3.9, complete offline checks and exact-commit CI. Inspect the native handoff; synthetic results do not establish boots, gameplay or restoration on real hardware.

Change only docs/batches/14-mgs4-patriotfix-review.md on the Worker branch. Record reviewed SHA, goal judgments, actual commands/results, limitations, findings and verdict below 500 prose words. Findings require severity, file/line and a concrete failure path. Commit, push and return review and reviewed Worker SHAs. No production changes, merge, tag or publication. Technical questions go to Brain.
```
