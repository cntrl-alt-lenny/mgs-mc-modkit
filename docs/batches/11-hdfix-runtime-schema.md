# 11-hdfix-runtime-schema

## Done

Audited official MGSHDFix 4.1.0 source at authenticated tag/tree
`f4f662d67a2a033dee0877e436a0fe65eb719e0b`, using the immutable planning brief
`d51a8fde5bdd3a0288ac96ecb9a015543602f265` and batch 10 evidence at
`9a8d98661b40d702f0e9a43248f01d5b385c67d1`. Built from fetched main `90967b9`.

Corrected all three omitted runtime keys, not just the first error: MSX Skip
Launcher Game, Crop Overscan Area and Correct Aspect Ratio to 4:3. Hidden
Config Tool controls are saved too. Capture/schema/template now contain 131
keys, matching every unique canonical runtime read. Choice constraints and
new defaults come from pinned source. [Source audit](evidence/11-hdfix-runtime-schema/source-review.md)
and [reproducible runtime enumeration](evidence/11-hdfix-runtime-schema/runtime-audit.json)
record the derivation.

Complete legacy 128-key settings migrate in memory before transactional writes.
Supported preferences survive, including custom new-key values; malformed,
unknown, missing original or partly migrated files refuse. Added regressions
for both games, preview non-mutation and rollback. Corrected compatibility
claims and guidance. Mod pins/checksums and unpublished kit 2.3.0 remain unchanged;
both shortcut hashes regenerated. Framework copies remain unchanged.

## Checked

Mac arm64 / Python 3.9.6 offline checks and exact commands, outputs, exits and
checked implementation SHA are in [checks](evidence/11-hdfix-runtime-schema/checks.txt).
Independent byte checks cover both shortcut tags/hashes, CRLF/LF, unchanged
pins and Python 3.9 grammar. Source capture refusal regressions remain intact.

## Not checked

Native Config Tool exports, Windows/Deck initialization, gameplay, actual
repair/preservation and removal/restoration are **NOT RUN** on this M1 MacBook
Pro seat. Prior batch 10 runtime errors are not corrected-candidate validation.
Dynamic choices and licensed runtime compatibility remain unproven. Use the
[Windows/Deck handoff](evidence/11-hdfix-runtime-schema/native-handoff.md).

## Failed or blocked

First added MGS3 regression used the helper's MGS2 manifest; transaction correctly
refused the wrong game. Corrected the test helper; the targeted rerun passed.
Desktop validation is unavailable on this host. Full native/release acceptance
remains blocked on the separate hardware checks and independent Verifier/Brain
review. No approval, merge, tag or publication performed.
