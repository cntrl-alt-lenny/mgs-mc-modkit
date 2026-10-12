# Validation access update — 2026-10-07

Candidate remains `15d9277196e7bd1cfbd45fe280a230050b276bed`.
This evidence-only update follows Verifier delivery
`e3368859c31ef4bde1b68f2eb48aea1b526e3325`. It does not change the Verifier's
review of Worker commit `9eccfcf4661ce4f916d6cec468724ac1db2d1169`.

Source: owner instructions and Brain's computer-use observations relayed to
Worker on 2026-10-07. Worker did not independently operate the remote host.

| Sequence | Instruction or actual observation | Result and limit |
| --- | --- | --- |
| 1 | Owner says only the Windows PC is likely available; Deck is not currently available. | Windows hardware/access still requires confirmation. Deck checks remain NOT RUN. |
| 2 | Owner explicitly authorizes installing missing licensed MGS games through Steam in its default library directory. | Permission exists to install missing titles once connected. It does not establish which titles are installed or their builds. |
| 3 | Brain's computer-use inventory returned Mac apps. | Current control surface was the Mac, not a Windows desktop. |
| 4 | Brain opened the existing Moonlight connection; paired Main PC showed `PC Status: Offline`. | No Windows session was reached. |
| 5 | Brain attempted Wake PC; later the paired PC still showed Offline. | Wake did not establish access. |
| 6 | Moonlight Test Network returned `This network does not appear to be blocking Moonlight.` | This diagnostic did not connect to the PC or prove its availability. |
| 7 | Brain has an access/connection question pending with the owner. | Existing streaming connection should be used once available. No credentials, alternate transport or game state inferred. |

No Windows desktop, Steam session, game installation or hardware smoke test
was reached. All applicable matrix scenarios remain NOT RUN; release readiness
remains blocked. No game files were changed.

Resume Windows testing when the existing streaming connection works. First
inventory actual installed games, Steam default library, builds, saves, mods,
settings and recovery state. Preserve and review the baseline before kit
installation/removal. Install missing licensed titles using the owner's
authorized Steam default directory; record download/completion and stock boot
observations. Then run the literal candidate's local `install.py`, verified
against its recorded hash, and fill the matrix with observed results. Audio
payload availability remains unknown; Deck testing still requires a host.
