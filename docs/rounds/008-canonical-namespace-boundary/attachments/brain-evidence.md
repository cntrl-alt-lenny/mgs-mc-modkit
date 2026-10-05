# Brain rejection evidence

Examined implementation: 0166a057fa869546f0cc28ef715a9961d771fb6a.
Complete delivery: 80709a01f28e0c716ab5e05ebaf5394b25d9c56a.
Only docs/rounds/007-canonical-capture-guard/worker.md differs between them.
Observed on 2026-10-05 with Python 3.9.6 and a local clang++ compiler.

## Independent result

The original conditional key fixture now produces CLI exit 1, zero stdout
bytes, and the expected unsupported-preprocessor error. The nested decoy plus
global namespace alias instead produces successful incorrect capture. The
synthetic C++ header compiles, and its actual canonical reference resolves to
a different key than capture reports. This is a blocking round 007 acceptance
failure, independent of green tests and CI. Round 007 is superseded, not accepted.

## Reproducible diagnostic

Command, using the inherited round 007 implementation plus the new diagnostic:

```text
python3 docs/rounds/008-canonical-namespace-boundary/attachments/reproduce_namespace.py --compile-cpp
API fields: {"Enable First Person Shooter Mode": "Bool", "First Person Shooter - Movement Enabled By Default": "Bool", "Toggle First Person Shooter Movement": "Hotkey"}
CLI exit: 0 stdout bytes: 1067 stderr: ''
Actual global ConfigKeys::Demo_Setting resolves to Replacement Key.
Compile exit: 0 stderr: ''
Native C++ resolution exit: 0 stdout: 'Replacement Key\n'
```

Diagnostic exit: 0. This diagnostic prints observed results; its own exit is
not a passing parser assertion. The CLI's exit 0 and nonempty JSON are the bug.
Compilation and execution use only a generated tiny C++ probe, never upstream
binaries or games. Verifier should independently construct related probes.

## Other checks already run

At the complete round 007 delivery:

```text
python3 -m pytest tests/test_schema_capture.py -q
42 passed in 0.22s
exit 0

python3 -m pytest tests/ -q
245 passed in 4.99s
exit 0
```

With this corrective brief and diagnostic added, before committing:

```text
python3 tools/fw.py check
0 error(s), 0 warning(s)
exit 0

python3 -m ruff check .
All checks passed!
exit 0
```

No production code, prior seat record or framework file was changed by Brain.
These results establish the need for correction, not acceptance or merge safety.
Actual game boots, runtime applicability and per-game exports remain unverified.
