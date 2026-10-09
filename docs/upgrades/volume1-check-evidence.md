# Batch 16 check evidence

Implementation commit: `1267ac3eca40186c6313bde0782631dc957d2e06`. Checks below ran at this commit.

Host: macOS arm64; absolute checkout paths in framework output replaced with `<seat>`.

```text
$ python3 --version
Python 3.9.6
exit=0
```

```text
$ python3 -m pytest tests/ -q
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 68%]
........................................................................ [ 91%]
..........................                                               [100%]
314 passed in 6.80s
exit=0
```

```text
$ python3 -m ruff check .
All checks passed!
exit=0
```

```text
$ python3 -m py_compile tools/fw.py install.py tools/validate_volume1_candidate.py

exit=0
```

```text
$ python3 tools/fw.py check
0 error(s), 0 warning(s)
exit=0
```

```text
$ python3 tools/fw.py status
Framework
  pinned to agentic-framework 4.0.0 (https://github.com/cntrl-alt-lenny/agentic-framework)
  newer release available: 4.0.1 -- minor or patch: update between batches; Brain proposes it
Merge rule
  owner-approves
Work not merged yet
  worker/16-volume1-qol-upgrade: 1 commit(s), last 2026-10-09; no summary yet: still working, or stopped without one
  worker/12-install-plan-engine: 1 commit(s), last 2026-10-09; no summary yet: still working, or stopped without one
  brain/11-12-briefs: 10 commit(s), last 2026-10-09; batch 11-12-briefs, 11-hdfix-runtime-schema-verifier-dispatch, 12-install-plan-interface, 14-mgs4-patriotfix-verifier-dispatch: Worker summary in -- Brain reviews it, or sends the Verifier prompt if this is a Checked batch
  brain/simple-banner: 2 commit(s), last 2026-10-09; batch 15-simple-banner: Worker summary in -- Brain reviews it, or sends the Verifier prompt if this is a Checked batch
  worker/14-mgs4-patriotfix: 6 commit(s), last 2026-10-08; batch 14-mgs4-patriotfix: Worker summary in -- Brain reviews it, or sends the Verifier prompt if this is a Checked batch
  worker/10-release-validation: 10 commit(s), last 2026-10-07; batch 10-release-validation: Verifier review in -- Brain judges it
  fix/recovery-and-usability: 3 commit(s), last 2026-10-03; no summary yet: still working, or stopped without one
This machine
  on worker/16-volume1-qol-upgrade; no uncommitted changes
  not on GitHub yet: worker/12-install-plan-engine (1 commit(s)), worker/16-volume1-qol-upgrade (1 commit(s))
  uncommitted changes in linked checkout <repo>/.worktrees/verifier-14-mgs4-patriotfix
  finished checkouts (clean, and their work is merged) that can be removed: <home>/.codex/worktrees/product-integration-brief/mgs-mc-modkit -- git worktree remove <folder>
  safe to leave this machine: NO -- push or deal with the items above first
Checks
  all project checks pass
Command form on this machine: python3 tools/fw.py <command>
next: ask Brain to review batch 11-12-briefs, 11-hdfix-runtime-schema-verifier-dispatch, 12-install-plan-interface, 14-mgs4-patriotfix-verifier-dispatch
exit=0
```

```text
$ python3 tools/validate_volume1_candidate.py --source /tmp/mgs-batch16/hdfix --archives /tmp/mgs-batch16
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
exit=0
```

```text
$ python3 tools/check_pins.py --json
{
  "rows": [
    {
      "what": "MGSHDFix (MGS2/MGS3)",
      "repo": "ShizCalev/MGSHDFix",
      "pin": "4.1.0",
      "latest": "4.1.2",
      "outdated": true
    },
    {
      "what": "MGS2 Community Bugfix Compilation",
      "repo": "ShizCalev/MGS2-Community-Bugfix-Compilation",
      "pin": "3.0.0",
      "latest": "3.0.0",
      "outdated": false
    },
    {
      "what": "MGS3 Community Bugfix Compilation",
      "repo": "ShizCalev/MGS3-Community-Bugfix-Compilation",
      "pin": "2.0.1",
      "latest": "2.0.1",
      "outdated": false
    },
    {
      "what": "MGSM2Fix (MGS1)",
      "repo": "nuggslet/MGSM2Fix",
      "pin": "v3.6",
      "latest": "v3.7.3",
      "outdated": true
    }
  ],
  "errors": [],
  "outdated": 2
}
exit=1
```

```text
$ python3 -c 'import hashlib,re
from pathlib import Path
p=Path("install.py");b=p.read_bytes();h=hashlib.sha256(b).hexdigest();v=re.search(rb'"'"'^MODKIT_VERSION = "([^"]+)"'"'"',b,re.M).group(1).decode()
for n in ["Install-MGS-Mods.desktop","Install-MGS-Mods.cmd"]:
 d=Path(n).read_bytes();assert ("SHA="+h).encode() in d;assert ("TAG=v"+v).encode() in d
 assert b"\r" not in d if n.endswith(".desktop") else b"\n" not in d.replace(b"\r\n",b"")
 print(n,"tag=v"+v,"sha256="+h,"line endings pass")
assert b"\r" not in b
print("install.py LF pass")'
Install-MGS-Mods.desktop tag=v2.3.0 sha256=e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a line endings pass
Install-MGS-Mods.cmd tag=v2.3.0 sha256=e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a line endings pass
install.py LF pass
exit=0
```

```text
$ git diff --exit-code origin/main -- install.py Install-MGS-Mods.cmd Install-MGS-Mods.desktop docs/agents tools/fw.py

exit=0
```

```text
$ git diff --check

exit=0
```


Additional checks at `1267ac3eca40186c6313bde0782631dc957d2e06`:

```text
$ /usr/bin/tar -tf /tmp/mgs-batch16/MGSHDFix_4.1.2.zip
stdout: 13 members; exact manifest layout matches (full listing in manifest).
exit=0
```

```text
$ /usr/bin/tar -tf /tmp/mgs-batch16/MGSM2Fix_3.7.3.zip
stdout: 7 members; exact manifest layout matches (full listing in manifest).
exit=0
```

```text
$ /usr/bin/tar -tf /tmp/mgs-batch16/MGS2-Community-Bugfix-Compilation_Base_v3.0.0.zip
stdout: 10441 members; exact manifest layout matches (full listing in manifest).
exit=0
```

```text
$ /usr/bin/tar -tf /tmp/mgs-batch16/MGS3-Community-Bugfix-Compilation_Base_v2.0.1.zip
stdout: 4514 members; exact manifest layout matches (full listing in manifest).
exit=0
```

```text
$ /usr/bin/tar -tf /tmp/mgs-batch16/MGSM2Fix_3.6.0.zip
stdout: 7 members; exact manifest layout matches (full listing in manifest).
exit=0
```

```text
$ python3 tools/validate_volume1_candidate.py --capture-template
stdout: blank capture form generated; not native evidence.
exit=0
```

```text
$ python3 tools/validate_volume1_candidate.py --exports /tmp/mgs-batch16/blank-capture
candidate validation failed: native platform required
exit=1 (expected refusal of incomplete metadata)
```
