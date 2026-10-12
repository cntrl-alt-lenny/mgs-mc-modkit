# 12-install-plan-engine — Verifier

Reviewed PR #22 at literal `c3ecd64a7a3a3a3e8994a77511bb1585b3ec04a9`, from an isolated detached seat. Dispatch: Brain `cef5164c4656332ea8e256b11746d6abd24ad9a0`. Read rules, state, original brief/interface, correction and disposition; fetched origin; inspected full production diff before Worker summary.

## Findings and verdict

**BLOCKER — incomplete transaction-path preflight**, `install.py:3973–3975`. Existing regular files at MGS3's `mgs-modkit/staging`, `rollback` or `backups` pass preparation. Execution commits MGS1/MGS2 before MGS3 raises `NotADirectoryError`. The latter is restored, but a knowable invalid destination escaped all-game validation. Check directory types and required recovery/backup ancestors before any game commits.

**BLOCKER — cached identity expires before use**, `install.py:4114–4119,4144–4145`; `install_plan.py:113–118`. Hashes are checked once before execution. Replacing MGS3's cached ZIP after MGS1 commits installs unconfirmed ASI bytes, with every outcome “installed and verified.” Locks protect game directories, not cached sources. Replay must retain authenticated payload identity through each use.

Verdict: **corrections required; not accepted**. No production edits, merge, tag or publication.

| Goal | Judgment / evidence |
|:--|:--|
| All-game preparation and sandbox | Partly met; invalid late payload leaves all games unchanged; transaction-path finding blocks completeness. Preparation never constructs live InstallTxn. |
| Identity | Selection correction met; confident/uncertain replacement refused with original acceptance retained. Cache finding blocks execution identity. |
| Review/settings/reset, classification/consent | Actual journey coverage passed; changed classification/confirmation bytes refuse; unchanged accepted uncertainty executes without prompts. |
| Locks, stale inputs, recovery | Stable order inspected; concurrent refusal, pending recovery and stale-input tests pass without live writes. |
| Space/order/cancellation/outcomes | Shared-root-volume aggregation, component overlaps/order, cancellation, completed/restored/unstarted tests pass. Separate mounted child volumes not tested. |
| Legacy records / repair / removal | Independent schema-1 repair/removal restores synthetic originals; production transaction/recipe contracts unchanged. |
| Standalone/parity | Isolated import without adjacent module, parity, non-writing sync and bad-marker tests pass. |

## Checks at reviewed SHA

Commands ran in the isolated repository root. Outputs below are actual; scripts were temporary verifier probes. Finding reproducer is preserved below.

| Exact command | Output/result | Exit |
|:--|:--|:--|
| `python3 tools/fw.py status` | Initial main clean; isolated seat detached, checks pass; unrelated Batch 14 seat has unpushed/uncommitted work, preserved | 0 |
| `git fetch origin` | no output | 0 |
| `python3 -m pytest tests/ -q` | `335 passed in 13.97s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py` | no output | 0 |
| `python3 tools/embed_install_plan.py --check` | `OK: standalone plan matches authoritative source` | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `PYTHONPATH=.:tests python3 -m pytest -p conftest /tmp/mgs-b12-verifier/probes.py -q -s` | Initial: `1 failed, 9 passed in 2.42s`; rollback obstruction needed an existing destination to exercise snapshot creation. Corrected fixture: `10 passed in 1.53s`, including both counterexamples | 1, then 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs-b12-verifier/reproduce.py` | staging/rollback/backups: `NotADirectoryError`, MGS1/2 installed, MGS3 restored; cache: all installed, unconfirmed bytes present | 0 |
| `python3 /tmp/mgs-b12-verifier/identity.py` | Independent regex/hash/byte assertions: both tags `v2.3.0`, SHA256 `64a8a44300b247796da988b40a0d37c734cdac6cb9d02389e0c99a041741e3ea`; CMD CRLF, desktop/Python LF; three changed Python files parse with `ast.parse(..., feature_version=(3,9))` | 0 |
| Same identity script, AST comparison with `git show 85697bd:install.py` | 47 uppercase constants (pins/GAMES/template/schema included) and 11 transaction/lock/recovery/removal/recipe definitions unchanged | 0 |
| `gh pr view 22 --json headRefOid,headRefName,baseRefName,url,statusCheckRollup` | head matches literal reviewed SHA; four CI jobs SUCCESS | 0 |
| `gh api repos/cntrl-alt-lenny/mgs-mc-modkit/actions/runs/37927964314` | `head_sha` matches reviewed SHA; `conclusion: success` | 0 |
| `gh run view 37927964314 --log` | Linux 3.9/3.11/3.12: 335 passed; desktop validation command passed; Windows `333 passed, 2 skipped in 46.01s`, job SUCCESS | 0 |

| `git diff --cached --check`; `python3 tools/fw.py check` (review document) | no whitespace errors; `0 error(s), 0 warning(s)` | 0 |

Native licensed game boots, real audio compatibility, real install/repair/removal, GUI and Config Tool exports: **NOT RUN**. Local Python 3.9 runtime and `desktop-file-validate` unavailable; exact-head CI supplies those checks. UPGRADING archive/layout/settings checks were synthetic; no pin upgrade or live archive authentication claimed. MGS4 integration is separate.

## Finding reproduction

Save this as `/tmp/mgs-b12-verifier/reproduce.py`; run the exact command above. It uses existing fixture builders and real preparation/execution; mutation between game commits simulates a concurrent cached-file writer.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pytest import MonkeyPatch
import install
from conftest import mod_zips, patch_download, build_zip
from test_install_plan import world, snapshot
for case in ('staging','rollback','backups','cache'):
    with TemporaryDirectory() as td, MonkeyPatch.context() as mp:
        root=Path(td)
        patch_download.__wrapped__(mp,mod_zips.__wrapped__(root))
        found,opts=world(root); last=found['mgs3'][0]
        if case!='cache':
            records=last/install.MODKIT_DIRNAME; records.mkdir()
            (records/case).write_bytes(b'obstruction')
            (last/'winhttp.dll').write_bytes(b'original')
        before=snapshot(found)
        plan=install.build_install_plan(found,opts,{})
        workspace=root/'workspace'; workspace.mkdir()
        adapter=install.CurrentRecipeAdapter(lambda _:None)
        prepared=install.prepare_plan(plan,adapter,workspace)
        outcomes=dict.fromkeys(found,'not started')
        if case=='cache':
            real=adapter.execute
            def execute(game,index,outcomes):
                real(game,index,outcomes)
                if index==0:
                    cached=Path(prepared.games[2].identities[-1][0])
                    build_zip(cached,{'plugins/MGS3-Community-Bugfix-Compilation.asi':b'UNCONFIRMED'})
            adapter.execute=execute
        try: install.execute_plan(prepared,adapter,outcomes)
        except OSError as exc: print(case,type(exc).__name__)
        assert outcomes['mgs1']==outcomes['mgs2']=='installed and verified'
        if case=='cache':
            assert (last/'plugins/MGS3-Community-Bugfix-Compilation.asi').read_bytes()==b'UNCONFIRMED'
        else: assert snapshot(found)['mgs3']==before['mgs3']
        print(case,outcomes)
```
