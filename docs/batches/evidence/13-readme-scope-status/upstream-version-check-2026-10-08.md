# README upstream-version snapshot — 2026-10-08

Documentation only. These are the latest stable releases observed on this date,
not an archive/settings compatibility audit or authorization to change installer
pins. Existing pins reviewed at main `67d1406fafb8f6e68f61f182665a2e1d9fc6f6a0`.
The active MGS4 Worker seat was preserved.

All commands below exited 0. Each queried `/releases/latest` using gh api and
returned `prerelease: false`, the listed tag and official release URL.

| Official API command | Installer pin | Observed latest tag | Published UTC |
| --- | --- | --- | --- |
| `gh api repos/ShizCalev/MGSHDFix/releases/latest` | 4.1.0 | 4.1.2 | 2026-09-18T10:45:29Z |
| `gh api repos/nuggslet/MGSM2Fix/releases/latest` | v3.6 / 3.6.0 | v3.7.3 | 2026-09-09T21:22:07Z |
| `gh api repos/ShizCalev/MGS2-Community-Bugfix-Compilation/releases/latest` | 3.0.0 | 3.0.0 | 2026-07-25T08:19:06Z |
| `gh api repos/ShizCalev/MGS3-Community-Bugfix-Compilation/releases/latest` | 2.0.1 | 2.0.1 | 2026-07-27T23:06:36Z |
| `gh api repos/ShizCalev/MGSPatriotFix/releases/latest` | Not integrated | 0.2.2 | 2026-09-11T18:04:27Z |

Cross-checked the official release pages:

- [MGSHDFix 4.1.2](https://github.com/ShizCalev/MGSHDFix/releases/tag/4.1.2)
- [MGSM2Fix v3.7.3](https://github.com/nuggslet/MGSM2Fix/releases/tag/v3.7.3)
- [MGS2 Bugfix 3.0.0](https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation/releases/tag/3.0.0)
- [MGS3 Bugfix 2.0.1](https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation/releases/tag/2.0.1)
- [MGSPatriotFix 0.2.2](https://github.com/ShizCalev/MGSPatriotFix/releases/tag/0.2.2)

README shows both actual pins and these newer versions, dates the check, and
labels MGS4 integration in progress. Actual upstream adoption still requires
the coupled archive/checksum/schema assessment and independent review. No code,
configuration template, shortcut, checksum, release tag or framework change.
