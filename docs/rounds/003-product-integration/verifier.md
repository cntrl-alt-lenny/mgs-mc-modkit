<!-- fw-report
round: 003-product-integration
role: verifier
branch: verifier/003-product-integration
head: 95f1b2fb7a08938c048ef7855285a7a97249d3a0
os: macOS 27.0
python: 3.9.6
written: 2026-10-03T18:39:36Z
-->
# Verifier report: 003-product-integration

Reviewed delivery: `95f1b2fb7a08938c048ef7855285a7a97249d3a0`.
Merged adoption baseline: `e5c50788b15bed5bf43e6a52529ebb0067f9a9b1`.
Reviewed product source: `7630a81a04abf4e7f96dd75663bae70ba31c4f2e`;
its original baseline is `e6aed3da73c3d02ed7f2795d2c6567ceabae55a9`.
Local checks ran against the literal reviewed delivery on macOS/Python 3.9.6.
The first pass reviewed the diff, source bytes, tests, release limitations and
CI checkout logs before opening this round's Worker report. Pass two compared
that report with the established evidence. Only this report is written by this
seat; existing seats, implementation and framework files are preserved.

## Findings

No product integration BLOCKER found.

- [SHOULD FIX] `docs/rounds/003-product-integration/worker.md:209` and PR 5's
  validation paragraph misattribute pull-request CI's actual tested commit.
  The report calls for a final-head run with its exact SHA; the PR subsequently
  says run `37144479909` passed at the literal delivery and its logs confirmed
  the tested commit. The actual checkout logs instead show
  `HEAD is now at f731fe1 Merge 95f1b2fb7a08938c048ef7855285a7a97249d3a0 into e5c50788b15bed5bf43e6a52529ebb0067f9a9b1`, followed by
  `f731fe1b636736c36c64ff5dbd0e66b0a03d0910` from git log.
  Run metadata's `headSha` identifies the PR head, not the checkout. Treating
  it as proof of exact-head execution can accept a different tested commit.
  This is an evidence attribution problem, not a product failure: fetching
  that synthetic merge and diffing it against the delivery gives an empty
  diff. The Verifier also dispatched direct branch CI run `37144808531`, whose
  checkout logs show the literal delivery in every job and whose tests pass.
  Correct the PR's attribution to the direct run and preserve this distinction
  in subsequent evidence. No Worker report or PR text was edited by this seat.

### Acceptance criteria

1. Met for the implementation and existing Worker report. All 40 tracked files
   from the reviewed product source are byte-identical in the delivery; there
   are no focused product corrections to account for. Every other path belongs
   to adoption or round records. The Verifier report completes this round's
   report set through the required report command; delivery is checked after
   pushing. Report freshness does not transfer acceptance to unreviewed code.
2. Met. The complete offline suite passes 203 tests, including framework
   hygiene and all seven queued-cancellation/reset regression cases. These
   cases inspect cancellation events, actual mod/settings/launcher bytes,
   persisted manifest preferences and truthful dialogs; the end-to-end cancel
   case compares the complete pre/post file inventory. They are preserved
   regressions that caught the initial reviewed defects, not new integration
   tests that merely restate the implementation.
3. Met. Installer pins, mod URLs/checksums, configuration schema and captured
   fixture are preserved through whole-file comparison. Both shortcuts match
   kit tag `v2.3.0` and installer SHA-256
   `a0bed642eb5b8c7a2c6521876e498f71ef8359b20927b5733e83fdb7eb22d7e5`.
   Windows CRLF is preserved. All six framework-owned files match the clean
   pinned source and manifest hashes; all adoption manifest paths, the manifest,
   project guidance and state file match the merged adoption baseline.
4. Met with independently supplied exact-head evidence. Direct run
   `37144808531` checked out `95f1b2fb7a08938c048ef7855285a7a97249d3a0`
   in all four jobs. Linux Python 3.9/3.11/3.12 each passed 203 tests, Ruff,
   compilation and desktop validation. Windows Python 3.12 passed 201 tests
   with the two privileged symlink tests skipped. The prior PR run also passed,
   but its actual checkout was the identical-tree synthetic merge above.
