# 16-volume1-qol-upgrade — Worker

Checked path. Candidate preparation and Windows ZIP correction delivered;
shipping adoption remains blocked by missing native Config Tool exports.
Base: `85697bd`. Original implementation: `1267ac3eca40186c6313bde0782631dc957d2e06`.
Correction implementation checked: `b2a776bf4a68cb38c0704c2fa32879e87cc59c12`.
Delivery changes only the summary and evidence after the correction.

## Done

Read the complete correction brief at `fbc360f7d820dc3795aa6c56bf2f778608ac62d7`,
Brain's batch 17 disposition/probes and failed Windows run 37920207041.
Fetched origin and continued the existing isolated Worker branch and PR #21.

Archive validation now checks original ZIP member names before Windows separator
normalization or NUL truncation. Unsafe control bytes and any lossy name change
are refused before layout/payload checks. The fixture explicitly serializes raw
names into both headers and asserts their identity before requiring the existing
unsafe-path refusal. Added matching-layout reader-normalization regressions,
NUL/hidden-traversal/control-byte cases, symlink and integrity refusal checks.

The existing official candidate manifest, 134-field canonical/runtime capture,
read-only source/archive/export tooling and native handoff remain intact.
Shipping installer, pins, settings/schema/constraints, shortcuts, framework and
Worker 12's engine are unchanged. Native handoff:
`docs/upgrades/volume1-2026-10-09.md`.

## Checked

Actual commands, output and exit codes at the literal correction implementation
are in `docs/upgrades/volume1-correction-evidence.md`; original evidence remains
in `docs/upgrades/volume1-check-evidence.md`.

| Check | Result |
|:--|:--|
| Python 3.9.6 full suite; targeted regressions | 326 passed; 43 passed; exit 0 |
| Ruff; compilation; Python 3.9 syntax | Passed; exit 0 |
| Framework check/status; whitespace | Passed; exit 0 |
| Five official ZIP SHA/size/layout/CRC/payload checks | Passed; exit 0 |
| Authenticated source and 134-field runtime/canonical equality | Passed; exit 0 |
| Live official asset/tag identities; native bsdtar layouts | Passed; exit 0 |
| Shortcut tags/hashes/line endings; protected shipping diff | Unchanged; exit 0 |
| Incomplete native capture | Refused; expected exit 1 |
| Advisory live pin check | Two newer mods; expected exit 1; no errors |

## Not checked

Real Windows/Proton MGS2/MGS3 default/kit exports, dynamic UI observations and
native provenance still gate adoption. Structural validation cannot establish
those facts. Native licensed game boots, actual install/repair/removal and
user-supplied audio compatibility remain separate release checks. Desktop
validation is unavailable on this Mac; Linux CI covers it. Independent Verifier
review of the new delivery SHA remains required. CI delivery results are reported on
PR #21; no release readiness is claimed.

## Failed or blocked

Prior delivery's Windows fixture failed because its writer normalized the name;
Brain additionally reproduced validator acceptance of raw backslashes. Both are
corrected without weakening the refusal assertion. Earlier download, fixture and
CRLF failures remain recorded in original evidence/history. Adoption remains
blocked, not this tooling correction. Framework's 4.0.1 notice is for Brain.
Never accepted, merged, tagged or published.
