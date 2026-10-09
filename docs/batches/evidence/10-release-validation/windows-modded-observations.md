# Windows candidate runtime observations

Candidate installer: `15d9277196e7bd1cfbd45fe280a230050b276bed`.
All times below are 2026-10-07 BST (UTC+1). `$STEAM` is the default Steam
root and `$CHECKOUT` is this Worker checkout; public logs replace local user
prefixes and Steam account identifiers. No mod configuration migration was
performed to hide a runtime error.

## Fresh install and preservation

`py -3 install.py` started15:15:29, process65500, unified session31217.
After the full closed-game stock inventory completed, the native review was
confirmed around15:25. All three games selected; optional audio unchecked.
Review and progress screenshots are retained. The session log reports all
three manifests committed and verified, finishing MGS1 Complete100%15:31:36.
At15:32:26 all journals absent and stagedfilecounts0. A later Steam screenshot
visually included the native MGS Mod Kit info dialog saying all three games
were modded and checked. Sky did not enumerate that Python dialog separately;
it was not acknowledged through another app's window. Process exit remains
unobserved at this phase; content commitment and final text do not assert0.

Installed-before-boots managed snapshot completed exit0:
MGS1 9files21010726bytes, MGS2 20244files2226361600bytes,
MGS3 8258files2090672328bytes. The comparison to the full pre-kit inventory
found9875 MGS2 and3790 MGS3 original backup files matching stock SHA256,
zero backup mismatches and no common-save or target-Steam-userdata differences
for any game. This comparison precedes any modded game boot.

## MGS1 first modded trial

Steam Play selected, actual game process50816 started15:44:07.
MGSM2Fix.log records v3.6.0 loaded and started, successful hooks, and
`MGSM2Fix64.asi` v3.6.0 was an actual loaded process module. The local
d3d11.dll loader v9.7.0 was also loaded. Thus injection was observed.
The screenshot rendered border artwork at58-61FPS with a black center.
Return then official H confirmation did not establish a title or playable
scene. The first observation lasted approximately47seconds; this does not
establish that black rendering is permanent. US/Max/4:3/SmoothingOff were
not independently selected in a first-time native settings screen.
Autosave SRAM writes appear in the game log; later save differences after
this boot must be distinguished from installer preservation.

Alt+F4 requested approximately15:44:53. Application Event1000 at15:44:54.067
reports exceptionc0000005 in METAL GEAR SOLID.exe, offset0x5d42b4,
process0xC680 (50816). Steam records game exit-1073741819 at15:45:03.
No force termination was used. Close/fault causality is unproven.
Result: injection observed, requested rendered/playable boot not established,
abnormal exit observed. See isolated screenshot and redacted runtime log.

## MGS2 first modded trial

Steam Play selected15:45:54, launcher52152 started15:45:56.
Actual loaded launcher modules: MGSHDFix.asi4.1.0.0 and
MGS2-Community-Bugfix-Compilation.asi3.0.0. Launcher rendered and accepted
Return after focusing the surface. The candidate boot-straight choice did
not skip the launcher. Navigated GameSelection, English, StartGame manually.
Actual game51636 started15:46:52 with `-region eu -lan en -selfregion EU
-launcherpath launcher.exe -ctrltype XBOX`.

Both launcher and game MGSHDFix logs report:

```
[MGSHDFix Config Helper] Failed to read config key 'MSX Skip Launcher Game' in section 'Launcher and Splashscreens': Key not found
Please run the MGSHDFix Config Tool to update your settings file.
```

The only targetable actual-game UI was its own error console, with this same
message. No console commands or migration were performed. Game modules at
15:47:36 confirm MGSHDFix4.1.0.0, Bugfix3.0.0, local WINHTTP/WININET9.7.4.
Installed settings SHA256:
`991c70959dd18e6633f39188e8de7cd10304beb8195df81b943d9f1c057062b7`.
Injection is distinct from failed configuration initialization; the
no-settings-schema-errors requirement fails on this exact candidate.
The configuration console stayed visible through15:48:09, game CPU0.703125,
responsive. WindowX requested15:48:16; Steam game exit-1073741510
(0xC000013A), launcher0 at15:48:18. No force termination was used.