5. Met for the automated-versus-hardware distinction; CI attribution should be
   corrected as described above. PR 5, Worker limitations and docs/RELEASING.md
   plainly retain real Windows/Deck boots, native GUI cancellation, actual
   Nexus audio compatibility, large-audio Steam restoration and real-machine
   concurrent-installer smoke tests. No synthetic fixture proves game/audio
   compatibility. Release gates were inspected, not exercised by publication.
6. Met for this seat's actions and the delivered Git delta: no merge, tag,
   release, upstream pin bump or repository-setting change was performed.
   PR 2 remains the separate candidate. Historical claims about all external
   actions are limited to observable Git/PR evidence, not an account audit.

### Independent commands and actual results

Every command listed here exited 0 unless explicitly stated otherwise.
Arguments `<framework>` and `<independent-probes.py>` denote temporary local
resources; no personal path or account detail is retained in this report.

- `git fetch origin`; `git worktree add --detach .worktrees/verifier-003 origin/main`:
  `HEAD is now at e5c5078 Merge pull request #4 from cntrl-alt-lenny/verifier/002-framework-adoption`.
- `python3 tools/fw.py start --role verifier --round 003-product-integration`:
  `seat ok: verifier, round 003-product-integration, branch verifier/003-product-integration at 95f1b2fb7a08`;
  `reviewing exactly 95f1b2fb7a08938c048ef7855285a7a97249d3a0 from origin/worker/003-product-integration`.
- `git diff --stat origin/main HEAD`: 26 paths; product delta plus this round's
  brief, Worker report and source-check attachment. Source comparison lists
  only additions when comparing against the reviewed product source.
- Independent Python assertions enumerated `git ls-tree -r --name-only` at
  the product source and compared each local file with `git show <source>:<path>`:
  `Product comparison: 40 files byte-identical`.
  Separate assertions compared all manifest paths with the adoption baseline,
  every copy with the pinned checkout and its SHA-256, and parsed both shortcut
  pins against installer bytes: six framework `MATCH` results, both launcher
  `MATCH v2.3.0` results and `Windows CRLF verified`.
- `python3 docs/rounds/003-product-integration/attachments/verify_sources.py <framework>`:
  `All 40 product files match reviewed source 7630a81a04abf4e7f96dd75663bae70ba31c4f2e`;
  six `Framework source/fingerprint match` lines;
  `All adoption manifest paths and the manifest match merged baseline`;
  `Python 3.9 installer syntax valid`;
  both shortcuts print the tag/digest stated above. The attachment independently
  checks the clean framework commit is
  `eca1306dc43cb81f0df3ee42f841812da68e8b1e`.
- `git diff --exit-code origin/main HEAD -- AGENTS.md docs/state.md docs/agents tools/fw.py tests/test_framework.py`:
  no output. No state sentences added or removed.
- `python3 tools/fw.py check`: `0 error(s), 0 warning(s)`.
- `python3 tools/fw.py status`: pin `3.1.0`, merge rule `owner-approves`,
  Worker reported at `84fbdfd94ef5`, Verifier started with no report yet,
  all project checks pass; next action is wait for this Verifier.
- `python3 -m pytest tests/ -q`: `203 passed in 8.07s`.
- `python3 -m ruff check .`: `All checks passed!`.
- `python3 -m py_compile tools/fw.py install.py`: no output.
- `python3 --version`: `Python 3.9.6`; `python3 -m ruff --version`: `ruff 0.15.12`.
  Native Linux CI separately used the pinned Ruff 0.15.13.
- Targeted pytest selection of
  `test_zenity_exit_with_queued_update`,
  `test_zenity_cancel_status_arrives_after_pipe_failure`,
  `test_reset_then_choices_match_review_manifest_and_files`, and
  `test_zenity_queued_cancel_restores_install_and_reports_cancellation`:
  `7 passed in 1.37s`.
