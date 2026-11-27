# Media stack first response

Verified November 26, 2026. Docker runs in Proxmox VM 1033 (`dkr`, 192.168.1.33), and Plex is at 192.168.1.35. The deployed media Compose file is `/opt/dkr/stack/docker-compose.yml`. TrueNAS is mounted on the Docker host at `/mnt/Main`.

## Check host and storage first

```sh
qm status 1033
qm guest exec 1033 -- uptime
qm guest exec 1033 -- df -h /mnt/Main/media
```

On `dkr`, check `findmnt /mnt/Main`, `df -h /mnt/Main/media`, and `docker ps`. If a storage operation hangs, investigate NAS and network I/O before restarting Docker.

## Check the stack

```sh
cd /opt/dkr/stack
docker compose config --quiet
docker compose ps
docker logs --tail=100 gluetun
```

Radarr, Sonarr, qBittorrent, Prowlarr, and Bazarr share Gluetun's network namespace. When Gluetun is recreated, dependent containers can retain a stale namespace; recreate the affected services and verify their WebUIs. Seerr/Overseerr lives under `/opt/dkr/plex-plugins` and also depends on this namespace. Port 5055 must be published and allowed in Gluetun.

The host `/mnt/Main` maps to `/Main` in Sonarr and regular Radarr. Kids and directors also use `/KidsMain` and `/DirMain`. Downloads and libraries must be on the same filesystem for hardlinks. Check device, inode, and link count before assuming an import was hardlinked.

Back up app configuration before changing paths or databases. Do not commit the live `.env` or VPN keys. Avoid a broad `docker compose down` for a single service problem; it interrupts all media services.
