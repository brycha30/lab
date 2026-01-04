IPTV Setup Runbook – Fire TV Cube + TiviMate (Gold Club IPTV)

1. Environment Context

Device
- Client: Amazon Fire TV Cube
- OS: Fire OS
- Player App: TiviMate (free version initially)

IPTV Provider
- Service: Gold Club IPTV
- Account Type: 48-hour free trial

IPTV URLs (from provider email)

M3U Playlist (Live TV)
http://cdn.goldclub.tv/playlist/2811600347/4115756289/m3u_plus

EPG (XMLTV)
http://cdn.goldclub.tv/xmltv.php?username=2811600347/4115756289

Host / Base URL
http://cdn.goldclub.tv/

2. Problem Statement

- IPTV channels load successfully in TiviMate
- TV Guide (EPG) shows “No information”
- Uncertainty whether TiviMate Premium is required
- Errors encountered when entering EPG URL
- Desire to create a US-only guide / EPG view

3. Root Cause

EPG URL entry errors
- Hidden spaces, wrong protocol, missing slashes common on Fire TV input

EPG not automatically bound
- Playlist and EPG must be manually linked on first setup

TiviMate refresh behavior
- Playlist and EPG updates must be triggered manually

Fire TV Cube cache behavior
- Failed EPG attempts remain cached until device reboot

Provider limitations
- Partial or inconsistent EPG data is normal
- Many international channels have no guide data

Premium misconception
- TiviMate Premium is NOT required for basic EPG functionality

4. Final Fix / Known-Good Configuration

Playlist Configuration (TiviMate)
- Playlist type: TV playlist
- Playlist URL:
  http://cdn.goldclub.tv/playlist/2811600347/4115756289/m3u_plus

EPG Configuration (TiviMate)
- EPG Source URL:
  http://cdn.goldclub.tv/xmltv.php?username=2811600347/4115756289
- EPG bound to: Gold Club playlist
- EPG update method: Manual + app-level refresh

US-Only Guide Configuration
- Method: Playlist group filtering

Path:
Settings → Playlists → gold club → Manage groups

Groups left enabled (examples):
- USA
- US LOCALS
- NFL PREMIUM
- NBA PREMIUM
- NHL PREMIUM
- ESPN+

All non-US groups disabled

5. Exact Steps / Paths

Re-enter EPG URL (clean method)
- TiviMate → Settings → Playlists → gold club → EPG
- Remove existing EPG source
- Add source
- Enter:
  http://cdn.goldclub.tv/xmltv.php?username=2811600347/4115756289
- Confirm / OK

Force Playlist Rebind
- TiviMate → Settings → Playlists → gold club → Update playlist

Force EPG Refresh
- TiviMate → Settings → EPG → Update EPG
- Wait 2–3 minutes
- Do NOT exit the app during refresh

Fire TV Cube Cache Reset (critical)
- Fire TV Settings → My Fire TV → Restart

6. Verification Steps

Playlist Verification
- TV → All channels
- Sports groups visible (NFL, ESPN, etc.)

EPG Verification
- TV → Guide
- Scroll right on major US channels

Confirm:
- Program titles appear
- Time blocks populate

Success criteria:
- At least some channels display guide data

7. Warnings / Do Not Do This Again

DO NOT use HTTPS for EPG

Wrong:
https://cdn.goldclub.tv/xmltv.php

Correct:
http://cdn.goldclub.tv/xmltv.php

DO NOT assume Premium fixes EPG
- Premium unlocks UI features only
- It does NOT add missing provider guide data

DO NOT expect full EPG coverage
- International channels often have no guide
- Overflow sports feeds may be blank

ALWAYS reboot Fire TV Cube after first EPG setup
- Cached failures persist without restart

DO NOT edit playlist and EPG simultaneously
Always:
1. Update playlist
2. Update EPG
3. Restart device

8. Optional Enhancements

Manual EPG mapping
- Channel → Long-press OK → Assign EPG

Favorites-only US guide
- Channel → Add to Favorites
- View Favorites group

TiviMate Premium (optional)
- Favorites sorting
- Multi-playlist support
- Catch-up (if provider supports)

9. Final Status

- Playlist working
- EPG URL confirmed correct
- Channels loading
- Partial EPG expected (provider limitation)
- US-only guide achievable via group filtering
