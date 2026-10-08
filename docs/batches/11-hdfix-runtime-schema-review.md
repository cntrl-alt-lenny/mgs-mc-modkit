# Batch 11 — Verifier review

Reviewed Worker: `fc831e9538bffd4c8ac5aebb9e9a3c44c082cf1c`; base: `90967b9068125d2e7c0ceac8f6c9d60808a45c95`.
Dispatch: `6443413ab7e9c008a13058c5122f2fbaf84fdfd1`; immutable brief: `d51a8fde5bdd3a0288ac96ecb9a015543602f265`.
Host: macOS 27.0.1, arm64, Python 3.9.6, 2026-10-08. Isolated detached seat; shared checkouts preserved.

## Judgments

Source/schema/defaults **MET**. Independently cloned [official 4.1.0 source](https://github.com/ShizCalev/MGSHDFix/tree/f4f662d67a2a033dee0877e436a0fe65eb719e0b); remote tag equals checkout, without a signed-tag or binary reproducibility claim. Independently resolved header literals and enumerated 133 reader calls: 131 unique pairs exactly match template, schema and runtime fixture. Other reader search resolves only config.cpp and input_handler.cpp.

`ConfigTool/main.cpp:724-1130,2425-2524` creates/registers hidden controls and saves them; flags govern visibility. `tab_data.cpp:150-159,226-227` supplies true/true and MG1 defaults, both launcher choices; header resolves names. `config.cpp:136-216,685,1190-1194` makes missing keys fatal to mod initialization and reads the three fields unconditionally. Corrected failure claims are justified. Full capture equals fixture, with bounded refusal tests intact. Changed hashes match raw BOM/CRLF bytes; former hashes reproduce LF-normalized source (header retaining BOM).

Migration/preservation **MET statically/offline**. Independently used actual main template, not the Worker’s deletion helper; its 128-key shape equals the permitted legacy shape. Both games preserve supported preferences; preview leaves complete byte inventories unchanged; rollback restores them; committed repair retains pre-existing original backups. All six partial additions refuse. Suite also covers malformed/duplicate/unknown keys, bad values, new custom choices, explicit changes/reset and transaction recovery. No production transaction changes were introduced.

Pins/shortcuts/scope **MET**: versions, URLs, checksums, kit version and framework copies unchanged. Native handoff **MET as a plan**: exact candidate, exports, both games/platforms, fresh/repair/custom/reset/negative cases, backups, cancellation, gameplay and removal are covered.

## Findings and verdict

No blocking or should-fix finding. Source/offline correction is suitable for Brain review; no merge/release approval. Native exports, dynamic choices, Windows/Deck initialization/gameplay and actual repair/removal remain **NOT RUN**. Reviewed Worker evidence corroborates source/archive checks; batch 10 failures do not validate this candidate. Desktop validator unavailable. First independent audit attempt exited 1 because my temporary regex expected std::string declarations; corrected to actual constexpr char pointers, rerun passed. Web tag fetch failed; official HTTPS clone succeeded.

## Independently observed commands/results at reviewed SHA

| Command | Actual result | Exit |
| --- | --- | --- |
| `python3 tools/fw.py status` (session start; repeated isolated) | all project checks pass; framework 4.0.1 advisory; no changed copies | 0 |
| `git fetch origin` | no output | 0 |
| `git clone --depth 1 --branch 4.1.0 https://github.com/ShizCalev/MGSHDFix.git /tmp/mgs-batch11-verifier-upstream` | HEAD f4f662d67a2a033dee0877e436a0fe65eb719e0b | 0 |
| `git ls-remote origin refs/tags/4.1.0` (upstream) | f4f662d67a2a033dee0877e436a0fe65eb719e0b | 0 |
| `python3 -m pytest tests/ -q` | 283 passed in 6.12s | 0 |
| `python3 -m ruff check .` | All checks passed! | 0 |
| `python3 -m py_compile tools/fw.py install.py` | no output | 0 |
| `python3 tools/fw.py check` | 0 error(s), 0 warning(s) | 0 |
| `python3 tools/capture_settings_schema.py /tmp/mgs-batch11-verifier-upstream --tag 4.1.0 --tree f4f662d67a2a033dee0877e436a0fe65eb719e0b` | JSON exactly equals fixture; original source-byte SHA256 matches | 0 |
| `PYTHONPATH=. python3 /tmp/mgs-batch11-independent.py` (temporary independent enumeration/preservation probe described above) | 133 calls / 131 pairs; actual main template, both games, preference/preview/rollback/original-backup preservation; six partial subsets refused: PASS | 0 |
| `python3 docs/batches/evidence/11-hdfix-runtime-schema/verify-pins.py` plus independent byte/AST assertions | both v2.3.0; SHA256 e3732996b09db0ffd7b38597b1d3e08552701aa0d6078ce7e4093816ba9c308a; Windows CRLF, tracked Python/desktop LF, Python 3.9 grammar, unchanged pins/framework PASS | 0 |
| `git diff 90967b9 fc831e9 --check -- . ':!Install-MGS-Mods.cmd'` | no output | 0 |
| `desktop-file-validate Install-MGS-Mods.desktop` | executable unavailable; NOT RUN | — |
| `shasum -a 256 /tmp/mgs-hdfix-batch11.zip` (cached Worker archive, independently hashed) | 413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523, equals pin | 0 |
| `bsdtar -tf /tmp/mgs-hdfix-batch11.zip` | winhttp.dll, wininet.dll, plugins/MGSHDFix.asi and Config Tool present; full archive lists 14 entries | 0 |
| `python3 tools/refresh_checksums.py` | All pinned checksums match the live release assets. | 0 |

| Live asset | Independently observed SHA256 |
| --- | --- |
| MGSHDFix 4.1.0 | 413171222e1292092cf879508917a19e0bcac03f34993f31b521ce7b2e4b3523 |
| MGSM2Fix 3.6.0 | a979dea88acd8324b269b101a79293d32674af03d64e800ab9978216b215410d |
| MGS2 Bugfix 3.0.0 | a832bb004ceb59885d08f8a3da6e59910c2d401a7e2b0447edf262edb1d63003 |
| MGS3 Bugfix 2.0.1 | a576b7037e35a630f7dae35553e8329de809633b85ba8baf4f72518fb58cf769 |
