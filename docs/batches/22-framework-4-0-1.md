# Batch 22: Framework 4.0.1

## Done

Brain applied the official Framework 4.0.1 updater on the Small path in an isolated seat. The owner authorized this framework update; MGS4 acceptance and other open PRs remain separate.

Source: `cntrl-alt-lenny/agentic-framework`, clean exact tag `v4.0.1`, commit `06a7d45e45751c40809d6644ea4503ec61cef709`. Implementation: `6ae8d5a14f8271fb80265acfb917cdbdcecaed9d`, based on main `bd8546524886614a04f5629b1fbbf1f741b73163`.

The update changes the manifest release/fingerprint and upstream wording in `tools/fw.py`. Installer behavior, shortcuts, mod pins, project rules, role cards, state and framework options are unchanged. No adapter or hook was added.

## Checked

Actual commands, output and exit codes at the implementation commit are in [checks.txt](evidence/22-framework-4-0-1/checks.txt); the updater transcript is in [adoption.txt](evidence/22-framework-4-0-1/adoption.txt).

- Full offline suite: 326 passed, exit 0.
- Ruff, compilation, framework check/status and diff whitespace check: exit 0; framework check reports zero errors/warnings.
- All six framework copies match the official source and their recorded SHA-256 fingerprints. Comparison helper retained in [comparison-script.txt](evidence/22-framework-4-0-1/comparison-script.txt).
- Project-owned files and both shortcuts match the main baseline byte for byte. Framework options/settings are unchanged; updated Python parses with the Python 3.9 grammar.
- Repeating the official update as a dry run reports nothing to do, exit 0.

Final delivery CI and Brain's final-head review must be green before merge. This Small batch needs no Worker or Verifier dispatch.

## Not checked

Native Windows/Steam Deck gameplay and GUI behavior were not exercised. This framework-only change does not establish MGS4 acceptance or remove its release gates.

## Failed or blocked

An initial temporary comparison helper used `.bat` instead of the repository's `.cmd` shortcut name and exited 1 when reading the nonexistent baseline path. Correcting the helper produced the recorded passing comparison; no product file changed to resolve it. No implementation blocker remains.
