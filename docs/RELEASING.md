# Releasing the kit

1. Run lint and the offline suite. CI tests Python 3.9/3.11/3.12 on Linux and
   Python 3.12 on Windows. Archive tools run natively on both platforms.
2. Complete the real-machine smoke checks below. Synthetic archives cannot prove
   a mod starts correctly in a licensed game or that a GUI renders on real hardware.
3. Set `MODKIT_VERSION`, write `docs/releases/v<version>.md`, and run
   `python tools/pin_shortcuts.py`. Commit all three installer/shortcut changes
   together. Preserve Windows CRLF endings.
4. Merge the reviewed PR, then tag that exact commit `v<version>` and push the
   tag. Do not publish shortcut files until their pinned release asset exists.
5. The release workflow calls the same CI workflow on the tagged SHA. Publishing
   waits for every Linux job and Windows job to pass, then checks both shortcuts'
   tag and SHA against the tagged installer. Release notes precede checksum details.

## Real-machine smoke checks

- Windows: fresh install → start all three games → change an option → repair →
  confirm custom language/resolution survives → remove → start stock games.
- Steam Deck/Linux: repeat with Proton launch options and optional audio; cancel
  during extraction and confirm restoration. Check the progress window and logs.
- Large audio: remove → Steam verification → remove again to finish cleanup.
- Repeat repair while another kit process owns the same game lock: it must refuse.

Record hardware, game version, mod pins and results in the release/PR. The 2.3.0
implementation was verified with synthetic archives on Linux; real game boots
and Windows execution are release checks, not results claimed by that local run.
