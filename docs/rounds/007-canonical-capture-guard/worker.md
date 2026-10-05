<!-- fw-report
round: 007-canonical-capture-guard
role: worker
branch: worker/007-canonical-capture-guard
head: 0166a057fa869546f0cc28ef715a9961d771fb6a
os: macOS 27.0.1
python: 3.9.6
written: 2026-10-05T07:48:50Z
-->
## Verified

- Start: `python3 tools/fw.py start --role worker --round 007-canonical-capture-guard` → exit 0: `seat ok: worker, round 007-canonical-capture-guard, branch worker/007-canonical-capture-guard at d3b1bbeafe62`.
- Main baseline is `f28f9eaea634b71f5bb788794635304e0987a764`; selected Worker baseline is `d3b1bbeafe62ed93ca02155dd1d689f8c6d9466b`. Implementation commit: `0166a057fa869546f0cc28ef715a9961d771fb6a`. Host Python: `Python 3.9.6`.
- Prior-tool reproduction at `d3b1bbe`: a synthetic `Demo_Setting` conditional declares `constexpr char const*` with `Replacement Key` in one branch and the reviewed spelling in the other. API returned success with only the reviewed key in the field list. CLI exited 0, stdout 1067 bytes containing JSON with only the reviewed key, and empty stderr. The original reproducer is now covered in both branch orders; conditional section and choice declarations are covered too.
- Against the prior tool, the new targeted tests were run by loading `git show d3b1bbe:tools/capture_settings_schema.py` into the test process. Exit 1: `8 failed, 2 passed in 0.07s`. Failures include both original branch orders, alternate section/key/choice declarations, a nested namespace, a conditional namespace wrapper and CLI partial-success behavior.
- At `0166a057`, the API raises `CaptureError: Unsupported source construct: preprocessor directive in ConfigKeys namespace; review the upstream source format`. CLI exits 1 with stdout length 0 and stderr `capture failed: Unsupported source construct: preprocessor directive in ConfigKeys namespace; review the upstream source format`. Focused regression suite: `python3 -m pytest tests/test_schema_capture.py -q` → exit 0: `42 passed in 0.23s`.
- Immutable source comparison: `python3 docs/rounds/006-schema-capture-safety/attachments/check_sources.py <scratch> docs/rounds/007-canonical-capture-guard/attachments/source-checks.json` → exit 0. Output: `4.1.0: CLI exit 0; 128 exact expected keys; constraints and ORIGINAL hashes match`; same for 4.1.1 with 128 keys; 4.1.2 with 131 keys; `4.1.0 whole fixture equal; 4.1.2 exact four additions/one removal verified; no binary export claimed`. Attachment records immutable commit identities and both untouched source-byte hashes for each version. 4.1.2 keeps the exact `kFirstPersonViewGameFlags` union `[MGS2, MGS3]`.
- A byte comparison of the 77 files in the Worker baseline tree found only the three authorized existing files changed: `tools/capture_settings_schema.py`, `tests/test_schema_capture.py`, and `docs/UPGRADING.md`; the other 74 existing files were byte-identical. `docs/rounds/007-canonical-capture-guard/attachments/source-checks.json` is the sole new supporting file. `git diff --check` → exit 0, no output.
- Shortcut comparison against unchanged `install.py` and the Worker baseline → exit 0: `Install-MGS-Mods.desktop` and `Install-MGS-Mods.cmd` both remain `v2.3.0`, SHA-256 `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`; both bytes remain unchanged and Windows CRLF is preserved.
- `python3 tools/fw.py check` → exit 0: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status` → exit 0: framework pinned/latest 3.1.0 and `all project checks pass`. It reports the pre-existing Round 004 Worker and Verifier reports stale; this correction does not edit those reports. It recognizes Round 007 as the in-flight Worker round.
- `python3 -m pytest tests/ -q` → exit 0: `245 passed in 5.05s`.
- `python3 -m ruff check .` → exit 0: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py tools/capture_settings_schema.py` → exit 0, no output.
- Direct branch CI: `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37279588476`; workflow result `completed`, `success`, head SHA `0166a057fa869546f0cc28ef715a9961d771fb6a`. Each of the four job logs checked out and printed that exact SHA. Linux Python 3.9: 245 passed; 3.11: 245 passed; 3.12: 245 passed; Windows Python 3.12: 243 passed, 2 skipped (existing Windows symlink permission skips). Linux lint, byte compilation and `desktop-file-validate Install-MGS-Mods.desktop` succeeded. Windows confirmed its archive tool as bsdtar. This is direct branch CI, not a generated PR merge checkout.
- `git push origin worker/007-canonical-capture-guard` → exit 0; pushed `d3b1bbe..0166a05`.
- Draft corrective PR `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/10` was opened referencing draft PR #9. No merge, tag or release action was taken.

## Not verified

Actual MGS1/MGS2/MGS3 boots, generated per-game Config Tool exports, runtime setting applicability, audio compatibility, GUI behavior and Steam Deck behavior. This is static source extraction evidence only. No upstream binary or mod was run or installed. Actual exports remain required before a coordinated settings or mod upgrade.

## Changed

- `tools/capture_settings_schema.py`: validate every declaration in exactly one unconditional `ConfigKeys` namespace; reject conditional directives, nested namespaces, duplicate or unsupported declaration spellings before resolving constants.
- `tests/test_schema_capture.py`: add regressions for both original conditional branch orders, conditional section/key/choice constants, unsupported namespace/declaration forms, API failures and empty-stdout CLI failure.
- `docs/UPGRADING.md`: document the full-namespace validation boundary and accepted pre-namespace include guards/includes.
- `docs/rounds/007-canonical-capture-guard/attachments/source-checks.json`: retain the immutable 4.1.0/4.1.1/4.1.2 comparison output. No `docs/state.md` changes.

## Open questions

Brain and owner review of exact commit `0166a057fa869546f0cc28ef715a9961d771fb6a` remains pending under `owner-approves`. Brain decides the disposition of prior draft PR #9. Runtime/export limitations remain as listed under Not verified.
