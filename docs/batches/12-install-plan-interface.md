# Batch 12: Brain interface decision

Design direction approved; implementation still requires the Checked review path. No change to shipping assets or release rules.

```text
MGS Master Collection Mod Kit · BATCH 12-install-plan-engine · Worker

Proceed with install_plan.py as the authoritative game-neutral source, deterministically embedded verbatim in install.py. Keep the installer runnable alone from the shortcuts' temporary download location. No adjacent-module import, runtime source download or new release asset. Delimit the generated region clearly; do not hand-edit it. The sync tool must fail on missing/duplicate markers and preserve Python LF. Add a non-writing check mode, parity coverage and an isolated standalone execution/import test with install_plan.py absent. Preserve Python 3.9 and regenerate both shortcut hashes after embedding.

A recording adapter is acceptable if it runs recipes exclusively against a sandbox game view and immutable snapshots of relevant existing settings/launcher inputs. Existing recipes inspect tx.game_dir directly after extraction; recording tx calls alone is insufficient. Audit every recipe/helper for side effects outside the adapter. Never construct live InstallTxn during preparation: its constructor may recover interrupted files. Detect pending recovery and stop/replan; any real recovery runs under locks and invalidates changed assumptions.

Stage all selected payloads and generated outputs, preserving component order and overlaps. Record their identities and authenticated settings, existing-file and record assumptions. Execution replays the validated actions through existing InstallTxn using the exact authenticated cached payloads and prepared settings; no network downloads, settings regeneration or UI prompts. Internal archive extraction by unchanged InstallTxn is acceptable only from those validated local bytes, retaining verification and rollback. Prefer staged output reuse when its existing API safely permits it; do not bypass transaction internals to avoid extraction. Revalidate plan inputs and staged contents under locks before the first live mutation. Recovery or changed inputs require replanning rather than silently adapting the confirmed plan.

Account for all simultaneous staging, original backups, rollback snapshots and writes per relevant volume, including shared volumes and large audio. Preserve cancellation and per-game outcomes. Meaningful tests must prove late-payload failure leaves every earlier game unchanged, preparation cannot touch live files, recipe checks see staged content, stale inputs/recovery stop safely, staged tampering is rejected and standalone behavior matches module behavior.

Worker 16 retains pins/schema/mod-writer ownership. Keep InstallTxn unchanged and existing recipe contracts stable. If a recipe needs a contract change or the adapter cannot isolate it safely, bring that specific change to Brain rather than bypassing safety or duplicating the recipe. Follow the existing full batch checks, summary, draft-PR and separate Verifier requirements. This design decision does not approve a merge or release.
```

Evidence reviewed: current shortcut/release assets contain standalone install.py only. Recipe checks inspect tx.game_dir; set_launcher_options reads launcher state and routes writes through tx. InstallTxn.__init__ can invoke interrupted recovery. The Worker's uncommitted module/embed tool was inspected as an initial sketch, not accepted implementation.
