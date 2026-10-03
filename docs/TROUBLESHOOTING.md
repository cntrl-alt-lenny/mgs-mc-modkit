# Troubleshooting and recovery

Close the games and finish Steam downloads before install, repair or removal.
The kit locks each game while modifying it, but Steam does not participate in
that lock. A second kit process reports that another installer is using the
game. Locks release automatically when the process exits; do not delete lock files.

## Interrupted or failed installation

Each game commits separately. The error dialog lists games already installed,
the game restored to its previous setup, and games not started. A successful
earlier game stays installed. On Linux, give that game its launch option from
the README even if a later game failed.

The current run keeps snapshots of existing files, including prior mod files
and large audio assets. Normal errors and cancellation restore those snapshots.
After power loss, rerun the shortcut: recovery happens under the game lock before
the next install or uninstall. Recovery may need time for large files on a
filesystem without hardlinks. If a restore fails, its journal and snapshots are
kept; close anything using the files and retry. Never delete `mgs-modkit` while
recovery is incomplete.

Old list-only journals and damaged records cannot reliably distinguish original
files from files the kit added. The installer stops instead of guessing. Copy
the entire game folder's `mgs-modkit` directory somewhere safe. Restore known
originals from `mgs-modkit/backups` to their matching game paths, then use Steam
**Properties → Installed Files → Verify integrity of game files**. Inspect
remaining mod loaders/plugins against the mod authors' file lists before removal.
Do not delete saves or an unfamiliar loader used by another mod. Preserve the
old record until you have checked the game folder and completed manual recovery.

## Removing audio or an untracked installation

Stock files larger than 64 MiB are recorded but not kept as permanent uninstall
backups. Removal explicitly asks you to use Steam **Verify integrity** for those
originals and retains the record. For installs made by kit 2.3.0, rerun **Remove
the mods** afterward: it verifies the original hashes before clearing the record.
For an older record without original hashes, complete Steam verification and
manual inspection before retiring the old `mgs-modkit` folder.

If the manifest is missing, the kit restores surviving backups but cannot prove
all mod files were identified. It reports **action required**, keeps recovery
data and directs you here. Steam verification restores stock files; it does not
remove added DLLs or plugins. Common kit loaders are `winhttp.dll`, `wininet.dll`,
`plugins/MGSHDFix.asi` (MGS2/3), and `dinput8.dll`, `d3d11.dll`,
`MGSM2Fix64.asi`, `MGSM2Fix32.asi` (MGS1). Compare with the installed authors'
archives rather than deleting these blindly.

## Logs and downloads

Every session writes a diagnostic log and prints its path. The newest 20 are kept:

- Linux/Deck: `$XDG_STATE_HOME/mgs-modkit/logs`, or `~/.local/state/mgs-modkit/logs`.
- Windows: `%LOCALAPPDATA%\MGSModKit\logs`.

Logs include selected local paths, versions, progress and detailed errors. Review
them before attaching one to an issue. Transient download failures retry up to
three times; checksum failures stop immediately. Partial downloads are discarded.

The progress window remains responsive during network and extraction work.
Cancel stops between chunks/files; a blocked network read may take up to the
15-second timeout. Archive processes are stopped before rollback. Terminal users
can press Ctrl+C. Do not kill the process while it is recovering if you can avoid it.

For **Failed to read config key**, repair with this kit's pinned Config Tool and
see [SETTINGS.md](SETTINGS.md). On Linux, check the exact Steam launch options.
