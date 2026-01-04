Docker Media Stack – VPN + Config Corruption Recovery Runbook
(Downloads VM – VMID 1032)

1. Environment Context

Host / VM
- VMID: 1032
- Hostname: downloads
- OS: Linux (Proxmox VM)
- User: root
- VM IP: 192.168.1.32

Docker Stack Location
- Stack directory:
  /mnt/Main/docker-projects/downloads

Storage

NAS-mounted media (kept on NAS):
- /mnt/Main        -> /Main
- /mnt/Main/KidsMain -> /KidsMain

Configs (migrated to VM local disk):
- /opt/docker-projects/downloads/config/<service> -> /config

Containers / Services

VPN
- Container: gluetun
- Provider: Private Internet Access (PIA)
- VPN Type: OpenVPN (UDP)
- Region: Brazil (São Paulo)
- Tunnel interface: tun0
- Public VPN IP (inside containers): 146.70.98.43

Core Services
- Download client: qbittorrent
- Indexer manager: prowlarr
- Automation:
  - sonarr
  - sonarr-kids
  - radarr
  - radarr-kids
- Subtitles:
  - bazarr
  - bazarr-kids
- CAPTCHA helper: flaresolverr

Network / Ports (via gluetun)

Web Interfaces
- qBittorrent: 8080
- Prowlarr: 9696
- Sonarr: 8989
- Sonarr-Kids: 8990
- Radarr: 7878
- Radarr-Kids: 7879
- Bazarr: 6767
- Bazarr-Kids: 6768
- FlareSolverr: 8191

qBittorrent Incoming
- TCP 6881
- UDP 6881

2. Problem Statement

Observed issues:
- Prowlarr failed to start
- Error: /config/prowlarr.db is corrupt
- SQLite errors:
  - database is locked
  - disk image is malformed
- WebUI ports intermittently unreachable
- curl http://192.168.1.32:9696 failed
- curl http://127.0.0.1:9696 reset connection
- docker-compose.yml repeatedly became invalid
- YAML parse errors
- Ports block malformed
- Scripts failed due to NAS filesystem rename behavior

3. Root Cause

Primary Root Cause
- SQLite databases stored on NAS-mounted CIFS/NFS shares
- SQLite is NOT safe on network filesystems
- Resulted in locked and corrupted prowlarr.db

Secondary Causes
- docker-compose.yml stored on NAS
- In-place edits (sed -i, perl -i) failed due to NAS rename semantics
- Malformed YAML created invalid ports mapping

Example of broken ports entry:
- "6881:6881/udp"   followed by inline merge with "8989:8989"

4. Final Fix / Known-Good Configuration

Design Decision
- Keep media on NAS
- Move all /config volumes to VM local disk
- Leave gluetun network_mode architecture intact

Environment Variables (.env)
ROOT=/mnt/Main/docker-projects/downloads
LOCAL_ROOT=/opt/docker-projects/downloads
PUID=1000
PGID=1000
TZ=America/New_York

Final docker-compose.yml (Key Sections)

gluetun (ports cleaned)
- Exposed ports explicitly
- Firewall input ports aligned with services
- No duplicate mappings

gluetun ports:
- 8080
- 9696
- 8989
- 8990
- 7878
- 7879
- 6767
- 6768
- 8191
- 6881 (TCP)
- 6881 (UDP)

prowlarr (local config)
- network_mode: service:gluetun
- /config mapped to:
  /opt/docker-projects/downloads/config/prowlarr

Example: sonarr
- network_mode: service:gluetun
- /config mapped to:
  /opt/docker-projects/downloads/config/sonarr
- Media mounted from:
  /mnt/Main -> /Main

Same pattern applied to:
- qbittorrent
- sonarr-kids
- radarr
- radarr-kids
- bazarr
- bazarr-kids
- flaresolverr

5. Exact Commands Used

Create local config directories
Command:
mkdir -p /opt/docker-projects/downloads/config/{qbittorrent,sonarr,sonarr-kids,radarr,radarr-kids,prowlarr,bazarr,bazarr-kids}
chown -R 1000:1000 /opt/docker-projects/downloads/config

Stop and restart stack
Command:
cd /mnt/Main/docker-projects/downloads
docker compose down
docker compose up -d

Verify VPN routing
Command:
docker exec -it qbittorrent sh -c 'wget -qO- https://ipinfo.io/ip; echo'
docker exec -it gluetun sh -c 'wget -qO- https://ipinfo.io/ip; echo'

Verify mounts
Command:
docker inspect prowlarr --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
docker inspect sonarr --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
docker inspect qbittorrent --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'

Validate compose file
Command:
docker compose config

6. Verification Steps

- docker compose ps shows all containers Up
- curl http://192.168.1.32:9696 returns HTTP 200
- docker logs prowlarr shows no SQLite errors
- ipinfo.io/ip matches VPN IP inside gluetun and qbittorrent
- Config paths resolve to /opt/docker-projects/...
- Media paths remain /mnt/Main and /mnt/Main/KidsMain

7. Warnings / Do-Not-Repeat Notes

DO NOT store SQLite-backed /config directories on NAS

DO NOT edit docker-compose.yml in-place on NAS
- sed -i
- perl -i

DO NOT allow malformed YAML in ports
- One bad line breaks entire stack

DO NOT duplicate port mappings
- 6881 previously appeared multiple times

ALWAYS validate configuration
Command:
docker compose config

ALWAYS:
- Keep configs on local disk
- Keep media on NAS
- Use network_mode: service:gluetun only for VPN-routed containers

8. Status

- Stack stabilized
- Prowlarr recovered (fresh local config)
- VPN routing verified
- YAML corrected
- Architecture now SQLite-safe
