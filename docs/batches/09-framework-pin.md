# 09-framework-pin

Path: Small (Brain; framework provenance and planning records).

## Done

Reapplied the official adopter from immutable framework `v4.0.0` commit
`b036c761ac2af2d47e61a1b473c708f094bd4295`. The prior helper matched later
upstream main despite declaring 4.0.0. Only three wording changes and the
helper fingerprint are corrected; no framework copy was edited by hand.
Committed the Checked release-validation prompts and a reproducible source
comparison. Installer, shortcuts, mod pins and settings are unchanged.

## Checked

macOS, Python 3.9.6, Ruff 0.15.12. Every command below exited 0.

At `b93eaaaf8730b4e03a164fe9a432ebcc85aadbf1`:

```text
python3 -m pytest tests/ -q
273 passed in 6.07s
python3 -m ruff check .
All checks passed!
python3 -m py_compile tools/fw.py install.py
(no output)
python3 tools/fw.py check
0 error(s), 0 warning(s)
python3 tools/fw.py status
(output excerpts)
  pinned to agentic-framework 4.0.0
  up to date with the latest release (4.0.0)
  all project checks pass
```

At `7f2bab4be20244ad8292ab9266c359542c06e569` (adds only the comparison attachment):

```text
python3 docs/batches/09-framework-pin/attachments/verify_source.py <clean-v4.0.0-checkout>
docs/agents/FRAMEWORK.md matches immutable release and manifest
docs/agents/roles/brain.md matches immutable release and manifest
docs/agents/roles/worker.md matches immutable release and manifest
docs/agents/roles/verifier.md matches immutable release and manifest
tools/fw.py matches immutable release and manifest
tests/test_framework.py matches immutable release and manifest
Python 3.9 syntax valid
Installer and both shortcuts unchanged
Checked commit: 7f2bab4be20244ad8292ab9266c359542c06e569
python3 -m ruff check .
All checks passed!
python3 -m py_compile tools/fw.py install.py
(no output)
python3 tools/fw.py check
0 error(s), 0 warning(s)
git diff --check origin/main HEAD
(no output)
```

`<clean-v4.0.0-checkout>` replaces the local temporary source path; the script
checks its literal commit and clean state. Reviewed the complete diff: helper
wording, manifest fingerprint, this record, source comparison and next prompts.

## Not checked

Real game boots, Windows/Deck GUI and cancellation, Nexus audio, large-original
Steam restoration, and real-machine concurrency remain release dependencies.
Source comparison is independent of the manifest's internal self-consistency.

## Failed or blocked

No correction check failed. Hardware access is pending for batch 10. This
housekeeping change does not establish release readiness or authorize a tag.
