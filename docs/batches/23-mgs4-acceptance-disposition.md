# Batch 23: MGS4 acceptance disposition

## Done

Brain reviewed PR #19 delivery `2844fa25cfda89301def7996a93a2ab6f2dec403`, whose only change after independently reviewed production `d9f13f4a02c3d894689bc21eac9911d619344c2c` is the Verifier report. The manifest blocker is resolved; no new blocking production finding remains. Recommend owner-approved code integration, retaining every native/release gate. No merge or release is authorized by this disposition.

## Checked

Brain reran 439 candidate tests, all 128 malformed-record refusals, and four schema-1/schema-2 lifecycle variants. Custom/hidden settings, saves, oldest backups and unowned ASIs survive the tested lifecycle. Ruff, compilation, embedding and framework checks pass. Both unpublished v2.3.0 shortcut hashes and line endings match production. Latest historical review bytes remain an exact suffix; all earlier reports remain in Git.

Actual review-head CI run `38258964488` checked merge `cdb682825cd8560b763ff67509a115e38963f1db`: Linux 3.9/3.11/3.12 each 482 passed, Windows 480 passed/two existing skips; lint, compilation and desktop validation pass. Parents are main `bd85465` (PR #21 tooling) and exact delivery.

Because main subsequently gained Framework 4.0.1, Brain also tested a local prospective merge: parents current main `20a199fc1c64cb3b0ccf453f0656686d4e9b8e49` and exact delivery; tree `2473b8a289e2150e6b622b3c90de0ac7d512fe98`. All 482 tests and required local checks pass. Game code/shortcuts equal reviewed production; merged tooling/framework equal main. Eleven earlier failure/replay probes, audio replacement/space probes and authenticated official-archive lifecycle pass. This local tree is not an actual GitHub merge or CI result.

Commands/output/exits and reproducible probe text are in [evidence](evidence/23-mgs4-acceptance/).

## Not checked

Native Config Tool exports, GUI/ASI initialization, licensed boots/gameplay, real audio and real-device restoration remain NOT RUN. Windows and Deck validation have separate ownership in Batches 24/25 and can start independently at the exact candidate. Missing devices, games or payloads block only their own checks; Mac fixtures cannot replace them. Framework is already 4.0.1 on main.

## Failed or blocked

The historical integration audit exits 1 because it compares later review text with the original report; Brain reproduced the documented non-blocking note. An initial temporary history probe incorrectly required the earliest report to be embedded in the latest one; corrected checks authenticate the latest suffix and the original Git object. No production fix is needed. Owner merge approval and native release evidence remain outstanding.
