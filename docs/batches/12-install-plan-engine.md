# 12-install-plan-engine — Worker

## Done

Continued the same isolated Worker branch from `8297142978fc2b6932fc2c0af9485b4b074e09c5`, following the complete correction brief at `fbc360f7d820dc3795aa6c56bf2f778608ac62d7` and Brain's batch 17 review/probe. No dependency on batches 14/16.

Retained the game-neutral plan engine, deterministic standalone embedding, private preparation sandbox and unchanged transaction/recovery/removal recipes. Selection now captures immutable audio acceptance: exact source/digest, game, role, classification and explicit confirmation. Digests bracket classification and confirmation. Collection carries that acceptance into the plan; planning cannot silently hash replacement bytes into a new acceptance. Plan validation requires matching acceptance; preparation checks classification and authenticates copied bytes; review, preparation and execution rechecks retain the selected digest. Changed files require fresh selection/confirmation before game writes, including settings/reset loops. Confident and unchanged explicitly accepted uncertain files need no executor prompts. Independent components and hard rejects remain.

Regenerated both shortcuts at unchanged v2.3.0. No pins, settings schema, mod writers, release tags or other seats changed.

## Checked

Production/test commit: `67c7bbf873ea6405519f3fb43f738541d4041044`. Actual commands, outputs, exits and initial failures: [evidence](evidence/12-install-plan-engine.txt).

| Command | Actual result | Exit |
|:--|:--|:--|
| `python3 -m pytest tests/ -q` | 335 passed in 33.50s | 0 |
| `python3 -m ruff check .` | All checks passed! | 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py` | no output | 0 |
| `python3 tools/embed_install_plan.py --check` | standalone/source match | 0 |
| `python3 tools/fw.py check` | 0 errors, 0 warnings | 0 |
| Independent shortcut/SHA/line endings/Python 3.9 assertions | both v2.3.0; SHA `64a8a44300b247796da988b40a0d37c734cdac6cb9d02389e0c99a041741e3ea` | 0 |

Brain's original probe installs the replacement at the old SHA; corrected planning rejects it. Twenty-three new tests cover confident/uncertain replacements, actual main review/settings/reset/prepared loops, classification/confirmation changes, acceptance game/role/proof corruption and unchanged accepted files. Each rejection checks every selected game's snapshot. Existing rollback, cancellation, recovery, old-record, no-interaction and standalone/parity checks remain green. Applicable UPGRADING archive/settings checks are synthetic; coupled values unchanged. Framework copies unchanged.

## Not checked

Native Windows/Steam Deck game boots, real install→repair→remove, licensed/user audio compatibility, Config Tool and GUI rendering: NOT RUN. `desktop-file-validate` unavailable locally; Linux CI runs it. Independent Verifier review remains required. Exact-delivery CI is reported on PR #22.

## Failed or blocked

No implementation blocker. Initial tests required collection metadata and corrected fixture filenames/classification shapes; failures retained in evidence. Ordinary diff checking flags required CMD CRLF; CR-aware checking passes. Framework status initially hit a disappearing app capture ref (exit 2); retry retained. Framework update remains Brain-owned. No acceptance, merge, tag or publication.
