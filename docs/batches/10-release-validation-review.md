# 10-release-validation: Verifier review

Reviewed Worker delivery `9eccfcf4661ce4f916d6cec468724ac1db2d1169`.
Candidate remains `15d9277196e7bd1cfbd45fe280a230050b276bed`.
Read the diff before the Worker summary; used an isolated detached checkout.
Independent checks below ran at the reviewed delivery on Darwin, Python 3.9.6.

| Goal | Judgment | Evidence |
| --- | --- | --- |
| Preserve production, pins, schema and version | Met | Candidate-to-delivery diff contains eight batch documentation/evidence additions only. |
| Candidate identity and static shortcuts | Met | Independently parsed installer constants and checked shortcut bytes; both v2.3.0 pins match installer SHA, Windows CRLF and Python/desktop LF. Candidate mod versions/checksums match the matrix. |
| Offline checks and candidate CI | Met | Re-ran local checks; fetched CI metadata and checkout logs independently. Four jobs checked out the literal candidate. |
| Complete resumable matrix | Met | All 21 checklist scenarios represented; 36 applicable platform cases NOT RUN, six Windows cases N/A. Dependencies and run-record fields retain unknown identities. |
| Actual hardware release validation | Not met | Every scenario 01–21: cannot tell whether behavior passes. No licensed game, GUI, audio or restoration observations supplied. |

No BLOCKER, SHOULD FIX or UNPROVEN CLAIM findings. NOTE:
`docs/batches/evidence/10-release-validation/smoke-matrix.md:5` correctly keeps
release readiness blocked. A missing SSH config alone does not establish
whether remote hardware exists; the document limits availability to this seat
and leaves Brain to resolve access. The v2.3.0 asset is unavailable, so testing
the candidate's local installer is necessary. Publication needs separate
approval and checks. No archives, audio or game installations were changed.

Verdict: evidence is complete for the work possible here; no revision required.
This review does not establish hardware success or approve a release.

## Commands and actual results

| Command at reviewed delivery | Actual output | Exit |
| --- | --- | --- |
| `python3 -m pytest tests/ -q` | `273 passed in 6.04s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py` | No output | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `git diff --check 15d9277196e7bd1cfbd45fe280a230050b276bed HEAD` | No output | 0 |
| `git diff --name-only 15d9277196e7bd1cfbd45fe280a230050b276bed HEAD` | Eight paths under `docs/batches/` | 0 |
| `python3 docs/batches/evidence/10-release-validation/verify-pins.py` | See output below | 0 |
| `gh release view --json tagName,url` | `tagName: v2.2.0` | 0 |
| `gh release view v2.3.0 --json tagName,url` | `release not found` | 1 |

Pin-check output:

```text
MODKIT_VERSION=2.3.0
install.py SHA-256=a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5
install.py: LF only
Install-MGS-Mods.desktop: TAG=v2.3.0, SHA=a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5, LF only
Install-MGS-Mods.cmd: TAG=v2.3.0, SHA=a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5, CRLF only
Versioned release notes exist; both shortcut pins match
```

CI query: `gh run view 37525559856 --json headSha,conclusion,jobs,url`
(exit 0): candidate `headSha`, overall and all four job conclusions `success`.
`gh run view 37525559856 --log` (exit 0) independently confirmed the candidate
checkout SHA in each job; actual test output follows. CI results concern the
candidate, not the documentation delivery.

```text
test (3.12): 273 passed in 6.30s
test (3.11): 273 passed in 5.51s
test (3.9): 273 passed in 6.73s
test-windows: 271 passed, 2 skipped in 18.08s
```

The two Windows skip decorators in `tests/test_safe_extract.py` concern
privileged symlink creation. Local desktop validation is unavailable; candidate
Linux CI supplies it. No hardware result is inferred from these checks.
