# Brain preliminary review: batch 11

Reviewed PR #17 at `fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c`, against main
`90967b9068125d2e7c0ceac8f6c9d60808a45c95`, on macOS arm64, Python 3.9.6.
Used an isolated detached checkout. Read the production/test/documentation diff
before the Worker summary. This is Brain's preliminary review; the separate
Verifier has not reviewed this delivery. No merge or release approval.

## Judgment

No blocking code finding identified. The three added settings, types, choices
and defaults match authenticated MGSHDFix 4.1.0 source. Config Tool visibility
does not exclude hidden controls from saving; shared runtime initialization
reads all three MG-only keys. Fresh source capture equals the committed fixture,
including all schema constraints and source-byte hashes. Runtime enumeration
matches all 131 unique canonical fields across 133 calls.

Migration accepts the complete historical shape and validates every value
before transactional writing. Supported preferences survive; partial shapes
and malformed edits refuse. Existing preview, rollback and preservation tests
pass. An additional check extracted the actual main template with Python AST,
substituted supported options for us/eu/jp, and verified migration preserves
every original value and is idempotent. No mod versions/checksums changed.

Source hash changes are explained by CRLF: normalizing the fresh source to LF
reproduces both previous fixture hashes. The new hashes describe original bytes.
Reviewed Config Tool construction/saving, the three declarations, shared runtime
reads and InputHandler's passed-key reader directly in the fresh clone.

## Actual command results at the reviewed delivery

| Command | Actual result | Exit |
| --- | --- | --- |
| `python3 -m pytest tests/ -q` | `283 passed in 6.08s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py` | No output | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `python3 docs/batches/evidence/11-hdfix-runtime-schema/verify-pins.py` | Both v2.3.0 shortcuts match SHA256 `e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a`; CRLF/LF, Python 3.9 grammar, unchanged pins/framework pass | 0 |
| `git -c core.whitespace=cr-at-eol diff --check origin/main...HEAD` | No output | 0 |
| `python3 docs/batches/evidence/11-hdfix-runtime-schema/audit-runtime.py /tmp/mgs-brain11-upstream-20261008` | Authenticated hashes; 133 calls, 131 unique keys; fixture equality | 0 |
| Fresh `capture(...) == fixture` and raw/LF SHA256 comparison, via Python | Equal fixture; old hashes equal LF-normalized upstream | 0 |
| AST extraction/migration/idempotence check, via Python | `Actual main 128-key template migrates, preserves all original values and is idempotent for us/eu/jp` | 0 |
| `git clone --depth 1 --branch 4.1.0 https://github.com/ShizCalev/MGSHDFix.git /tmp/mgs-brain11-upstream-20261008` | Checkout `f4f662d67a2a033dee0877e436a0fe65eb719e0b` | 0 |
| `git ls-remote origin refs/tags/4.1.0`, in the upstream clone | Same literal SHA | 0 |
| `gh run view 37783269039 --json headSha,conclusion,event,jobs,url` | Exact delivery SHA; all four Linux/Windows jobs successful | 0 |

## Failed attempts and limits

Default `git diff --check` exited 2 because the intentionally byte-preserved
Windows shortcut uses CRLF. The corrected `cr-at-eol` check passed. A source
search named four nonexistent upstream paths (exit 2); the corrected search
located `src/resources/input_handler.cpp`. First two extra migration probes
used unsupported audio labels `Stereo`/`Original` and correctly refused (exit 1);
the corrected probe used the declared `Stereo (2.0)` choice and passed.

Native Config Tool exports, corrected-candidate Windows/Deck initialization,
gameplay and actual repair/removal are NOT RUN. Desktop validation was not run
locally; Linux CI at this delivery passed it. Static results establish no native
compatibility or release readiness. Next: separate Verifier at the exact SHA.
