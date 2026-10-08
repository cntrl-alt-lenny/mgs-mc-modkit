# Brain disposition of batch 11

Worker reviewed: `fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c`.
Verifier delivery/current PR #17 head: `84e6737aa26c5f24e49312637cf49e76cc0bedb2`.
Base: `90967b9068125d2e7c0ceac8f6c9d60808a45c95`.
Brain host: macOS arm64, Python 3.9.6, 2026-10-08.

## Decision

No blocking or should-fix finding. Accept the source/offline settings correction
for owner-approved merge; this does not approve a release or establish successful
game boots. The Verifier reviewed the exact Worker SHA, added only its review,
and stayed within its role. Production, tools, tests and shortcuts are unchanged
between the reviewed Worker and Verifier delivery.

The source-backed three defaults and 131-key runtime schema agree with Brain's
earlier independent source review. Inspected and reran the Verifier's additional
probe: independent literal resolution, all 133 calls/131 pairs, migration using
the real main template, both games, complete preview/rollback inventories,
original backup retention after committed repair, and all six incomplete subsets.
This corroborates its findings rather than relying only on its prose.

The native handoff covers exports, both games/platforms, fresh installation,
repair, custom values, reset, negative cases, cancellation, locks, gameplay and
removal. These remain a plan, not observed hardware evidence. Native exports,
dynamic choices, Windows/Deck boots/gameplay, audio and real repair/removal
remain NOT RUN. No finding requires production changes before source/offline
acceptance. Batch 12 remains queued until batch 11's merge is approved.

## Actual Brain checks at Verifier delivery

| Command | Actual result | Exit |
| --- | --- | --- |
| `git diff --name-only fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c 84e6737aa26c5f24e49312637cf49e76cc0bedb2` | Only docs/batches/11-hdfix-runtime-schema-review.md | 0 |
| `git diff --quiet fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c 84e6737aa26c5f24e49312637cf49e76cc0bedb2 -- install.py tools tests Install-MGS-Mods.cmd Install-MGS-Mods.desktop` | No output; equal | 0 |
| `python3 -m pytest tests/ -q` | 283 passed in 6.08s | 0 |
| `python3 -m ruff check .` | All checks passed! | 0 |
| `python3 -m py_compile tools/fw.py install.py` | No output | 0 |
| `python3 tools/fw.py check` | 0 error(s), 0 warning(s) | 0 |
| `python3 docs/batches/evidence/11-hdfix-runtime-schema/verify-pins.py` | Both v2.3.0 shortcuts match e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a; line endings, Python 3.9 grammar, unchanged pins/framework pass | 0 |
| `git -c core.whitespace=cr-at-eol diff --check origin/main...HEAD` | No output | 0 |
| `PYTHONPATH=. python3 /tmp/mgs-batch11-independent.py` after inspecting its entire source | Independent runtime enumeration: 133 calls / 131 pairs, exact schema + fixture; raw source hashes PASS. Actual main template: both games; preferences, preview inventory, rollback inventory, original backup after commit; all 6 partial subsets refused PASS | 0 |
| `python3 docs/batches/evidence/11-hdfix-runtime-schema/audit-runtime.py /tmp/mgs-brain11-upstream-20261008` | Authenticated source/fixture equality; 133 calls/131 keys | 0 |
| `gh pr view 17 --json headRefOid,statusCheckRollup,body` | Exact Verifier delivery; CI 3.9/3.11/3.12 Linux and Windows all SUCCESS, run 37785564529 | 0 |

## README evidence

After fetching origin, an AST inventory of GAMES at every local and origin ref
returned only `mgs1`, `mgs2`, `mgs3`. No fetched integration branch includes MGS4
or Peace Walker. Text search found only upgrade assessment discussion of an
upstream mod's Volume 2 support; upstream capability does not implement kit
integration. `gh release list --limit 3 --json tagName,name,isLatest,publishedAt`
returned v2.2.0 as latest, published 2026-08-28. Current README claims of a
verified Deck badge are unsupported; batch 11 independently corrects that badge
to the same pending value. This documentation draft does not expand product scope.
