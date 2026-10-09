# 16-volume1-qol-upgrade — Worker

Checked path. Source/archive/tooling preparation delivered; shipping adoption
blocked by missing native Config Tool exports. Base: origin/main `85697bd`.
Implementation checked: `1267ac3eca40186c6313bde0782631dc957d2e06`.
The delivery adds only this summary and recorded evidence to that implementation.

## Done

Read the complete Worker/ownership briefs at
`095a3b1b03d8bb543aa929069eca501b9e7cd8fa`; fetched origin and used an isolated
Worker branch. Reverified official stable releases, every intervening release
note, literal tag commits and the Bugfix/MGSHDFix coupling. Committed the exact
candidate archive identities/layouts/payload hashes and independent 4.1.2
canonical/runtime capture: 27 sections, 134 fields, including hidden MG keys.

Added read-only source/archive/native-export validation, blank capture metadata
generation and synthetic failure tests. Recorded the soft-particle rename,
changed static default and future preservation/refusal requirements. Both
MGSM2Fix INIs are byte-identical; Git source differs only by recorded CRLF/LF.
Provided the reproducible native capture handoff in
`docs/upgrades/volume1-2026-10-09.md`. Shipping pins/settings, installer,
shortcuts, framework copies and Worker A's engine/orchestration are unchanged.

## Checked

Actual commands, output and exit codes at the implementation SHA are in
`docs/upgrades/volume1-check-evidence.md`.

| Check | Result |
|:--|:--|
| Python 3.9.6 full pytest | 314 passed; exit 0 |
| Ruff; compilation; framework check/status | Passed; exit 0 |
| Official archive SHA256/layout/CRC/payloads | Five ZIPs passed; exit 0 |
| Authenticated source and runtime/canonical equality | Passed; exit 0 |
| Native macOS bsdtar layouts | All five match manifest; exit 0 |
| Incomplete native capture | Correctly refused; expected exit 1 |
| Both shortcut tags/hashes and line endings | Match unchanged installer; exit 0 |
| Installer/shortcut/framework diff against base | Empty; exit 0 |
| Advisory live stable pin check | Two newer mods; expected exit 1, no errors |

## Not checked

Actual Windows/Proton per-game default and kit exports, dynamic choices/defaults,
UI evidence and native provenance remain missing. Structural validation cannot
establish those facts. Candidate migration/recovery is not implemented without
the gate evidence. Native Windows/Deck licensed boots, real install/repair/removal
and user-supplied audio remain separate release checks. Desktop validation is
unavailable on this Mac. GitHub CI and independent exact-SHA verification are
pending at delivery; no release readiness is claimed.

## Failed or blocked

Adoption is blocked; retained all shipping pins. Initial manifest inspection
reached still-downloading ZIPs (BadZipFile, then two incomplete-size refusals);
completed downloads were subsequently fully checked. One early test failed
because the candidate fixture had not yet been generated; final suite passes.
The first source check refused CRLF checkout bytes against LF Git blobs;
authenticated upstream attributes and explicit dual hashes now validate the
exact conversion. Framework's 4.0.1 notice is for Brain, not this Worker.
No technical interface conflict arose; Brain coordinates later adoption and
integration after native capture and independent review. Never merged, tagged
or published.
