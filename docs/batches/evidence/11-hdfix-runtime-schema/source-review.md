# Pinned source and runtime audit

Planning brief read with `git show d51a8fde5bdd3a0288ac96ecb9a015543602f265:docs/batches/11-hdfix-runtime-schema-brief.md`.
Batch 10 summary and Windows MGSHDFix logs read at `9a8d98661b40d702f0e9a43248f01d5b385c67d1`.
Worker base is latest fetched `origin/main`, `90967b9`.

Cloned the official HTTPS remote `https://github.com/ShizCalev/MGSHDFix.git`
at tag 4.1.0. `git rev-parse HEAD` and `git ls-remote origin refs/tags/4.1.0`
both returned `f4f662d67a2a033dee0877e436a0fe65eb719e0b` (exit 0).
This authenticates repository/tag identity via GitHub HTTPS, not a signed tag or
binary-to-source reproducibility claim. `audit-runtime.py` refuses any other
HEAD or changed bytes in the four reviewed files. The schema capture records
original source-byte hashes and keeps all existing syntax refusal boundaries.

Upstream source at that tree:

| File/lines | Finding |
| --- | --- |
| `ConfigTool/main.cpp:724-1130` | Every canonical field's control is created. Game flags govern labels/layout visibility; hidden controls still enter `m_controls` at 1130. |
| `ConfigTool/main.cpp:2425-2524` | OnSave iterates all `m_controls`, creates `iniData` and truncates/writes it. Hidden MG fields are included. No export was executed here. |
| `ConfigTool/tab_data.cpp:150-159` | Crop Overscan Area and Correct Aspect Ratio to 4:3 both have `Field::Bool, true`. |
| `ConfigTool/tab_data.cpp:226-227` | MSX Skip Launcher Game is a choice, default `SkipLauncherMSX_Option_MG1`; both MG1/MG2 choices are explicit. |
| `src/resources/config_keys.hpp:117-128,724-729` | Resolves section/key names and MG1 choice `Metal Gear (MSX)`, MG2 `Metal Gear 2: Solid Snake`. |
| `src/resources/config.cpp:136-216` | Missing section/key calls FatalConfigError, showing console and exiting the mod initialization thread. Initial C++ variable values do not supply fallback for missing keys. |
| `src/resources/config.cpp:685,1190,1194` | All three previously filtered MG-only canonical fields are read unconditionally. |
| `src/dllmain.cpp:287-295` | MSX game choice affects MG launcher parameters only. |
| `src/features/mg1_display_scaling.cpp:163-168,222-227` | Scaling features return early for non-MG games; required boolean reads still occur first in shared config initialization. |

Audit enumerates all 133 canonical `getValue`/`GetKeybind` calls in config.cpp,
including conditional reads: 131 unique section/key pairs, exactly equal to
the corrected 131 Config Tool fields and template keys. No missing or tool-only
canonical key remains. Enumeration includes potential paths rather than trying
to evaluate game/feature conditions. Search of other src files found no other
canonical settings reader sites; InputHandler reads the passed section/key.
Reviewed all MG-only rows: two canonical booleans and the launcher choice;
other MG-only entries are spacers. Safety Switch is a UI-only literal row.
The independent runtime fixture makes an omitted key fail offline tests.

Migration admits the exact complete legacy shape (all 128 original keys, no
new keys) or an already complete 131-key shape. It fills only the three source
backed defaults, then applies normal types/constraints to every key. Existing
supported choices survive, including custom values in the new keys. It cannot
prove who authored a matching legacy file; it recognizes schema shape, not
provenance. Missing original keys, partial new-key presence, duplicates, unknown
sections/keys and invalid values refuse before replacement. Existing historical
pressure-overlay normalization remains. Options preview is memory-only; writes
still use InstallTxn and its rollback/recovery behavior.

Native per-game Config Tool exports, initialization/gameplay and Deck behavior
are NOT RUN. Static source evidence supports these three defaults and schema
corrections; it does not validate dynamic choices or platform runtime behavior.

Other attempts retained: the web page reader could not fetch the official tag
page (restricted URL); the official HTTPS git clone and remote tag comparison
succeeded. During compatibility-comment editing, an intermediate unpushed
header edit removed/misplaced unrelated documentation; diff review caught it,
the full original usage/transaction prose was restored, and final compilation,
lint and all 283 tests passed. Those local comment-only edits were consolidated
before pushing; the functional implementation commit remains separately stated.
