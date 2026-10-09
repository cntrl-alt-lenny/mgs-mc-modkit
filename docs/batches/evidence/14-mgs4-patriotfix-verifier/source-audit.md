# Independent source audit

Reviewed installer: 48cfa4127a4f77080cec55263c2477166826b67b.
Sources were freshly fetched; Worker notes/fixtures were comparison targets, not
proof of source identity. No Windows binaries or licensed game assets were run.

- Official clone of https://github.com/ShizCalev/MGSPatriotFix at tag 0.2.2
  resolves to c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de; clean after probes.
- https://store.steampowered.com/app/2492670/ identifies MGS4 (content age-gated).
  Tagged src/resources/common.hpp:39 independently maps app 2492670 to mgs4.exe
  under MGS4; dllmain.cpp:111/128 maps root mgs4_savedata_win. Launcher layout
  and root settings follow ConfigTool/main.cpp and src/resources/config.cpp.
- Official https://github.com/ShizCalev/MGSPatriotFix/releases/tag/0.2.2
  confirms separate game ZIPs, root installation and Proton winmm=n,b.
- Downloaded https://github.com/ShizCalev/MGSPatriotFix/releases/download/0.2.2/MGS4_MGSPatriotFix_0.2.2.zip
  with curl -fL (exit 0). Python hashlib and shasum independently agree on
  4f8fa5dd493c9d5d023fd4dfdcad39a2259b2aedf02685840751c263f497a6b1.
  unzip -Z1 inventory is recorded in checks.txt; ten non-directory members.
  Packaging create_release.yaml:220/221 installs separate Launcher/d3d11.dll
  and MGS4/winmm.dll; both ASIs are in scripts. Log placeholders are omitted
  by installer, while runtime logging creates diagnostics.
- Read all active ConfigHelper::getValue sites in config.cpp, including computed
  launcher/controller alternatives and PW branch; cross-searched src/ConfigTool
  for getValue, settings and INI accesses. 24 recorded reads map to captured keys.
  Commented development readers are inactive. ConfigTool/main.cpp:2453–2532
  serializes every control, hidden controls included, quoting choices and
  emitting numeric bool/int/float values. Language codes/pairs derive from
  config_keys.hpp plus GetActiveLanguagePairs/OnSave, rather than UI labels.
- ConfigTool/tab_data.cpp and config_keys.hpp independently support 28 fields,
  choice lists, floats 0.05–10, filtering 1–16, language eu/en,fr,it,gr,sp,pt
  and jp/jp. Captured JSON matches the committed fixture at the clean source.
- graphics_tuning.cpp:70–86 changes only samplers originally at 8: kit value 8
  preserves them. Motion blur/dynamic resolution hooks are conditional, shadow
  zero bypasses override. various_tweaks.cpp:12 bypasses focus-loss override
  with Pause On Focus Loss=1. Original PW defaults are retained; no FPS patch.
- Capture inventory omits .h headers. probes.py temporarily appends #error to
  compiled stdafx.h: capture still equals fixture, proving a drift-refusal gap.
  Header restored byte-for-byte; final git status is clean.
- Immutable framework clone at v4.0.0 resolves to
  b036c761ac2af2d47e61a1b473c708f094bd4295. verify-delivery.py comparisons were
  inspected and rerun; shortcut tags/SHA bytes, Python grammar/endings, old pins
  and framework bytes all match.

Setup attempts: framework clone --branch 4.0.0 failed exit 128 (tag absent);
--branch v4.0.0 succeeded exit 0. gh run view from the PatriotFix clone failed
exit 1/HTTP 404 because it selected that repository; rerun in kit succeeded.

Native Config Tool export, GUI, ASI initialization, licensed boots/gameplay,
Windows/Deck real repair/removal and DS3 remain NOT RUN. Native-handoff.md has
appropriate evidence requirements; static source and archive success cannot
establish those gates.

Verifier evidence lint attempt: python3 -m ruff check . exited 1 with three E402
errors for imports after the necessary fixture/module search-path setup. Added
explicit E402 annotations for those evidence-only imports; rerun recorded below.

Supplemental official release metadata: GET
https://api.github.com/repos/ShizCalev/MGSPatriotFix/releases/tags/0.2.2
via urllib.request (exit 0); MGS4 asset name, URL, size and GitHub SHA-256 digest
recorded in release-asset.json. Digest also matches both local computations.
