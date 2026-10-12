# 14-mgs4-patriotfix: manifest correction independent re-review

Reviewed **d9f13f4a02c3d894689bc21eac9911d619344c2c** on 12 October 2026 under Brain dispatch **62602c60845621972f032b9a9b0f8453a9e8b5d9**. Rules/card/state/brief/disposition read; origin fetched; isolated seat; correction diff inspected before Worker summary.

Verdict: **prior manifest blocker resolved; no new blocking findings**. This supersedes the historical verdict below. Brain determines acceptance; nothing accepted, merged, tagged or published. Historical review/evidence bytes follow unchanged; older verdicts remain in Git.

Native exports, GUI, ASI initialization, licensed Windows/Deck boots/gameplay, real audio and real-device restoration: **NOT RUN**. Synthetic/CI evidence cannot establish native compatibility. Source capture remains bounded, excluding build projects/resources/dependencies/binaries.

| Goal / constructor assumption | Independent judgment |
|:--|:--|
| Malformed settings and mods | Met: 128 cases, schemas 1/2, eight shapes per mapping including null/scalars/empty/malformed/convertible pair lists; each MGS1–4 last. Real collection/preparation refuses before any live constructor; complete selected files/directories/records/backups unchanged. No discarded/reset settings. |
| Valid/missing settings | Met offline: four schema-1/2 present/missing lifecycle variants; preparation non-mutating, successful replay/repair/removal, custom/hidden values, custom mods, saves, oldest backups and unowned ASI preserved; explicit backup-byte comparison across repair. Absent settings retains constructor `{}` default. |
| Record object/game/added/overwritten/paths | Shared `_read_record` and `_validate_manifest` validate object/list/path/ownership; game identity and required lists checked in preflight and constructor. List/set/path comprehensions receive validated values. |
| Mods/settings conversions | Preflight requires dictionaries, defaults absent fields to `{}`; constructor copies mappings. Values inside dictionaries remain unrestricted structurally. |
| Recovery/directories/orphans | Planning/adapter rejects pending journal; preparation validates root/staging/rollback/backups, linked backups and destination ancestors. MGS4 private recipe restricts orphan ownership; other recipes retain generic adoption. Permission/disk/concurrent races are not claimed preflight omissions. |
| Schema/transaction_id/files | No further constructor conversion; shared manifest compatibility retained. Transaction ID participates in recovery, which pending journals prevent during preparation/replay. |
| Earlier fixes / production scope | Met: entire installer AST except `_plan_validate_record` unchanged versus `03c5890`; engine/embed/audio/capture/history byte-preserved. Directory/replay/legacy-removal/header/audio probes pass. |
| Shortcuts / CI combination | Met: both unpublished v2.3.0 pins independently match SHA `3f2b0049358d31679aa5db63d630e74383be771957cf6d3edce3e32e64a39e75`; CMD CRLF, desktop/Python LF. Actual CI checkout `ab4cbe666af085f1ad39ac62fe46402f236055d4` has parents `bd8546524886614a04f5629b1fbbf1f741b73163` (merged PR #21) and literal candidate; installer/module/shortcut/embed/capture bytes equal candidate. |
| Finding: NOTE, historical audit predicate | `docs/batches/evidence/14-mgs4-plan-integration/verify-integration.py:33` compares original `c2e7ea4` review bytes; later historical reviews intentionally differ. Unmodified historical script exits 1 at that predicate, not production. Original bytes evaluated from their stated Git commit; independent current-history audit passes. |

| Exact command / inspection at literal candidate before review edit | Actual output / exit |
|:--|:--|
| `python3 tools/fw.py status`; `git fetch origin` | All project checks pass; clean detached candidate; fetch silent / 0 each |
| `python3 -m pytest tests/ -q` | `439 passed in 29.77s` / 0 |
| `python3 -m ruff check .` | `All checks passed!` / 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py tools/capture_patriot_schema.py` | Silent / 0 |
| `python3 tools/embed_install_plan.py --check`; `python3 tools/fw.py check` | `OK: standalone plan matches authoritative source`; `0 error(s), 0 warning(s)` / 0 each |
| `python3 --version`; `command -v desktop-file-validate` | Python 3.9.6 / 0; validator unavailable / 1; actual Linux CI validator succeeds |
| `python3 -m pytest tests/test_install_plan.py -q -k 'standalone or embedding or sync_check'` | `3 passed, 26 deselected in 0.55s` / 0 |
| `python3 docs/batches/evidence/14-manifest-preflight/audit.py` | Only validator changes; constructor/recovery/removal/recipes/writers unchanged; engine/embed/audio/capture/review preserved; original review ancestor / 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-preflight-verifier/records.py` | `PASS 128 schema-1/2 late settings/mods refusals; real collection/preparation; zero live constructors; all files/directories/records/backups unchanged` / 0 |
| `python3 /tmp/mgs14-preflight-verifier/legacy.py .` | Four schema/settings combinations PASS, all-game lifecycle/custom/hidden/save/oldest/unowned checks; backup-byte comparison added / 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/probes.py` | `PASS 11 independent failure/identity/outcome probes`; directory/ancestor refusal, cache/copy mutation, private extraction and cancellation preservation / 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/audio.py`; `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/space.py` | Confident/uncertain replacement refuses; shared-game/separate-cache thresholds pass (simulated devices) / 0 each |
| `python3 docs/batches/evidence/14-mgs4-patriotfix-correction/source-audit.py /tmp/mgs14-repeat-source` | Live tag `c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de`; 61 inputs/blobs/CRLF/hashes/fixture/header delta PASS / 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/actual-archive.py /tmp/mgs14-repeat.zip` | Official ZIP SHA `4f8fa5dd493c9d5d023fd4dfdcad39a2259b2aedf02685840751c263f497a6b1`; zero-write four-game preparation; authenticated replay/repair/removal/settings/saves/oldest/unowned PASS / 0 |
| `python3 /tmp/mgs14-final-verifier/framework.py` | Six pinned framework copies byte-equal source and fingerprints / 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/verify-integration.py` | Original recipe and engine assertions PASS; original report-byte predicate fails / 1; historical assertion rerun with original report from Git PASS / 0 |
| `python3 /tmp/mgs14-preflight-verifier/identity.py` | Entire AST except validator unchanged; historical bytes preserved; shortcuts/3.9/CI merge-tree equality and PR21 parent assertions PASS / 0 |
| `python3 tools/check_pins.py` | Two advisory updates (HDFix 4.1.2, M2Fix v3.7.3); other pins current / 1; no upgrade |
| `gh pr view 19 --json headRefOid,headRefName,baseRefName,url,statusCheckRollup`; `gh run view 38232687896 --json headSha,conclusion,jobs` | Exact literal head; four SUCCESS jobs / 0 each |
| `gh run view 38232687896 --log > /tmp/mgs14-preflight-ci.log`; `git fetch origin refs/pull/19/merge` | Actual checkout `ab4cbe6`; Linux 3.9/3.11/3.12 each 482 passed, Windows 480 passed/2 existing skips; lint/compile/desktop validation pass / 0 each |

| `python3 tools/refresh_checksums.py` | `All pinned checksums match the live release assets.` All five live archive SHA-256s equal unchanged pins / 0; subsequent advisory pin check exits 1 as recorded above |

| Post-edit `python3 tools/fw.py check`; `python3 tools/fw.py status`; `git -c core.whitespace=cr-at-eol diff --check`; `git diff --stat` | `0 error(s), 0 warning(s)`; all project checks pass (unrelated linked Brain seat dirty, preserved); whitespace silent; only authorized review changed / 0 each |

## Reproducible correction probes

### records.py

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from pytest import MonkeyPatch
import install
from conftest import mod_zips, patch_download
from test_mgs4_plan import combined, prepare

def full(found):
    return {key: [(p.relative_to(root).as_posix(), 'dir' if p.is_dir() else 'file', None if p.is_dir() else p.read_bytes()) for p in sorted(root.rglob('*'))] for key,(root,_) in found.items()}

count=0
for schema in (1,2):
 for key in ('mgs1','mgs2','mgs3','mgs4'):
  for field in ('settings','mods'):
   for value in (None,42,False,'invalid',[],['invalid'],[['custom','value']],[[1,2,3]]):
    with TemporaryDirectory() as folder, MonkeyPatch.context() as mp:
     base=Path(folder)
     mp.setattr(install,'app_data_dir',lambda:base/'state')
     patch_download.__wrapped__(mp,mod_zips.__wrapped__(base))
     found,options=combined(base); found[key]=found.pop(key)
     root=found[key][0]; record=root/install.MODKIT_DIRNAME/install.MANIFEST_NAME
     record.parent.mkdir()
     body=dict(schema=schema,game=key,added=[],overwritten=[],mods={},settings={}); body[field]=value
     record.write_text(json.dumps(body))
     backup=record.parent/'backups'/('MGSPatriotFix.settings' if key=='mgs4' else 'original.bin')
     backup.parent.mkdir(); backup.write_bytes(b'oldest backup')
     (record.parent/'empty').mkdir()
     before=full(found)
     for k,location in found.items(): options[k]=install.options_for_game(k,location,options[k],lambda _:None)
     assert full(found)==before
     opened=[]
     def forbid(*a,**kw):
      opened.append(a); raise AssertionError('live transaction opened')
     mp.setattr(install,'InstallTxn',forbid)
     try: prepare(base,found,options)
     except install.CorruptManifestError: pass
     else: raise AssertionError((schema,key,field,value))
     assert not opened and full(found)==before
     count+=1
print('PASS',count,'schema-1/2 late settings/mods refusals; real collection/preparation; zero live constructors; all files/directories/records/backups unchanged')
```

### legacy.py

```python
"""Independent valid old/new records through full mixed-game repair/removal."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    seat = Path(sys.argv[1]).resolve()
    sys.path[:0] = [str(seat), str(seat / 'tests')]
    import install
    from pytest import MonkeyPatch
    from conftest import mod_zips, patch_download
    from test_mgs4_plan import combined, prepare
    from test_install_plan import snapshot
    print('Reviewed SHA:', subprocess.check_output(
        ['git', '-C', str(seat), 'rev-parse', 'HEAD'], text=True).strip())
    for schema in (1, 2):
        for missing in (False, True):
            with TemporaryDirectory() as folder, MonkeyPatch.context() as patch:
                base = Path(folder)
                patch.setattr(install, 'app_data_dir', lambda: base / 'app-state')
                patch_download.__wrapped__(patch, mod_zips.__wrapped__(base))
                found, options = combined(base)
                game = found['mgs4'][0]
                settings = game / 'MGSPatriotFix.settings'
                parser = install.patriot_defaults()
                parser['Mouse Settings']['Mouse Vertical Sensitivity'] = '2.750000'
                parser['Launcher and Splashscreens']['Internal Upscaling (PW)'] = '"4K"'
                settings.write_text(install.render_ini(parser))
                (game / 'MGSM2Fix.asi').write_bytes(b'unowned original')
                before = snapshot(found)
                for key, location in found.items():
                    options[key] = install.options_for_game(key, location, options[key], lambda _: None)
                adapter, prepared = prepare(base, found, options)
                assert snapshot(found) == before
                install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
                for directory, _ in found.values():
                    record = directory / install.MODKIT_DIRNAME / install.MANIFEST_NAME
                    body = json.loads(record.read_text())
                    body['schema'] = schema
                    if schema == 1:
                        body.pop('files', None)
                    if missing:
                        body.pop('settings', None)
                    else:
                        body['settings']['owner-custom-metadata'] = {'keep-structurally-valid': True}
                    body['mods']['owner-extra-mod'] = 'owner-version'
                    record.write_text(json.dumps(body))
                for key, location in found.items():
                    options[key] = install.options_for_game(key, location, options[key], lambda _: None)
                before_repair = snapshot(found)
                oldest = {k: {p.relative_to(directory).as_posix(): p.read_bytes() for p in (directory / install.MODKIT_DIRNAME / 'backups').rglob('*') if p.is_file()} for k, (directory, _) in found.items()}
                adapter, prepared = prepare(base, found, options, 'repair')
                assert snapshot(found) == before_repair
                install.execute_plan(prepared, adapter, dict.fromkeys(found, 'not started'))
                assert oldest == {k: {p.relative_to(directory).as_posix(): p.read_bytes() for p in (directory / install.MODKIT_DIRNAME / 'backups').rglob('*') if p.is_file()} for k, (directory, _) in found.items()}
                values = install.validate_patriot_settings(settings.read_text())
                assert values['Mouse Settings']['Mouse Vertical Sensitivity'] == '2.750000'
                assert values['Launcher and Splashscreens']['Internal Upscaling (PW)'] == '"4K"'
                for directory, _ in found.values():
                    body = json.loads((directory / install.MODKIT_DIRNAME / install.MANIFEST_NAME).read_text())
                    assert body['mods']['owner-extra-mod'] == 'owner-version'
                    notes, ok = install.uninstall_game(directory, lambda _: None)
                    assert ok, notes
                assert snapshot(found) == before
                print('PASS schema', schema, 'settings missing', missing,
                      'all-game install/repair/remove; custom/hidden values, saves, oldest originals and unowned ASI preserved')
    print('All fixtures disposable; native compatibility NOT RUN')


if __name__ == '__main__':
    main()
```

### identity.py

```python
import ast, hashlib, re, subprocess
from pathlib import Path
root=Path.cwd(); old='03c58903d386c1c9bc0c9671e8c4b60c69ae30b6'; candidate='d9f13f4a02c3d894689bc21eac9911d619344c2c'; merge='ab4cbe666af085f1ad39ac62fe46402f236055d4'
def blob(ref,name):return subprocess.check_output(['git','show',ref+':'+name])
a=ast.parse(blob(old,'install.py')); b=ast.parse((root/'install.py').read_bytes())
for tree in (a,b):tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='_plan_validate_record']
assert ast.dump(a)==ast.dump(b)
print('PASS entire installer AST except _plan_validate_record unchanged: constants/constructor/recipes/removal/audio/replay/directory fixes')
changed=subprocess.check_output(['git','diff','--name-only',old,candidate],text=True).splitlines()
assert all(p in ('install.py','Install-MGS-Mods.cmd','Install-MGS-Mods.desktop','docs/batches/14-mgs4-patriotfix.md','tests/test_mgs4_plan.py') or p.startswith('docs/batches/evidence/14-manifest-preflight/') for p in changed)
assert blob(old,'docs/batches/14-mgs4-patriotfix-review.md')==(root/'docs/batches/14-mgs4-patriotfix-review.md').read_bytes()
print('PASS all historical evidence/review bytes preserved')
digest=hashlib.sha256((root/'install.py').read_bytes()).hexdigest()
for name in ('Install-MGS-Mods.cmd','Install-MGS-Mods.desktop'):
 data=(root/name).read_bytes(); assert re.search(rb'TAG=v2\.3\.0',data); assert re.search(rb'SHA='+digest.encode(),data)
 assert b'\n' not in data.replace(b'\r\n',b'') if name.endswith('.cmd') else b'\r' not in data
for name in ('install.py','install_plan.py','tools/embed_install_plan.py','tools/capture_patriot_schema.py'):
 data=(root/name).read_bytes(); assert b'\r' not in data; ast.parse(data,feature_version=(3,9))
print('PASS both v2.3.0 shortcuts SHA',digest,'CMD CRLF; desktop/Python LF; Python 3.9 grammar')
for name in ('install.py','install_plan.py','Install-MGS-Mods.cmd','Install-MGS-Mods.desktop','tools/embed_install_plan.py','tools/capture_patriot_schema.py'):
 assert blob(merge,name)==blob(candidate,name),name
print('PASS actual CI merge tree installer/module/shortcut/embed/capture bytes equal literal candidate')
parents=subprocess.check_output(['git','show','-s','--format=%P',merge],text=True).split(); assert candidate in parents
assert subprocess.run(['git','merge-base','--is-ancestor','bd8546524886614a04f5629b1fbbf1f741b73163',merge]).returncode==0
assert blob(merge,'tools/capture_settings_schema.py')==blob('bd8546524886614a04f5629b1fbbf1f741b73163','tools/capture_settings_schema.py')
print('PASS CI merge includes main bd85465 PR21 tooling; parents',*parents)
```

## Historical review and evidence (superseded verdict)

# 14-mgs4-patriotfix: combined independent Verifier review

Reviewed PR #19 at literal **868bebf712a7c11edcecd8b3afc636291a379cc4** on 12 October 2026. Dispatch: Brain `675ba20ceaf416163dc2765ba0b7d2c8f5ad5fb7`. Started with framework status, read rules/card/state and complete dispatch/briefs/dispositions, fetched origin, used an isolated detached seat, and inspected the full production diff before the Worker summary. Original review remains in Git at `38ef1b6a679411d48b784a8142aed797ae170117`; all historical evidence files are untouched.

## Findings and verdict

**BLOCKER — malformed late manifest settings escape all-game preparation**, `install.py:4298–4303`, reaching `install.py:2240` only during replay. A schema-1 MGS4 record with valid game/file/mod lists but `settings: null`, `42`, or `["invalid"]` passes options collection and preparation. Execution commits MGS1–3, then MGS4's constructor raises `CorruptManifestError` converting settings to a dict. MGS4 remains unchanged; the earlier commits are real. Preparation must validate every record assumption consumed by the live constructor, including settings, before any selected game writes. The independent reproducer below confirms all three cases.

Both original Batch 12 blockers are corrected: regular-file recovery directories and unusable live/backup ancestors now refuse before transactions; private replay copies retain confirmed archive identity through copying/extraction. Original MGS4 legacy-removal and compiled-header authentication findings are corrected.

Verdict: **corrections required; BLOCKED for acceptance**, independently reproduced again at the same literal production SHA. No production edits, acceptance, merge, tag or publication. Brain decides disposition.

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

## Repeat verification at the same literal SHA

Historical evidence above and below is preserved. Review parent `b646a768e1e4c848b00aea090a73b905909dc4ed` differs from the reviewed SHA only in this document. Fresh isolated checkout; original probe scripts inspected and rerun against the literal candidate.

| Exact command / inspection | Actual repeat result | Exit |
|:--|:--|:--|
| `python3 tools/fw.py status`; `git fetch origin` | Initial main clean; isolated candidate clean; all project checks pass; fetch silent | 0 each |
| `git worktree add --detach .worktrees/verifier-14-combined 868bebf712a7c11edcecd8b3afc636291a379cc4` | Existing seat preserved; creation refused | 128 |
| `git worktree add --detach .worktrees/verifier-14-combined-audit 868bebf712a7c11edcecd8b3afc636291a379cc4` | Fresh isolated candidate created | 0 |
| `python3 -m pytest tests/ -q` | `408 passed in 18.96s`, local Python 3.9.6 | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py install_plan.py tools/embed_install_plan.py tools/capture_patriot_schema.py` | silent | 0 |
| `python3 tools/embed_install_plan.py --check` | `OK: standalone plan matches authoritative source` | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `command -v desktop-file-validate` | unavailable locally | 1 |
| `python3 -m pytest tests/test_install_plan.py -q -k 'standalone or embedding'` | `2 passed, 27 deselected in 0.31s`; isolated import without source module | 0 |
| `python3 -m pytest tests/test_install_plan.py -q -k sync_check` | `1 passed, 28 deselected in 0.16s`; nonwriting/bad markers | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/record.py` | `null`, `42`, `['invalid']`: MGS1–3 installed; MGS4 unchanged, constructor refuses; blocker confirmed | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/probes.py` | 11 probes PASS: directory/live/backup ancestors refuse; cache-after-commit/copy-race refuse; extraction uses private bytes; cancellation restores MGS2, leaves MGS3–4 unstarted | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/audio.py` | confident and explicit uncertain replacement refuse combined plan | 0 |
| `PYTHONPATH=.:tests python3 /tmp/mgs14-final-verifier/space.py` | device 1/2 deficient-by-one refuse; exact thresholds pass, simulated devices | 0 |
| `git clone --depth 1 --branch 0.2.2 https://github.com/ShizCalev/MGSPatriotFix.git /tmp/mgs14-repeat-source` | literal tree `c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de` | 0 |
| `curl -fL https://github.com/ShizCalev/MGSPatriotFix/releases/download/0.2.2/MGS4_MGSPatriotFix_0.2.2.zip -o /tmp/mgs14-repeat.zip` | 9862 KiB fresh official archive | 0 |
| `python3 docs/batches/evidence/14-mgs4-patriotfix-correction/source-audit.py /tmp/mgs14-repeat-source` | 61 literal blobs/CRLF/hashes; live tag; clean fixture parity PASS | 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/actual-archive.py /tmp/mgs14-repeat.zip` | official checksum, four-game preparation/replay/repair/removal/save/oldest-settings/unowned ASI PASS | 0 |
| `PYTHONPATH=. python3 /tmp/mgs14-repeat-identity.py` | identity.py reproduced below, only source path changed to fresh clone: all 61 mutation/omission and added-header refusals; both shortcut hashes/line endings/3.9 grammar/pins PASS | 0 |
| `python3 docs/batches/evidence/14-mgs4-plan-integration/verify-integration.py`; `python3 /tmp/mgs14-final-verifier/framework.py` | original recipes/safety/source/parity/docs and six pinned framework copies PASS | 0 each |
| Official source inspection: `ConfigTool/main.cpp:2449`, `src/resources/config.cpp`, `src/fixes/graphics_tuning.cpp:72`, `src/dllmain.cpp:111` | all controls serialized including PW; 28 fields/24 reads verified; rendering defaults retain filtering 8, shadows 0, blur/dynamic resolution; root/save paths agree | 0 |
| Official [Steam app page](https://store.steampowered.com/app/2492670/) read | MGS4 title and KONAMI identity verified | n/a |
| `python3 tools/refresh_checksums.py` | `All pinned checksums match the live release assets.` All five exact SHA-256s match; no pins changed | 0 |
| `python3 tools/check_pins.py` | unchanged five pins; HDFix 4.1.2/M2Fix v3.7.3 advisory updates | 1 |
| `gh pr view 19 --json headRefOid,headRefName,url,statusCheckRollup` | current head is earlier review `b646a76`, four green jobs; production reviewed separately | 0 |
| `gh api 'repos/cntrl-alt-lenny/mgs-mc-modkit/actions/runs?head_sha=868bebf712a7c11edcecd8b3afc636291a379cc4'`; `gh run view 38218395168 --json headSha,conclusion,jobs` | literal candidate run `38218395168`, success, all four jobs green | 0 each |
| `gh run view 38218395168 --log > /tmp/mgs14-repeat-ci.log`; `rg 'passed\|desktop-file-validate\|All checks passed' /tmp/mgs14-repeat-ci.log` | Linux 3.9/3.11/3.12: 408 passed, lint/compile/desktop pass; Windows 406 passed, 2 skipped | 0 each |

| `git -c core.whitespace=cr-at-eol diff --check`; `python3 tools/fw.py check` (repeat review) | only authorized review document changed; whitespace clean; `0 error(s), 0 warning(s)` | 0 each |

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
