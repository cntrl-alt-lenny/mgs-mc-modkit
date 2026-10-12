# 16-volume1-qol-upgrade — Verifier

Reviewed: `b0d6a83a2d8e5551c0d78407929c6286854e7192` (PR #21).
Dispatch: `cef5164c4656332ea8e256b11746d6abd24ad9a0`.
Review date: 2026-10-12. Isolated detached seat; only this review is changed,
pushed as a descendant to `worker/16-volume1-qol-upgrade`.

## Findings and verdict

No BLOCKER or SHOULD FIX found for candidate preparation or the Windows ZIP
correction. This is a review verdict for Brain, not adoption/merge approval.

NOTE — `tools/validate_volume1_candidate.py:182-184,202-203`: provenance and
observation references are nonempty strings, not authenticated evidence. A
fabricated synthetic bundle structurally passes, including a non-date capture
time, but the result explicitly still requires independent native review.
Brain must inspect real exports, screenshots/observations and game versions;
structural success cannot establish compatibility or shipping defaults.

## Goal judgments

| Goal | Judgment and independently checked evidence |
|:--|:--|
| Official identities | Met: eight release/tag/notes/signature records agree with official GitHub APIs. Five asset IDs, URLs, names and sizes agree. Baseline v3.6 resolves to `c200ebf9162c2f2ef803557f7ad808283d511846`, release 301495977. Unsigned source and non-reproducible binaries remain explicit limitations. |
| Source capture | Met: fresh official 4.1.2 checkout at `33e80bf4d2223f6866b0b92e06c3c9b85efab652`; seven audited files match blob hashes and exact committed CRLF transformations. Canonical/runtime equality: 27 sections, 134 fields, 139 read calls. |
| Constraints/migration | Met for preparation: bounded static choices/integers match source. 25 dynamic fields need native observations. Three new booleans and the same-identifier particle rename are confirmed; preserve custom values despite changed static default. Legacy/repaired shape handling and ownership-plus-byte-match loader removal are plans, not implemented or proven migrations. |
| ZIP correction | Met: direct header construction reproduces old ACCEPT and corrected unsafe refusal with matching normalized manifest. Fixture resets names after ZipInfo construction and asserts serialized identity; Windows CI passes. NUL-hidden traversal, control bytes, identity changes, symlinks, collisions, integrity refusals are covered without extraction. |
| Shipping isolation | Met: installer, both shortcuts, repaired shipping schema and all framework copies equal base. HDFix 4.1.0, M2Fix v3.6 and existing Bugfix pins remain unchanged. |
| Native adoption | Cannot tell; explicitly gated. Missing or synthetic bundles do not establish exports, UI constraints, provenance, defaults or compatibility. |

Real Windows/Proton MGS2/MGS3 default/kit exports, native dynamic UI/provenance
review, licensed Windows/Deck boots, repair/removal and audio compatibility:
**NOT RUN**. Local desktop validation is unavailable; Linux CI covers it.
No production edits, acceptance, merge, tag or publication.

## Exact evidence

All local checks below ran at the reviewed SHA with Python 3.9.6 on macOS arm64.
Scratch paths are represented by `$S`; they are not delivery dependencies.

| Actual command | Actual output | Exit |
|:--|:--|:--|
| `python3 --version` | `Python 3.9.6` | 0 |
| `python3 -m pytest tests/ -q` | `326 passed in 6.50s` | 0 |
| `python3 -m pytest tests/test_volume1_candidate.py -q` | `43 passed in 0.10s` | 0 |
| `python3 -m ruff check .` | `All checks passed!` | 0 |
| `python3 -m py_compile tools/fw.py install.py tools/validate_volume1_candidate.py` | no output | 0 |
| `python3 tools/fw.py check` | `0 error(s), 0 warning(s)` | 0 |
| `python3 tools/fw.py status` | all project checks pass; detached HEAD clean; safe to leave yes; 4.0.1 notice for Brain | 0 |
| `git diff --exit-code 85697bd -- install.py Install-MGS-Mods.cmd Install-MGS-Mods.desktop docs/agents tools/fw.py tests/fixtures/hdfix-4.1.0-schema.json` | no output | 0 |
| `git diff --check` | no output | 0 |
| `python3 tools/check_pins.py --json` | outdated=2 (HDFix 4.1.2, M2Fix v3.7.3); errors=[] | 1 (advisory) |
| `python3 tools/validate_volume1_candidate.py --source "$S/hdfix"` | commit `33e80bf…`; fields=134; native exports not established by source | 0 |
| `python3 tools/validate_volume1_candidate.py --capture-template` | blank metadata form, four file records, both games | 0 |
| `python3 tools/validate_volume1_candidate.py --exports "$S/blank"` | `candidate validation failed: native platform required` | 1 (expected) |
| `gh run list --commit b0d6a83a2d8e5551c0d78407929c6286854e7192 --json databaseId,headSha,conclusion,name` | CI 37927638509, success, requested head | 0 |
| `gh run view 37927638509 --json headSha,jobs,conclusion` | four jobs success | 0 |
| `gh run view 37927638509 --log` | Windows Python 3.12.10: `324 passed, 2 skipped in 20.01s`; Linux 3.9/3.11/3.12: 326 each, lint and desktop validation pass | 0 |
| `git fetch origin refs/pull/21/merge` then `git diff --exit-code b0d6a83 FETCH_HEAD` | merge `22182b1a030b94275fe5ee38e6d701343a7f24c8`; identical trees `3c27eb2bbfd77e2fda0eddfba59cfdba8776fbc0` | 0 |

CI logs were read, not inferred from a green badge. The two Windows skips are
existing privileged symlink-extraction tests in `tests/test_safe_extract.py`;
the new candidate tests have no Windows skips. CI checked GitHub's PR merge
commit whose complete tree equals the reviewed head.

Framework comparison initially used the wrong upstream directory and failed
with FileNotFoundError (exit 1). Retrying the actual `framework/` and
`templates/tests/` mappings matched all six pinned copies (exit 0).

### Independent raw-header and native-boundary probe

Command: `python3 "$S/probes.py"` (exit 0), with the following script:

```python
import hashlib, json, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tools')
import validate_volume1_candidate as new
old={'__file__':str(Path('tools/validate_volume1_candidate.py').resolve()),'__name__':'original'}
exec(subprocess.check_output(['git','show','0e909f639f7687839c4fe3e3af37c551b3b36467:tools/validate_volume1_candidate.py']),old)
def rawzip(path,name):
    raw=name.encode();data=b'test';crc=zipfile.crc32(data)
    local=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0,0,0,0,crc,4,4,len(raw),0)+raw+data
    central=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0,0,0,0,crc,4,4,len(raw),0,0,0,0,0,0)+raw
    end=struct.pack('<IHHHHIIH',0x06054b50,0,0,1,1,len(central),len(local),0)
    path.write_bytes(local+central+end)
    assert path.read_bytes().count(raw)==2
    return {'sha256':new.digest(path.read_bytes()),'size':path.stat().st_size,'members':[name]}
with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)/'raw.zip';a=rawzip(p,'a\\b');a['members']=['a/b']
    original=zipfile.ZipInfo.__init__
    def windows_init(obj,*args,**kwargs):
        original(obj,*args,**kwargs);obj.filename=obj.filename.replace('\\','/')
    with patch.object(zipfile.ZipInfo,'__init__',windows_init):
        assert old['archive_check'](p,a)['crc']=='pass'
        print('Original raw-backslash/matching-normalized-manifest bypass: reproduced ACCEPT')
        try: new.archive_check(p,a)
        except ValueError as e: print('Corrected same bytes:',str(e))
        else: raise AssertionError('accepted')
    names=['a\\b','safe\x00/../outside','safe\x00','a\nb','a\x7fb','../outside','/absolute','C:/drive','a/./b']
    with patch.object(zipfile.ZipFile,'read',side_effect=AssertionError('read before refusal')),patch.object(zipfile.ZipFile,'extract',side_effect=AssertionError('extracted')),patch.object(zipfile.ZipFile,'extractall',side_effect=AssertionError('extracted')):
        for name in names:
            a=rawzip(p,name)
            try: new.archive_check(p,a)
            except ValueError as e: assert 'unsafe' in str(e)
            else: raise AssertionError('accepted '+repr(name))
    print('Independent header writer: 9 unsafe-name cases refused before payload read; no extraction')
    sys.path.insert(0,'tests');import test_volume1_candidate as tests
    b=Path(temp)/'synthetic';b.mkdir();metadata,manifest=tests.bundle(b)
    result=new.export_check(b,manifest,tests.SCHEMA)
    print('Synthetic metadata can structurally pass:',result['adoption'])
print('exit=0')
```

```text
Original raw-backslash/matching-normalized-manifest bypass: reproduced ACCEPT
Corrected same bytes: unsafe archive path: a\b
Independent header writer: 9 unsafe-name cases refused before payload read; no extraction
Synthetic metadata can structurally pass: still requires independent provenance/defaults/native review
exit=0
```

### Official authentication and preservation audit

Commands: `git clone --quiet --depth 1 --branch 4.1.2 https://github.com/ShizCalev/MGSHDFix.git "$S/hdfix"` and
`git clone --quiet --depth 1 --branch v4.0.0 https://github.com/cntrl-alt-lenny/agentic-framework.git "$S/framework"`
(exit 0 each). For each manifest asset, the download command was
`curl --fail --location --silent --show-error --retry 2 ASSET_URL -o "$S/ASSET_NAME"`.
API IDs, URLs, sizes and available digest declarations were checked before download.
The following consolidated audit records those checks and independent source,
layout, constraint-coverage, INI, shortcut and framework comparisons.

Command: `python3 "$S/audit.py"`:

```python
import ast,base64,hashlib,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path
S=Path('/tmp/mgs-v16-review')
m=json.loads(Path('docs/upgrades/volume1-candidate.json').read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
def api(path): return json.loads(subprocess.check_output(['gh','api',path]))
for r in m['releases']:
    repo,tag=r['repo'],r['tag'];v=api(f'repos/{repo}/releases/tags/{tag}')
    ref=api(f'repos/{repo}/git/ref/tags/{tag}')['object']
    if ref['type']=='tag': ref=api(f'repos/{repo}/git/tags/'+ref['sha'])['object']
    assert ref['sha']==r['commit']
    assert (v['id'],v['html_url'],v['draft'],v['prerelease'])==(r['release_id'],r['url'],False,False)
    assert sha(v['body'].encode())==r['notes_sha256']
    signature=api(f'repos/{repo}/commits/'+r['commit'])['commit']['verification']
    assert (signature['verified'],signature['reason'])==(r['signature_verified'],r['signature_reason'])
    print(repo,tag,'release/tag/notes/signature PASS')
assert api('repos/nuggslet/MGSM2Fix/git/ref/tags/v3.6')['object']['sha']=='c200ebf9162c2f2ef803557f7ad808283d511846'
baseline=api('repos/nuggslet/MGSM2Fix/releases/tags/v3.6')
assert baseline['id']==301495977 and not baseline['prerelease'] and not baseline['draft']
print('Baseline v3.6 official tag/release PASS')
for a in m['assets']:
    repo=a['url'].split('github.com/')[1].split('/releases/')[0]
    v=api(f'repos/{repo}/releases/assets/'+str(a['asset_id']))
    assert (v['name'],v['size'],v['browser_download_url'])==(a['name'],a['size'],a['url'])
    if v.get('digest'): assert v['digest']=='sha256:'+a['sha256']
    names=subprocess.check_output(['/usr/bin/tar','-tf',str(S/a['name'])],text=True).splitlines()
    assert sorted(names)==a['members']
    print(a['name'],'official asset identity + bsdtar layout PASS',len(names))
s=m['hdfix_source']
for name,expected in s['git_blob_sha256'].items():
    b=subprocess.check_output(['git','-C',str(S/'hdfix'),'show',s['commit']+':'+name])
    assert sha(b)==expected
    assert (b.replace(b'\n',b'\r\n') if s['checkout_eol'][name]=='crlf' else b)==(S/'hdfix'/name).read_bytes()
print('Seven source blobs and exact checkout transforms PASS')
sys.path.insert(0,'tools');import capture_settings_schema as c
text=c.without_comments((S/'hdfix/src/resources/config.cpp').read_text(encoding='utf-8-sig'))
constant=c.constant_values(c.without_comments((S/'hdfix/src/resources/config_keys.hpp').read_text(encoding='utf-8-sig')))
pairs=re.findall(r'(?:ConfigHelper::getValue|InputHandler::GetKeybind)\s*\(\s*ini\s*,\s*ConfigKeys::(\w+_Section)\s*,\s*ConfigKeys::(\w+_Setting)',text)
fields={(constant(s),constant(k)) for s,k in pairs}
schema=json.loads(Path('tests/fixtures/hdfix-4.1.2-candidate-schema.json').read_text())
assert fields=={(s,k) for s,ks in schema['fields'].items() for k in ks}
print('Runtime calls/fields/sections:',len(pairs),len(fields),len({s for s,k in fields}))
old=zipfile.ZipFile(S/'MGSM2Fix_3.6.0.zip').read('MGSM2Fix.ini')
new=zipfile.ZipFile(S/'MGSM2Fix_3.7.3.zip').read('MGSM2Fix.ini')
ini=m['m2fix_ini_comparison']
blob=api(f'repos/nuggslet/MGSM2Fix/git/trees/{ini["source_commit"]}')
entry=next(e for e in blob['tree'] if e['path']==ini['source_path'])
raw=base64.b64decode(api('repos/nuggslet/MGSM2Fix/git/blobs/'+entry['sha'])['content'])
assert sha(raw)==ini['source_sha256'] and sha(new)==ini['archive_ini_sha256']
assert old==new and new.replace(b'\r\n',b'\n')==raw
print('M2Fix baseline/candidate INI identical; authenticated source LF conversion PASS')
for name in ('tools/validate_volume1_candidate.py','tests/test_volume1_candidate.py'):
    ast.parse(Path(name).read_text(),feature_version=(3,9))
b=Path('install.py').read_bytes();h=sha(b);v=re.search(rb'^MODKIT_VERSION = "([^"]+)"',b,re.M).group(1).decode()
assert b'\r' not in b
for name in ('Install-MGS-Mods.desktop','Install-MGS-Mods.cmd'):
    d=Path(name).read_bytes();assert ('SHA='+h).encode() in d and ('TAG=v'+v).encode() in d
    assert b'\r' not in d if name.endswith('.desktop') else b'\n' not in d.replace(b'\r\n',b'')
print('Python 3.9 grammar; installer LF; shortcuts LF/CRLF: PASS; tag v'+v+' SHA256 '+h)
f=json.loads(Path('docs/agents/framework.json').read_text())
for name,v in f['files'].items():
    if v['kind']=='copy':
        source=name.replace('docs/agents/','framework/') if name.startswith('docs/agents/') else 'templates/'+name if name.startswith('tests/') else name
        b=Path(name).read_bytes();assert b==(S/'framework'/source).read_bytes() and sha(b)==v['sha256']
print('Six framework copies equal v4.0.0 source PASS')
print('Local desktop-file-validate available:',bool(shutil.which('desktop-file-validate')))
```

Official audit output (exit 0):

```text
ShizCalev/MGSHDFix 4.1.2 release/tag/notes/signature PASS
ShizCalev/MGSHDFix 4.1.1 release/tag/notes/signature PASS
nuggslet/MGSM2Fix v3.7.3 release/tag/notes/signature PASS
nuggslet/MGSM2Fix v3.7.2 release/tag/notes/signature PASS
nuggslet/MGSM2Fix v3.7.1 release/tag/notes/signature PASS
nuggslet/MGSM2Fix v3.7 release/tag/notes/signature PASS
ShizCalev/MGS2-Community-Bugfix-Compilation 3.0.0 release/tag/notes/signature PASS
ShizCalev/MGS3-Community-Bugfix-Compilation 2.0.1 release/tag/notes/signature PASS
Baseline v3.6 official tag/release PASS
MGSHDFix_4.1.2.zip official asset identity + bsdtar layout PASS 13
MGSM2Fix_3.7.3.zip official asset identity + bsdtar layout PASS 7
MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip official asset identity + bsdtar layout PASS 10441
MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip official asset identity + bsdtar layout PASS 4514
MGSM2Fix_3.6.0.zip official asset identity + bsdtar layout PASS 7
Seven source blobs and exact checkout transforms PASS
Runtime calls/fields/sections: 139 134 27
M2Fix baseline/candidate INI identical; authenticated source LF conversion PASS
Python 3.9 grammar; installer LF; shortcuts LF/CRLF: PASS; tag v2.3.0 SHA256 e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a
Six framework copies equal v4.0.0 source PASS
Local desktop-file-validate available: False
```

Command: `python3 tools/validate_volume1_candidate.py --source "$S/hdfix" --archives "$S"` (exit 0):

```json
{
  "archives": [
    {
      "asset": "MGSHDFix_4.1.2.zip",
      "sha256": "fbac84acc36bd395ab649beb576cf60e861fb43d3b36c26057fe900f5fa38e1d",
      "members": 13,
      "crc": "pass"
    },
    {
      "asset": "MGSM2Fix_3.7.3.zip",
      "sha256": "0dabbe0b74bd1844d9f03d864949534ca3c29ea7bd9cf109f877963186e4aa80",
      "members": 7,
      "crc": "pass"
    },
    {
      "asset": "MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip",
      "sha256": "a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003",
      "members": 10441,
      "crc": "pass"
    },
    {
      "asset": "MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip",
      "sha256": "a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769",
      "members": 4514,
      "crc": "pass"
    },
    {
      "asset": "MGSM2Fix_3.6.0.zip",
      "sha256": "a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d",
      "members": 7,
      "crc": "pass"
    }
  ],
  "source": {
    "commit": "33e80bf4d2223f6866b0b92e06c3c9b85efab652",
    "fields": 134,
    "native_exports": "not established by source"
  }
}
```

| Additional independent source check | Output | Exit |
|:--|:--|:--|
| `gh api repos/ShizCalev/MGSHDFix/contents/ConfigTool/tab_data.cpp?ref=f4f662d67a2a033dee0877e436a0fe65eb719e0b` and corresponding `src/resources/config_keys.hpp`, decoded and compared to fresh 4.1.2 | 4.1.0 `MGS2_SoftParticles_Setting="Show Soft Particles"`, static default=true; 4.1.2 same identifier, `"Blend Particle Effect Sprites"`, default=false | 0 |

16-volume1-qol-upgrade · Verifier · DONE · reviewed b0d6a83a2d8e5551c0d78407929c6286854e7192; review commit supplied with delivery.