## MGS3 first modded trial

Steam Play selected, launcher65716 started15:48:36. MGSHDFix launcher log
independently reported the same missing MSX Skip Launcher Game key.
Manually selected NorthAmerican/English/StartGame. Actual game72944 started
15:50:12 with `-region us -lan en -selfregion EU -launcherpath launcher.exe
-ctrltype XBOX`. Both game and launcher logs retain the missing-key error.
Only the game-owned error console rendered; no title/playable scene was
observed. Actual loaded local modules: MGSHDFix.asi4.1.0.0,
MGS3-Community-Bugfix-Compilation.asi2.0.1, WINHTTP/WININET9.7.4.
Settings SHA256:
`b1b53b46f9ed5a0af1b94ae31856c100190b28168182bc39a1dcad8c5a249c4c`.
WindowX requested15:51:15 after about63seconds. Steam game exit-1073741510,
launcher0 at15:51:16. No force termination or config migration.
The no-settings-schema-errors requirement independently fails for MGS3.

## Custom settings, repair and real concurrency

All game processes absent before changing installed preferences. The evidence
helper first asserted the wrong MGS1 section name before writing any file;
observed actual `[External Resolution]`, corrected helper, then executed0.
MGS1 external1024x768; MGS2 French/1280x720; MGS3 Spanish/1600x900.
MGS2 remainsEU, MGS3 remainsUS; chosen languages fit installed packs.
Candidate offline validator passes both HDFix settings; this does not waive
the live missing-key errors. `windows-custom-settings.json` retains precise
before/after hashes and values. MGS1 has no corresponding language key;
native US/language selection remains unproven.

The closed-game before-repair managed snapshot completed0 with all originals
hashed again. Snapshot helper initially aliased the single root bugfix version
cache as `<account>`; only numeric account directories are now redacted.
Original snapshots are retained unchanged; comparator normalizes the two
independently hash-verified aliases only. MGS2 version cache30bytes SHA
`002339fb1817e633fb7af6305068611f39ffcc611803a6216e57e16f3afe5b2d`;
MGS3 version cache37bytes SHA
`4ab3277ab612248887d3bc3528e2ebb7b71c74571c791f69f1c0577e2c9cd25d`.
Every snapshot path is unique. Game-write comparison identifies MGS1 remote
data/cache, MGS2/MGS3 launcher usersv and Steam cache changes since boot.
Protected pre-test copies remain available; installer-mutation preservation
will compare against this immediate pre-repair phase.

Second real candidate PID47032/session60596 was prearmed at Ready to install
for MGS2 only, no audio. First repair PID62488/session60857 selected all three,
no audio, supported ChangeSettings: Keyboard/Mouse prompts, boot-straightoff,
stereo/HQmovies/skiplogos unchanged. Native changed plan retained.
First actual repair started15:57:26, reached MGS2 verified downloads/extraction.
Second InstallNow clicked15:58:18. Its actual log records msvcrt LK_NBLCK
PermissionError13, then `Another installer is working on this game. Close it
and try again.` GameLock fails before InstallTxn and before downloading.
No second download, stage, settings write or commit appears in its log.
The first process continued legitimate MGS2 extraction; global file equality
is not claimed while that first process writes. Second final error dialog
not separately exposed and exit remains unobserved at this phase.
See second review, first progress and full refusal log. No synthetic lock
holder substituted for these two candidate processes.

## Repair completed and preserved storage

First repair reached all three verified manifests and Complete100% at16:02:44.
Final All done text was visually observed over Steam16:05:10; the native
Python dialog was not enumerated, so acknowledgement/exit remained unknown.
Immediate closed-game post-repair snapshot completed0. Comparison against
the immediate pre-repair phase has **no common-save or Steam-userdata hash
changes for any game**, and no mismatch among MGS2's9875/MGS3's3790 originals.
See windows-repair-comparison.json and windows-repaired-settings.json.
MGS1 retained1024x768; MGS2 retained French/EU1280x720; MGS3 retained
Spanish/US1600x900. Supported native changes to Keyboard/Mouse and boot-straight
off were saved independently. MGS1 language has no selected INI key and native
selection remains unproven; storage preservation does not establish gameplay.

