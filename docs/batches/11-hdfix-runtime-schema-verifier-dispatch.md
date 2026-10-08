# Batch 11: exact-commit Verifier dispatch

Brain preliminary review found no blocking code issue. Native validation remains outstanding. Send this to a separate Verifier seat.

```text
MGS Master Collection Mod Kit · BATCH 11-hdfix-runtime-schema · Verifier

Review PR #17 at the exact Worker delivery commit fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c, against main 90967b9068125d2e7c0ceac8f6c9d60808a45c95.

Start with python3 tools/fw.py status. Read AGENTS.md, docs/agents/FRAMEWORK.md, your Verifier card and docs/state.md. Use an isolated seat and preserve other checkouts and uncommitted work. This seat may run on the M1 MacBook Pro; do not assume Windows or Steam Deck access.

Read the real diff before the Worker summary. Read the immutable planning brief with git show d51a8fde5bdd3a0288ac96ecb9a015543602f265:docs/batches/11-hdfix-runtime-schema-brief.md.

Independently authenticate MGSHDFix 4.1.0 source and derive the complete runtime settings requirements, Config Tool saving behavior, types, choices and defaults. Challenge hidden game controls, the three added keys, fixture assumptions and changed source hashes. Review migration against actual historical settings, supported custom preferences, malformed and partially migrated files, preview non-mutation, transactional rollback and original backup preservation.

Run the complete offline suite, Ruff, compilation and framework check/status. Independently verify both shortcut tags and SHA256, Windows CRLF, Python/desktop LF and unchanged mod pins. Run relevant UPGRADING checks and desktop-file validation where available. Record actual commands, outputs, exit codes, host and reviewed SHA.

Distinguish static/source evidence, reviewed Worker evidence and independently observed native results. Missing Config Tool exports, Windows/Deck initialization, gameplay and actual repair/removal remain NOT RUN. Inspect the native handoff for completeness. No release readiness follows from CI.

Change only docs/batches/11-hdfix-runtime-schema-review.md on worker/11-hdfix-runtime-schema. Keep prose below 500 words; include each goal's judgment, checks, limitations, findings and verdict. Findings need severity, file/line and a concrete failure path. Commit, push and return the literal review SHA and reviewed Worker SHA. Do not edit production, merge, tag or publish. Technical questions go to Brain.
```
