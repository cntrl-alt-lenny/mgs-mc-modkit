# Constructor versus private preparation audit

Baseline production: `868bebf712a7c11edcecd8b3afc636291a379cc4`;
preserved review head: `03c58903d386c1c9bc0c9671e8c4b60c69ae30b6`.
Correction changes only `_plan_validate_record`; `InstallTxn` stays unchanged.

| Constructor consumption | Non-mutating preparation validation |
|:--|:--|
| Recovery root, interrupted journal | Root/link/type checks; pending journals refuse in plan building and adapter recheck before preparation/replay. Preparation never recovers or opens a transaction. |
| Manifest JSON object, record link | Shared `_read_record` refuses malformed JSON, non-object and links. |
| Added and overwritten lists, path/backup safety, MGS4 ownership boundary | Shared `_validate_manifest`; constructor and preflight call it. Returned strings and dictionary entries support constructor list/set/path comprehensions. Required file lists and game identity are checked in both. |
| Prior mods copied with `dict(...)` | Optional `mods` defaults to `{}`; present value must be a dictionary in both. No new restrictions on custom names/versions. |
| Prior settings copied with `dict(...)` | **Confirmed omission corrected:** absent `settings` defaults to `{}`; present value must be a JSON object during preparation. Null, scalar, empty/malformed/pair lists refuse. Values inside valid mappings remain unrestricted by this structural check. Recipe settings validation remains authoritative. |
| Schema, transaction identity, optional file hashes | No schema-dependent constructor conversion; `_validate_manifest` retains its existing compatibility. Schema-1/schema-2 fixtures execute and repair; no new schema/profile rules. Transaction identity only matters to recovery, whose journal refuses pending replay. |
| Staging/rollback/backups directories | Preflight rejects links and non-directory obstructions; checks backup subtree links. Existing destination/backup ancestor and destination checks complete preparation before any live transaction. |
| Orphan original backups | Constructor walks backups; preflight checks links, private MGS4 preparation enforces the same reviewed-file boundary and tracks orphan ownership. Other recipes retain generic orphan adoption. |

No further knowable constructor/preparation mismatch was found. This audit does
not claim filesystem races, permissions, disk errors or native compatibility can
be ruled out by preflight. Existing locks, snapshot rechecks, replay authentication
and rollback remain intact.

Regressions put each affected MGS1–4 game last, run real options collection and
preparation, forbid live transaction construction and compare all selected file
bytes plus directory membership, including the original record and orphan backup.
Four successful all-game lifecycle variants cover schema 1/2 with present/missing
settings, retained custom mod metadata, MGS4 custom/hidden settings, saves, oldest
originals, repair and removal. Historical tests and reports remain intact.
