# 14-mgs4-patriotfix: combined independent Verifier review

Reviewed PR #19 at literal **868bebf712a7c11edcecd8b3afc636291a379cc4** on 12 October 2026. Dispatch: Brain `675ba20ceaf416163dc2765ba0b7d2c8f5ad5fb7`. Started with framework status, read rules/card/state and complete dispatch/briefs/dispositions, fetched origin, used an isolated detached seat, and inspected the full production diff before the Worker summary. Original review remains in Git at `38ef1b6a679411d48b784a8142aed797ae170117`; all historical evidence files are untouched.

## Findings and verdict

**BLOCKER — malformed late manifest settings escape all-game preparation**, `install.py:4298–4303`, reaching `install.py:2240` only during replay. A schema-1 MGS4 record with valid game/file/mod lists but `settings: null`, `42`, or `["invalid"]` passes options collection and preparation. Execution commits MGS1–3, then MGS4's constructor raises `CorruptManifestError` converting settings to a dict. MGS4 remains unchanged; the earlier commits are real. Preparation must validate every record assumption consumed by the live constructor, including settings, before any selected game writes. The independent reproducer below confirms all three cases.

Both original Batch 12 blockers are corrected: regular-file recovery directories and unusable live/backup ancestors now refuse before transactions; private replay copies retain confirmed archive identity through copying/extraction. Original MGS4 legacy-removal and compiled-header authentication findings are corrected.

Verdict: **corrections required; BLOCKED for acceptance**. No production edits, acceptance, merge, tag or publication. Brain decides disposition.

