# Authenticated MGS4 / PatriotFix set

Prerequisite: Brain explicitly confirmed batch 11's merge and that this Worker
prompt could begin. Fetched main is `67d1406fafb8f6e68f61f182665a2e1d9fc6f6a0`,
[PR 17](https://github.com/cntrl-alt-lenny/mgs-mc-modkit/pull/17).
Planning brief read with `git show a1c9264b2ba803a0f05774bd3bc60dcdcbe013d2:docs/batches/14-mgs4-patriotfix-brief.md`.
Shared checkouts were not reset. Framework 4.0.1 advisory is outside this batch;
4.0.0 copies remain untouched.

[Steam app 2492670](https://store.steampowered.com/app/2492670/) identifies MGS4
Master Collection. Official upstream [tag 0.2.2](https://github.com/ShizCalev/MGSPatriotFix/tree/0.2.2)
resolves to `c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de` (local detached checkout
and live tag agree). `src/resources/common.hpp:39` maps MGS4 to mgs4.exe,
subfolder MGS4 and 2492670; PW is a separate game/ID. Tagged README defines
Steam root METAL GEAR SOLID 4 and Proton `winmm=n,b`. Config Tool and dllmain
locate the game/Launcher subfolders and root settings; dllmain:111/128 defines
root mgs4_savedata_win. No kit code edits that save tree or game executable/assets.

Downloaded only official [MGS4 0.2.2 asset](https://github.com/ShizCalev/MGSPatriotFix/releases/download/0.2.2/MGS4_MGSPatriotFix_0.2.2.zip).
Computed SHA-256: `4f8fa5dd493c9d5d023fd4dfdcad39a2259b2aedf02685840751c263f497a6b1`.
Exact archive inventory and official release metadata are in checks.txt.
Packaging workflow stages Launcher/d3d11.dll, MGS4/winmm.dll and both
scripts/MGSPatriotFix.asi, root Config Tool and licenses. Payload allowlist requires
all 10 files before live writes. Upstream placeholder logs are deliberately not
installed: runtime logging.cpp:101–108 creates logs itself, preserving diagnostic
history. Existing unmanaged/competing loaders and duplicate ASIs refuse.

Capture independently resolves every active canonical field in tab_data.cpp,
including hidden PW fields and three currently inactive diagnostic controls.
There are 8 sections/28 fields. Config Tool main.cpp:721 computes visibility,
1119 stores hidden controls too, and 2453–2532 saves all controls (bool/int/float/
quoted choices). Language output codes come from MGS4_LanguagePairs and OnSave;
valid pairs eu/en,fr,it,gr,sp,pt and jp/jp. Capture records 24 runtime reads,
including both branches of computed launcher/controller keys. All source
getValue/INI access was searched; active runtime reads are in resources/config.cpp.
Commented development readers do not create runtime requirements. Capture is
bounded to exact tree, source inventory and raw-byte hashes of all 58 C++ files;
any changed/new file refuses pending source review. MIT attribution is preserved.

Default derivation: tab declarations supply bools, ranges, Float 1.0/0.05–10,
choices and hidden defaults. graphics_tuning.cpp:70–86 only changes samplers whose
value is 8, so setting 8 preserves those values. Blur/dynamic resolution hooks
are conditional; shadows 0 bypasses override. various_tweaks.cpp:12 bypasses
its focus-loss hook when Pause On Focus Loss=1. These are kit conservative
changes from upstream filtering 16/pause off; no FPS unlocker is added. Launcher/
logo skips are QoL choices; automatic update checks are always disabled.
Other supported custom values survive unless explicitly changed/reset.

Source review and extracted files do not establish native Config Tool exports,
Windows/Deck boot/gameplay, flashback compatibility or real restoration. Those
remain NOT RUN under native-handoff.md. Existing MGS1–3 set and schema are unchanged.