MGS1 repaired boot PID49464 started16:05:58 and rendered the native launcher
at1024x768/60FPS, proving the selected external-resolution effect and changed
boot-straight preference. Return/focus/H did not reach native first-time
region/quality selections. AltF4 requested16:07:04–16:07:07; Application event
1000 fault16:07:07.4147536 c0000005/offset5d42b4; Steam exit16:07:12
-1073741819. No forced termination or close/fault causal claim.

After that process was absent, only the installed MGSM2Fix StartGame setting
was changed false→true for a separate follow-up (source/pins/schema unchanged).
INI SHA256 before b8e393c84b8499c05185516f4b1cb82f7c46ab238bc0a9787ef1ecee2a3a4aa8,
after496743c579abb1d5dd3c6333e79fb17534514e4ce746277b111668ce29d53c84.
Actual PID53988 launched16:08:34. At16:12:36 (four minutes), the1024x768
window still rendered border artwork/59FPS with a black center; Return/H had
not reached a title or playable scene. The intended two-minute bound was
exceeded during context refresh; the actual longer observation is retained.
AltF4 requested after that capture. Event1000 fault16:12:46.1174104,
c0000005/offset5d42b4; Steam16:12:50 exit-1073741819. Process absent16:12:57,
then immediate pre-removal snapshot began. Actual isolated screenshots and
MGSM2Fix logs are retained; no further repeat inferred a playable pass.

## Removal and pending-dialog cleanup

Exact local `py -3 install.py --uninstall` PID49176/session40728 rendered its
all-three checklist. After OK, the native yes/no messagebox had no returned
Sky window; fresh enumeration/selection recovery could not target it.
Native process had MainWindowHandle0/RespondingTrue. Its session log contained
only the header, no transaction. Our pending PID was terminated deliberately;
actual process exit1, no restoration/confirmation success claimed.

The recorded backend-selection harness runs the unchanged installer main
with only tkinter unavailable in that process, selecting its existing terminal
UI. Real inputs were blank=all3, then y after the immediate pre-removal snapshot.
Production restoration completed actual exit0: MGS2 removed486/restored9875;
MGS3 removed672/restored3790; MGS1 removed7. All kit recovery folders removed.
Full session log and terminal completion text/input sequence are retained.
There was no required-Steam-verification note. Read-only audit found candidate
loaders/configs/kit records absent, stock executables/builds unchanged and
MGS1 runtime log retained. Full closed-game stock hashing started16:17:54
before any post-removal stock boots. This fallback proves observed production
removal behavior, not successful native GUI confirmation.

At16:18:20, fresh65500/repair62488/refusal47032 were still our python.exe
install.py processes, RespondingTrue, MainWindowHandle0/title empty. Fresh
Sky enumeration again returned no targetable native dialog. With operations
finished/locks released, controlled cleanup terminated only those PIDs.
All three actual sessions returned exit1. These termination codes are kept
separate from verified content/completion/refusal outcomes; normal native
acknowledgement and successful natural process exits remain unproven.

Protected initial14/pre-kit16 file copies were independently rehashed after
removal: zero differences from their retained original protected hashes.
Current game-written source files differ from those older snapshots, so
source/copy inventory commands correctly return1; that is not damaged backup
or installer-induced save loss. Immediate mutation comparisons remain separate.

## UI access failures retained

After context refresh a `var` state binding was undefined; an attempted Play
action stopped before input. Recovered using persistent globalThis bindings.
MGS2 offscreen accessibility Play returned `element 3510 has no cached bounds`;
scrolled completed rows into view, refreshed, then launched the observed
control successfully. A Steam state returned an empty screenshots array even
though the tool displayed an image; an attempted screenshotId lookup stopped
before input. Fresh accessibility selection succeeded. After StartGame the
old launcher state capture returned `foreground window did not report a
process id`; fresh list_windows selected the actual game console.
These are separately recorded UI access outcomes, not invented game exits.