| Goal | Judgment / evidence |
|:--|:--|
| Collection/confirmation/all-game preparation | Partly met; late payload/settings/layout/loader/orphan failures leave every game unchanged; malformed manifest-settings blocker remains |
| Audio/custom settings | Met offline: confident/explicit-uncertain selection identity refuses replacement; real journey classification/confirmation/review/reset coverage passes; custom/hidden values preserved |
| Replay identity/no interaction | Met: post-commit cache mutation and copy mutation refuse; original-source mutation during extraction installs authenticated bytes; no downloads, picking, confirmation or settings regeneration |
| Locks/stale inputs/recovery | Stable sorted lock order inspected; concurrency, settings/saves/record/payload drift and pending recovery refuse; unsafe save journal tests pass |
| Space/cancellation/outcomes | Shared-game and separate-cache device thresholds pass; cancellation preserves completed/restored/unstarted outcomes; mounted child volumes not exercised |
| Saves/oldest backups/repair/removal | Met in disposable fixtures, including actual PatriotFix bytes, old schema records, custom settings, unowned ASI and oldest originals |
| Official identity/settings | Steam app [2492670](https://store.steampowered.com/app/2492670/); fresh official tag/tree/archive verified; exact inventory, 28 fields/24 runtime reads, hidden PW serialization and conservative defaults independently inspected |
| Existing games/standalone/docs | MGS1–3 pins/schema/recipes unchanged; deterministic embedding and isolated standalone import pass; one MGS4 README row and unpublished-checkout/published-shortcut distinction verified |

## Checks at the reviewed SHA

All commands ran from the isolated repository root unless stated. Temporary scripts are reproduced below. No upstream binary was executed.

| Exact command | Actual output/result | Exit |
|:--|:--|:--|
| `python3 tools/fw.py status`; `git fetch origin` | main clean; isolated detached seat clean, all project checks pass; fetch silent | 0 each |
| `python3 -m pytest tests/ -q` | `408 passed in 18.73s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py tools/capture_patriot_schema.py` | silent | 0 |
| `python3 tools/embed_install_plan.py --check` | `OK: standalone plan matches authoritative source` | 0 |
| `git -c core.whitespace=cr-at-eol diff --check` (review document) | silent; only the authorized review file changed | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `python3 --version` | `Python 3.9.6`; full local suite actually uses 3.9 | 0 |
| `command -v desktop-file-validate` | unavailable locally; exact-head Linux CI runs it successfully | 1 |
| `git clone --depth 1 --branch 0.2.2 https://github.com/ShizCalev/MGSPatriotFix.git /tmp/mgs14-final-verifier/patriot` | detached at `c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de` | 0 |
| `curl -fL https://github.com/ShizCalev/MGSPatriotFix/releases/download/0.2.2/MGS4_MGSPatriotFix_0.2.2.zip -o /tmp/mgs14-final-verifier/patriot.zip` | 9862 KiB downloaded | 0 |
| `python3 docs/batches/evidence/14-mgs4-patriotfix-correction/source-audit.py /tmp/mgs14-final-verifier/patriot` | literal Git blobs plus declared CRLF match all 61 inputs; live tag agrees; clean capture equals fixture; only three header hashes added versus original | 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/actual-archive.py /tmp/mgs14-final-verifier/patriot.zip` | official SHA `4f8fa5dd493c9d5d023fd4dfdcad39a2259b2aedf02685840751c263f497a6b1`; four-game zero-write preparation, no-network/writer replay, repair/removal/oldest custom settings/save/unowned ASI PASS | 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/verify-integration.py` | 16 original recipes/safety definitions unchanged; engine/embed/audio tests equal Batch 12 input; original review/capture unchanged; README PASS | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/probes.py` | `PASS 11 independent failure/identity/outcome probes`; output below | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/record.py` | all three malformed settings escape preparation, MGS1/2/3 installed, MGS4 unchanged; `CONFIRMED late malformed manifest settings escapes preparation` | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/audio.py` | confident and explicitly uncertain replacements refuse for combined four-game plan | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/space.py` | device 1 or 2 one byte below required refuses; exact thresholds pass; simulated devices only | 0 |
| `PYTHONPATH=. python3 /tmp/mgs14-final-verifier/identity.py` | 61 modified/omitted inputs and added header refuse; clean recapture; both v2.3.0 shortcuts SHA `f797e85222e85f521dee199bacdc01dd2764259c531bed5100f8879704cea06c`, CMD CRLF/desktop-Python LF; 3.9 grammar; MGS1–3 constants AST-equal | 0 after repair |
| Same identity script, initial attempt | source/shortcut checks passed; verifier's `ast.literal_eval` cannot handle URL f-string; changed to AST comparison, rerun passed | 1 |
| `git clone --depth 1 --branch v4.0.0 https://github.com/cntrl-alt-lenny/agentic-framework.git /tmp/mgs14-final-verifier/framework`; `python3 /tmp/mgs14-final-verifier/framework.py` | six installed copies byte-equal pinned source and fingerprints | 0 each |
| Initial inline framework comparison | four cards passed; verifier used wrong upstream test-template location; corrected to `templates/tests/test_framework.py`, rerun passed | 1 |
| `python3 tools/refresh_checksums.py` | all five live official release-asset SHA-256s match the unchanged installer pins | 0 |
| `python3 tools/check_pins.py` | PatriotFix/Bugfix pins current; advisory HDFix 4.1.2 and M2Fix v3.7.3 available; no upgrades made | 1 (advisory) |
| `gh pr view 19 --json headRefOid,headRefName,baseRefName,statusCheckRollup` | literal head matches, four jobs SUCCESS | 0 |
| `gh run view 38218395168 --json headSha,conclusion,jobs`; `gh run view 38218395168 --log > /tmp/mgs14-ci.log` | exact head, success; Linux 3.9/3.11/3.12: 408 passed; Windows: 406 passed, 2 skipped; lint/compile/desktop validation passed | 0 each |

Native Config Tool exports, GUI, ASI initialization, licensed Windows/Deck boots/gameplay, DS3/flashbacks, real user audio and real-device restoration: **NOT RUN**. Bounded source capture excludes build projects/resources/dependencies/binaries. Synthetic probes and CI do not remove the native handoff gates.

## Reproducible temporary verifier scripts

Save each fenced script under `/tmp/mgs14-final-verifier/` with its stated filename; commands above use the reviewed checkout and its fixture builders.

### record.py

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pytest import MonkeyPatch
import json,install
from conftest import mod_zips,patch_download
from test_mgs4_plan import combined,prepare
from test_install_plan import snapshot
for bad in (None,42,['invalid']):
 with TemporaryDirectory() as td, MonkeyPatch.context() as mp:
  base=Path(td);mp.setattr(install,'TAR',install.find_tar());mp.setattr(install,'app_data_dir',lambda:base/'app')
  patch_download.__wrapped__(mp,mod_zips.__wrapped__(base))
  found,options=combined(base);last=found['mgs4'][0]
  record=last/install.MODKIT_DIRNAME/install.MANIFEST_NAME;record.parent.mkdir()
  record.write_text(json.dumps({'schema':1,'game':'mgs4','added':[],'overwritten':[],'mods':{},'settings':bad}))
  options['mgs4']=install.options_for_game('mgs4',found['mgs4'],options['mgs4'],lambda _:None)
  before=snapshot(found);adapter,prepared=prepare(base,found,options)
  outcomes=dict.fromkeys(found,'not started')
  try:install.execute_plan(prepared,adapter,outcomes)
  except install.CorruptManifestError as e:print('settings',bad,type(e).__name__,outcomes)
  else:raise AssertionError('expected record refusal')
  assert outcomes['mgs1']==outcomes['mgs2']==outcomes['mgs3']=='installed and verified'
  assert snapshot(found)['mgs4']==before['mgs4']
print('CONFIRMED late malformed manifest settings escapes preparation')
```

### probes.py

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pytest import MonkeyPatch
import install
from conftest import mod_zips, patch_download, build_zip
from test_mgs4_plan import combined, prepare
from test_install_plan import snapshot

cases = ['staging','rollback','backups','live-parent','backup-parent','cache-after-commit','copy-race','source-during-extract','late-settings','late-loader','cancel']
for case in cases:
    with TemporaryDirectory() as td, MonkeyPatch.context() as mp:
        base=Path(td)
        mp.setattr(install,'TAR',install.find_tar())
        mp.setattr(install,'app_data_dir',lambda:base/'app')
        patch_download.__wrapped__(mp,mod_zips.__wrapped__(base))
        found,options=combined(base); last=found['mgs4'][0]
        if case in ('staging','rollback','backups'):
            records=last/install.MODKIT_DIRNAME; records.mkdir()
            (records/case).write_bytes(b'obstruction')
        if case=='live-parent': (last/'MGS4/scripts').write_bytes(b'obstruction')
        if case=='backup-parent':
            p=last/install.MODKIT_DIRNAME/'backups/MGS4'; p.parent.mkdir(parents=True);p.write_bytes(b'obstruction')
        if case=='late-settings': options['mgs4']['patriot_filtering']=0
        if case=='late-loader': (last/'MGS4/winmm.dll').write_bytes(b'unowned loader')
        before=snapshot(found)
        if case in ('staging','rollback','backups','live-parent','backup-parent','late-settings','late-loader'):
            mp.setattr(install,'InstallTxn',lambda *a,**k:(_ for _ in ()).throw(AssertionError('live transaction')))
            try: prepare(base,found,options)
            except (RuntimeError,ValueError,OSError) as e: print(case,type(e).__name__,'zero game writes')
            else: raise AssertionError('invalid destination accepted')
            assert snapshot(found)==before
            continue
        adapter,prepared=prepare(base,found,options)
        last_cache=Path(prepared.games[-1].identities[0][0])
        outcomes=dict.fromkeys(found,'not started')
        real=adapter.execute
        def execute(g,index,outcomes):
            real(g,index,outcomes)
            if index==0 and case=='cache-after-commit':
                build_zip(last_cache,{'MGS4/winmm.dll':b'UNCONFIRMED'})
        mp.setattr(adapter,'execute',execute)
        if case=='copy-race':
            copy=install.shutil.copyfile
            def race(src,dst,*a,**k):
                result=copy(src,dst,*a,**k)
                if Path(src)==last_cache and 'replay_' in str(dst): Path(dst).write_bytes(b'UNCONFIRMED')
                return result
            mp.setattr(install.shutil,'copyfile',race)
        if case in ('source-during-extract','cancel'):
            extract=install.InstallTxn.install_archive
            def mutate(tx,archive,**kwargs):
                if case=='source-during-extract':
                    pg=next(p for p in prepared.games if p.game.key==tx.game_key)
                    assert str(archive) not in dict(pg.identities)
                    for source,_ in pg.identities: Path(source).write_bytes(b'UNCONFIRMED')
                result=extract(tx,archive,**kwargs)
                if case=='cancel' and tx.game_key=='mgs2': raise install.CancelledInstall('independent cancel')
                return result
            mp.setattr(install.InstallTxn,'install_archive',mutate)
        try: install.execute_plan(prepared,adapter,outcomes)
        except (install.ReplanRequired,install.CancelledInstall):
            assert case!='source-during-extract'
            assert outcomes['mgs1']=='installed and verified'
            if case=='cancel':
                assert outcomes['mgs2']=='previous setup restored'
                assert snapshot(found)['mgs2']==before['mgs2']
                assert outcomes['mgs3']==outcomes['mgs4']=='not started'
            else:
                assert snapshot(found)['mgs4']==before['mgs4']
                assert outcomes['mgs4']=='not changed; inspect recovery record / lock'
        else:
            assert case=='source-during-extract'
            assert set(outcomes.values())=={'installed and verified'}
        assert not any(b'UNCONFIRMED'==b for game in snapshot(found).values() for b in game.values())
        print(case,outcomes)
print('PASS 11 independent failure/identity/outcome probes')
```

### audio.py

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pytest import MonkeyPatch
import install
from conftest import mod_zips,patch_download,FakeUI,build_audio_zip,build_mgs2_base_zip
from test_mgs4_plan import combined
from test_install_plan import snapshot
for uncertain in (False,True):
 with TemporaryDirectory() as td,MonkeyPatch.context() as mp:
  base=Path(td);mp.setattr(install,'TAR',install.find_tar());patch_download.__wrapped__(mp,mod_zips.__wrapped__(base))
  found,options=combined(base);path=base/'selected.zip'
  (build_audio_zip if uncertain else build_mgs2_base_zip)(path)
  audio=install.collect_audio_archives(FakeUI(checklist=[['mgs2:base']],files=[str(path)],yesno=[True] if uncertain else []),['mgs2'])
  accepted=audio['mgs2'][0]['acceptance'];before=snapshot(found)
  build_audio_zip(path,{'us/vox/new.sdt':b'changed'})
  assert install.sha256_file(path)!=accepted.sha256
  try:install.build_install_plan(found,options,audio)
  except install.ReplanRequired:pass
  else:raise AssertionError('acceptance rebound')
  assert snapshot(found)==before
  print('PASS confident' if not uncertain else 'PASS explicit uncertain','selection replacement refuses for combined four-game plan')
```

### space.py

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from pytest import MonkeyPatch
import install
from conftest import mod_zips,patch_download
from test_mgs4_plan import combined,prepare
with TemporaryDirectory() as td, MonkeyPatch.context() as mp:
    base=Path(td); mp.setattr(install,'TAR',install.find_tar())
    patch_download.__wrapped__(mp,mod_zips.__wrapped__(base))
    found,options=combined(base);adapter,prepared=prepare(base,found,options)
    cache=base/'workspace'; original=Path.stat
    def stat(path,*a,**k):
        real=original(path,*a,**k)
        return SimpleNamespace(st_dev=2 if cache in path.parents else 1,st_size=real.st_size)
    mp.setattr(Path,'stat',stat)
    expected={1:install.SPACE_MARGIN_BYTES+sum(g.required_bytes for g in prepared.games),2:install.SPACE_MARGIN_BYTES+sum(original(Path(s)).st_size for g in prepared.games for s,_ in g.identities)}
    for deficient in (1,2,None):
        visited=[]
        def free(path):
            device=path.stat().st_dev;visited.append(device)
            return expected[device]-(1 if device==deficient else 0)
        mp.setattr(install,'free_bytes',free)
        try:adapter.check_space(prepared)
        except RuntimeError:assert deficient is not None
        else:assert deficient is None
        print('space',deficient,'visited',visited,'requirements',expected)
print('PASS independent shared-game and separate-cache volume thresholds; simulated devices, no mounted-device claim')
```

### identity.py

```python
import ast, hashlib, json, re, subprocess
from pathlib import Path
import install
from tools.capture_patriot_schema import capture, REVIEWED
root=Path.cwd(); source=Path('/tmp/mgs14-final-verifier/patriot')
fixture=json.loads((root/'tests/fixtures/patriotfix-0.2.2-schema.json').read_text())
assert capture(source)==fixture
for name in REVIEWED:
    p=source/name; raw=p.read_bytes()
    try:
        p.write_bytes(raw+b'\r\n#error Unreviewed\r\n')
        try: capture(source)
        except ValueError: pass
        else: raise AssertionError('modified '+name)
        p.unlink()
        try: capture(source)
        except ValueError: pass
        else: raise AssertionError('omitted '+name)
    finally:p.write_bytes(raw)
p=source/'src/extra.h'
try:
    p.write_bytes(b'added')
    try: capture(source)
    except ValueError: pass
    else: raise AssertionError('added header accepted')
finally:p.unlink()
assert capture(source)==fixture
print('PASS all 61 modified and omitted C++ inputs, added header refused; clean source recaptures fixture')
digest=hashlib.sha256((root/'install.py').read_bytes()).hexdigest()
for name in ('Install-MGS-Mods.cmd','Install-MGS-Mods.desktop'):
    raw=(root/name).read_bytes()
    assert re.search(rb'TAG=v2\.3\.0',raw)
    assert re.search(rb'SHA='+digest.encode(),raw)
    assert (b'\n' not in raw.replace(b'\r\n',b'')) if name.endswith('.cmd') else b'\r' not in raw
for name in ('install.py','install_plan.py','tools/embed_install_plan.py','tools/capture_patriot_schema.py'):
    raw=(root/name).read_bytes(); assert b'\r' not in raw
    ast.parse(raw,feature_version=(3,9))
print('PASS both v2.3.0 shortcuts / '+digest+'; CMD CRLF, desktop/Python LF, Python 3.9 grammar')
old=ast.parse(subprocess.check_output(['git','show','origin/main:install.py'])); new=ast.parse((root/'install.py').read_bytes())
def constants(tree):
    return {n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['HDFIX_VERSION','HDFIX_URL','HDFIX_SHA256','M2FIX_VERSION','M2FIX_TAG','M2FIX_URL','M2FIX_SHA256','GAMES','SETTINGS_SCHEMA','SETTINGS_TEMPLATE','SETTINGS_CONSTRAINTS']}
a,b=constants(old),constants(new)
for key in a:
    if key=='GAMES':
        prior={ast.literal_eval(k):ast.dump(v) for k,v in zip(a[key].keys,a[key].values)}
        current={ast.literal_eval(k):ast.dump(v) for k,v in zip(b[key].keys,b[key].values)}
        assert all(current[g]==data for g,data in prior.items())
    else:assert ast.dump(a[key])==ast.dump(b[key]),key
print('PASS MGS1-3 pins, recipes metadata and HDFix settings constants unchanged against origin/main')
manifest=json.loads((root/'docs/agents/framework.json').read_text())
print('Framework manifest keys:',sorted(manifest))
```

### framework.py

```python
from pathlib import Path
import json,hashlib
root=Path.cwd();upstream=Path('/tmp/mgs14-final-verifier/framework')
manifest=json.loads((root/'docs/agents/framework.json').read_text())
for name,entry in manifest['files'].items():
 if entry['kind']!='copy':continue
 candidate=upstream/name
 if name.startswith('docs/agents/'):candidate=upstream/'framework'/name.removeprefix('docs/agents/')
 if name=='tests/test_framework.py':candidate=upstream/'templates/tests/test_framework.py'
 assert candidate.read_bytes()==(root/name).read_bytes(),name
 assert hashlib.sha256((root/name).read_bytes()).hexdigest()==entry['sha256']
 print('PASS pinned source copy',name)
```
