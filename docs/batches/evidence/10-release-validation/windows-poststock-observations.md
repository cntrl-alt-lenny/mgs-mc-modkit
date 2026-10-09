# Post-removal stock observations

Worker, Windows 11 Pro build26300.9550, 2026-10-07. Action/Steam timestamps
below are local BST (UTC+1); snapshot JSON uses UTC. Candidate source,
pins/schema/version unchanged. Each game was closed before the next launched.

Full closed-game snapshot16:17:54–by16:31:05 completed0 before stock boots.
Former backup bytes match every restored live original: MGS2 9875 and MGS3
3790, zero mismatches. All common savedata and remote save bytes match the
immediate pre-removal phase. MGS1 remotecache.vdf alone changed; cause unproven.
MGS2/MGS3 target userdata unchanged. Full old-stock comparison has zero missing
files; all original assets/executables match. MGS2/MGS3 launcher/usersv changes
already predate removal. Extras are MGS1 MGSM2Fix.log and game-created
winbackup/meta_008_0000.bin, plus each MGS2/MGS3 Bugfix version-check cache.
No official asset mismatch or retained loader/config/recovery record.
See removal/stock-restoration comparisons and removed-audit.json.

## MGS1

Steam actual PID9376 launched16:32:24. Native Ver3.0.0 launcher rendered at
1913x1080 window/60FPS with PRESS ANY BUTTON. One supported Return input
did not advance to native region/quality selections or emulated title/gameplay.
Read-only module enumeration16:32:49: RespondingTrue/CPU4s, no MGSM2Fix,
MGSHDFix or Community-Bugfix modules. Same launcher-only boundary as initial
stock; playable/save loading remains unproven. Isolated screenshot retained.
WindowX close requested16:33:08; Steam16:33:09 exit0, process absent16:33:14.
No forced termination.

## MGS2

First Play action after scrolling produced no target process/log for40s.
Fresh capture showed settled rows moved after the earlier animated screenshot.
Refreshed/activated Steam and selected the observed settled MGS2 Play button;
no unrelated game launch/process was observed. This is a UI access/layout
outcome, not a stock game test failure.

Actual launcher PID30292 began16:34:36, Ver2.1.0/1920x1080/240FPS.
Supported Return navigated GameSelection→English→StartGame.
Actual game PID29724 began16:35:35 with region eu/lan en/selfregionEU/XBOX.
Read-only module enumeration16:35:58: RespondingTrue/CPU36.328125s, no
MGSM2Fix/MGSHDFix/Community-Bugfix modules. Real1920x1080 game rendered
Bluepoint logo60FPS; no prior missing-settings error console appeared.
Opening sequence rendered normally. Actual HDtitle60FPS observed16:39:21
(about3m46s after game start). One supported Return input left the title
unchanged through16:39:38; playable/menu/save loading remains unproven.
Isolated title screenshot retained. AltF4 close requested16:39:45;
Steam16:39:47 game29724 and launcher30292 both exit0; absent16:39:51.
Same rendered-title boundary as initial stock; no force termination.

## MGS3

Actual launcher PID11428 began16:40:07, Ver3.0.0/1280x720 windowed/240FPS.
Module enumeration16:40:25: RespondingTrue/CPU6.65625s, no candidate mod
modules. Supported Return navigated GameSelection→NorthAmerican→English→
StartGame. Actual game PID45580 began16:41:06, region us/lan en/selfregionEU/
XBOX. Enumeration16:41:21: RespondingTrue/CPU5.3125s, no candidate mod
modules. Actual window initially rendered black loading23FPS/HDlogo/Steam
overlay, no missing-settings error console. At16:46:50, the responsive game
rendered black/KONAMI logo60FPS, CPU657.140625s. Sampling delay exceeded the
intended two-minute bound; actual interval5m44s is retained. First windowX
request16:47:03 did not close. A fresh16:47:18 observation directly rendered
HDtitle60FPS; isolated logo/title screenshots retained. No playable input or
save-loading pass inferred. AltF4 requested16:47:27. Application event1000
fault16:47:27.7109220, c0000005/offset115f64, process0xB20C. Steam16:47:32
game45580 exit-1073741819 and launcher11428 exit0. All targets absent16:47:52.
No forced termination or close/fault causal claim. Same exception/offset as
the initial pre-kit stock fault; candidate mod modules were absent.

## Final machine state

Closed-game final managed snapshot completed0. MGS1 common/target userdata
unchanged since removal; MGS2/MGS3 launcher usersv and Steam cache changed
after these stock boots. Actual gameplay save files remained unchanged.
Final audit16:48:46BST again found loaders/mod configs/all kit recovery
records absent, original executable hashes/builds unchanged. Native target
process query returned none; Sky returned no game window. Steam UI showed
all three Play buttons, no downloads queued, network/disk0bps.
Private initial14/pre-kit16 protected copies remain intact and available;
no save data, credentials or licensed payloads are distributed in evidence.