- `PYTHONPATH="$PWD:$PWD/tests" python3 -m pytest -p conftest <independent-probes.py> -q`:
  `3 passed in 0.59s`. These temporary independent probes, used previously for
  the product review and now imported against this combined installer, verify:
  (a) a child process exits after the first restore, leaving unchanged journal
  and both snapshots, then retry restores the entire original inventory;
  (b) cancellation stops a partially extracting blocked child, then restores a
  prior live write with cancellation still set;
  (c) failed repair plus injected sharing violation reports recovery incomplete,
  preserves the prior manifest, stock backup and every pre-run snapshot, and
  retry restores custom language/render settings before uninstall restores stock.
  The harness is not committed; these are additional observed fault probes,
  not extra cases claimed in the repository's 203-test suite.
- `git -c core.whitespace=cr-at-eol diff --check origin/main HEAD`: no output.
- `python3 tools/fw.py delivery --round 003-product-integration` before reporting:
  `origin/verifier/003-product-integration (95f1b2fb7a08): delivered`;
  `worker: report describes 84fbdfd94ef5`.
- `gh run view 37144479909 --log`: successful; checkout is
  `f731fe1b636736c36c64ff5dbd0e66b0a03d0910`, with the passing results described
  in the finding. `git fetch origin f731fe1b636736c36c64ff5dbd0e66b0a03d0910`
  followed by `git diff --exit-code 95f1b2fb7a08938c048ef7855285a7a97249d3a0 f731fe1b636736c36c64ff5dbd0e66b0a03d0910`:
  no output, proving an identical tree.
- `gh workflow run ci.yml --ref worker/003-product-integration`:
  created direct run `https://github.com/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37144808531`.
- `gh run view 37144808531 --json headSha,status,conclusion,jobs`:
  `headSha: 95f1b2fb7a08938c048ef7855285a7a97249d3a0`,
  `status: completed`, `conclusion: success`, all four jobs successful.
- `gh run view 37144808531 --log`: each job's fetch and git log confirm that
  literal SHA, with actual result excerpts:

```text
test (3.9): All checks passed!; 203 passed in 4.80s
test (3.11): All checks passed!; 203 passed in 4.28s
test (3.12): All checks passed!; 203 passed in 11.10s
test-windows: 201 passed, 2 skipped in 14.36s
```

  Linux desktop validation and byte compilation steps completed successfully.
  The Windows skips are `test_symlink_member_rejected` and
  `test_symlinked_dir_rejected`, marked for Windows privilege limitations.

### Worker report comparison

After the blind first pass, read the complete Worker report. The product
integration accounting, unchanged framework/state guidance, source comparisons,
203-test result, lint/compilation and explicit hardware limitations agree with
independent evidence. Changes after its implementation evidence commit are
this round's report only; delivery considers its stamp current. The substantive
exception is exact-head CI attribution: metadata alone does not prove the
checkout, as the independently inspected logs demonstrate. The direct run now
supplies the missing literal-SHA evidence without altering delivery files.

## Not verified

- Real Windows and Steam Deck/Proton game boots, native GUI progress/cancel,
  actual Nexus audio payload compatibility, large-audio Steam verification
  cleanup and concurrent installers on real machines remain outstanding.
  Synthetic mod files, archive-shaped fixtures and native CI do not prove them.
- Live upstream mod release/schema compatibility and real archive contents were
  not revalidated or downloaded in this integration round. All reviewed source
  pins, schema definitions and capture fixture are preserved; no upgrades occur.
- Release/tag publication gates were read, not triggered. No v2.3.0 release was
  published or tag created. Repository protections/account settings and the
  owner's historical approval conversation were not independently audited.
- The temporary fault-probe harness is not a durable round attachment; the
  committed tests remain the reproducible baseline. Brain may rerun those
  committed recovery/settings/responsive-install tests to re-derive behavior.
- Brain acceptance and owner merge/release approval are outside this seat.

## Verdict

High confidence that this is a faithful integration at the exact reviewed
Worker delivery: product bytes and adoption fingerprints are preserved, the
combined offline suite passes, and literal-head Linux/Windows CI now passes.
No product blocker was found. The one SHOULD FIX is an evidence-attribution
correction in the PR/Worker CI narrative; this report records both actual
checkout commits and supplies the correct direct-run evidence. Hardware release
requirements remain open. This informs Brain's decision; it is not approval to
merge or publish. Only the Verifier report is committed by this seat.
