# 12-install-plan-engine — Worker

## Done

Built from `origin/main` at `85697bd`, independently of batches 14/16. Followed the complete brief at `095a3b1b03d8bb543aa929069eca501b9e7cd8fa` and Brain's embedding decision at `5f6dd663d72a987b06b5910a88eb7e2550b5bce9`.

Added authoritative game-neutral `install_plan.py`, deterministically embedded into standalone `install.py`. Plans record schema/profile, ordered games/paths/settings, exact package versions/checksums, supplied archive roles/identities, incompatibilities and input assumptions. `tools/embed_install_plan.py --check` verifies without writing; sync rejects missing/duplicate markers and non-LF Python.

The current-recipe adapter runs unchanged recipes against a private sandbox, authenticates every cached archive, validates generated settings, launcher records, destinations, existing records and aggregate per-volume space before any game-file write. Preparation never constructs live InstallTxn. Pending recovery is handled under locks before choices are collected; later recovery or stale inputs require a fresh plan. Execution locks all selected games, rechecks inputs/cache/space, then replays local archives and prepared bytes through unchanged InstallTxn. No executor downloads, settings regeneration, picking or confirmation. Earlier commits, restored games and unstarted games remain separate.

Preserved entry points, independently selectable ordered audio components, mod-specific writers, pins/schema, transaction/recovery/removal contracts and record schema. Regenerated both shortcut hashes without changing release version/tag. Installed-file verification explicitly does not establish game playability.

## Checked

Production/test commit: `6a1e8765c6a991e8b71015d2600e1926dbaf3e81`. Actual commands, output excerpts and exit codes: [evidence](evidence/12-install-plan-engine.txt).

| Command | Actual output | Exit |
|:--|:--|:--|
| `python3 -m pytest tests/ -q` | `312 passed in 22.62s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py` | no output | 0 |
| `python3 tools/embed_install_plan.py --check` | standalone/source match | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `python3 tools/fw.py status` | `all project checks pass` | 0 |
| Both shortcut tag/SHA/line-ending assertions | v2.3.0; SHA `5639d83c64f8bfbe41f88c57495701f6dba23a26d704cb5cd9e5b947f1245f52` | 0 |

Tests include late failure with zero earlier mutation, stale inputs/cache/recovery, concurrent refusal, cancellation/failure/recovery outcomes, no executor interaction, schema-1 repair/removal, source parity and isolated standalone import/execution without the source module. Applicable UPGRADING checks cover settings/archive layout synthetically; no coupled values changed. Framework copies unchanged.

## Not checked

NOT RUN: native Windows/Steam Deck game boots, real install→repair→remove, licensed/user-supplied audio, native Config Tool and GUI rendering. `desktop-file-validate` unavailable on this Mac. Cross-platform CI and independent Verifier review remain required. No MGS4 integration, new profile/game, release, merge or tag.

## Failed or blocked

No implementation blocker. Initial fault-hook, exception-expectation and Ruff failures were corrected and retained in evidence. Framework 4.0.1 availability is Brain-owned; unrelated seats were preserved. Brain coordinates integration order with Worker 16 and exact-commit Checked review.
