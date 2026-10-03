# Upstream upgrade assessment — 3 October 2026

The tracked updates were reviewed from the authors' release notes. This change
keeps the existing pins while fixing the installer and strengthening the upgrade
process. It does not claim boot validation of newer mods.

| Mod | Candidate and benefit | Required validation |
|:--|:--|:--|
| MGSHDFix | [4.1.1](https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.1): MGS3 DualShock 3 crash fix. [4.1.2](https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.2): shader compilation/performance changes, MGS2 fixes and additional MGS3 config options. | Capture the new Config Tool schema/export, merge existing settings with new defaults, verify both bugfix packs and boot MGS2/MGS3 on Windows and Deck. Review upstream's obsolete `d3d11.dll` removal instruction without deleting an unrelated mod loader. |
| MGSM2Fix | [v3.7](https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7) adds Volume 2 support; [v3.7.1](https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.1) and [v3.7.2](https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.2) focus on the MGS4 flashback; [v3.7.3](https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.3) fixes a Proton crash. | Compare the new INI and archive layout, verify existing MGS1 preferences survive, and test the targeted MGS1 game on both platforms. Volume 2 support does not expand this kit's scope automatically. |

MGSHDFix's changed Config Tool options make a numeric pin-only bump unsuitable.
MGSM2Fix's changes are largely outside this kit's Volume 1 scope; the latest
Proton fix is a reason to test v3.7.3, not proof of compatibility here. The
`preview` release is excluded from stable pin updates.

Follow [UPGRADING.md](UPGRADING.md) and record actual boot/repair/uninstall results
before changing download hashes. The weekly tracking issue remains open until
an upgrade is validated. Users get advisory notices for new kit releases;
individual mods do not update themselves.
