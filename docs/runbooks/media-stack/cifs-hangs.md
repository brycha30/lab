Runbook: Deluge / Sonarr / Radarr CIFS-Induced Hangs and Sonarr Custom Formats (Plex-Friendly)

1. Environment Context

Host / Container
- Proxmox LXC: Docker LXC (community-scripts)
- Hostname: docker
- IP: 192.168.1.31
- OS: Debian GNU/Linux 12
- Observed uptime during issue: 1–2 hours
- Memory: 16 GiB RAM, 4 GiB swap

Docker Services
- deluge
- sonarr
- radarr
- bazarr
- bazarr-kids
- jackett
- flaresolverr
- firefox
- vpn
- portainer
- omada-controller
- dashy
- caddy
- cloudflare-ddns

Network / Storage
- NAS IP: 10.10.10.2
- Primary CIFS share: //10.10.10.2/Main
- Host mount: /mnt/Main
- Deluge container bind: /Main

Torrent Paths (Deluge)
- /Main/torrents
- /Main/torrents/incomplete
- /Main/torrents/downloads
- /Main/torrents/seed

Deluge
- Daemon: localhost
- Port: 58846
- Auth file: /config/auth
  localclient:<hash>:10
  bryan:3bryan111:10
  dad:3bryan111:10

2. Problem Statement

- Deluge CLI commands (e.g. resume *) intermittently hang for 30–60 seconds
- System load previously spiked above 100, later normalized, but commands still stalled
- Sonarr and Radarr activity intermittently blocked or stalled
- Issue occurred while torrents were seeding or downloading to CIFS-mounted storage
- Goal:
  - Stabilize Deluge under CIFS load
  - Configure Sonarr and Radarr custom formats for Plex Direct Play
  - Ensure compatibility with Roku, Samsung TV, and Fire TV Cube

3. Root Cause

Primary Root Cause:
- CIFS/SMB instability to NAS at 10.10.10.2

Evidence from kernel logs:
- CIFS: VFS: \\10.10.10.2 has not responded in 180 seconds
- Error -512 sending data on socket
- No writable handle in writepages rc=-9
- Repeated mount retries
- BAD_NETWORK_NAME errors for //10.10.10.2/KidsMain

Impact:
- Kernel I/O waits caused processes to block
- Deluge daemon blocked on disk I/O, causing CLI commands to appear hung
- Sonarr and Radarr .NET tasks blocked by kernel hung-task detector

Explicitly ruled out:
- Authentication issues (deluge-console info worked)
- Deluge daemon crash
- CPU or RAM exhaustion

4. Final Fix / Known-Good Configuration

4.1 Deluge Stability Tuning

Goal:
- Reduce CIFS pressure by limiting concurrent activity

Command executed:

docker exec -it deluge sh -lc \
'deluge-console -d 127.0.0.1 -p 58846 -U bryan -P 3bryan111 \
"config -s max_active_downloading 1; \
config -s max_active_limit 2; \
config -s max_connections_global 200; \
config -s max_upload_slots_global 20; \
config -s max_connections_per_second 10"'

4.2 Sonarr / Radarr Custom Formats (Plex-Friendly)

Design Goal:
- Maximize Plex Direct Play
- Minimize transcoding on Roku, Samsung TV, Fire TV
- Avoid large remuxes and unsupported codecs

Preferred Formats:
- Video: H.264 (x264 / AVC)
- Audio: AC3
- Audio: AAC

Penalized:
- Video: HEVC (x265)

Heavily Penalized or Blocked:
- Video: AV1
- Video: VC-1
- Container: AVI
- REMUX

Audio to Avoid:
- DTS
- TrueHD / Atmos
- FLAC
- Opus

Example Scoring (Profile → Custom Formats):

Video – H.264 (x264/AVC): +500
Audio – AC3 (Preferred): +300
Audio – AAC (Preferred): +200
Video – HEVC (x265): -200
Audio – Opus: -2000
Audio – FLAC: -2500
Container – AVI: -3000
Audio – DTS: -4000
Audio – TrueHD / Atmos: -5000
Video – AV1: -5000
REMUX: -10000

Effect:
- Ensures Plex Direct Play
- Prevents unnecessary transcoding
- Avoids oversized media files

5. Exact Commands Used

Verify Deluge connectivity:

docker exec -it deluge sh -lc \
'deluge-console -d 127.0.0.1 -p 58846 -U bryan -P 3bryan111 "info"'

Pause all torrents:

docker exec -it deluge sh -lc \
'deluge-console -d 127.0.0.1 -p 58846 -U bryan -P 3bryan111 "pause *"'

Resume a specific torrent:

docker exec -it deluge sh -lc \
'deluge-console -d 127.0.0.1 -p 58846 -U bryan -P 3bryan111 \
"resume ace60cbfcc458a07b4741941afbd6ea1bffcfc60"'

Check mounts inside container:

docker exec -it deluge sh -lc 'df -hT'

Kernel diagnostics:

dmesg -T | egrep -i "blocked for more than|cifs|smb|nfs|hung task"

6. Verification Steps

- df -hT shows //10.10.10.2/Main mounted at /Main
- deluge-console info returns torrent list without auth errors
- Load average drops to normal range (below 20)
- docker stats shows Deluge CPU below 5 percent during idle or seeding
- Sonarr and Radarr no longer stall during import or rename
- Plex reports Direct Play on Roku, Samsung TV, and Fire TV clients

7. Warnings / Do-Not-Do-Again Notes

DO NOT allow unlimited Deluge connections on CIFS mounts.

DO NOT run heavy REMUX or DTS/TrueHD content unless Plex transcoding is acceptable.

DO NOT assume Deluge CLI hangs are authentication failures; check kernel I/O first.

AVOID unstable or misnamed CIFS shares (e.g. KidsMain BAD_NETWORK_NAME).

CIFS instability manifests as application hangs, not clean errors.

If CIFS issues persist:
- Move torrents to local disk
- Or migrate CIFS to NFS with proper mount options

8. Next Hardening (Future Work)

- Switch torrents from CIFS to local disk with move-complete job
- Migrate CIFS to NFS with correct topology and mount options
- Add Deluge label-based throttling per media type
- Add Sonarr and Radarr import delays during CIFS reconnect events
