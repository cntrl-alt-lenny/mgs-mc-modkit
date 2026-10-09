# 15-simple-banner

Path: Small (Brain; README illustration and status wording only).

## Done

Replaced the crowded README banner with simple charcoal/cream typography and
one restrained green accent. Included MGS1–4, with MGS4 marked in development
and precise delivery status in README. Removed the unsupported one-click claim and decorative glows, scanlines,
waveforms and technical labels. Kept an accessible SVG title/description.

Clarified that MGS4 is implemented on the Worker branch in PR #19, but awaits
the corrections identified by independent review and merge before inclusion
in the main installer. This is
more precise than "integration in progress" and does not imply native gameplay
validation. No production code, pins, framework or release change.

## Checked

Inspected existing artwork, README and the current PR #19 delivery/status.
The Worker delivery is `48cfa4127a4f77080cec55263c2477166826b67b`; its summary
reports 314 offline tests, and all four CI jobs pass at that exact delivery.
Brain also reran the full offline suite at that delivery: 314 passed in 6.95s.
This precheck is not independent acceptance. Rendered the SVG through Sharp and
visually inspected 1280×320 and 640×160 outputs; all four game labels fit.
[Preview](evidence/15-simple-banner/banner-preview.png).

Full offline suite, Ruff, compilation, framework check/status, diff whitespace
and production equality pass. All six framework copies match immutable 4.0.0
source and manifest. [Actual check evidence](evidence/15-simple-banner/checks.txt)
records the checked commit; only documentation/artwork differs from main.
After the independent review, refreshed status to corrections pending and the
banner to a stable in-development label; rerendered both preview sizes.

## Not checked

Correction verification, native exports, licensed Windows/Deck initialization,
gameplay and real repair/removal remain outstanding. New launcher architecture,
upstream upgrades and framework 4.0.1 are separate work, not required to review
and merge the current MGS4 implementation.

## Failed or blocked

An initial replacement patch targeted the SVG twice; the tool refused without
writes. Replaced the SVG once and applied the documentation separately.
Quick Look produced a square clipped thumbnail; the actual SVG renders correctly
through Sharp. Two exploratory reads used paths from the wrong checkout and
found no file; corrected the locations, with no writes or check substitution.
Owner approval is required before merging this visual/status update.
