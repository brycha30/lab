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

## Space accounting and watchlist check (November 26, 2026)

TrueNAS `main_pool` showed 42.84 TiB usable, 23.91 TiB used, and 18.93 TiB available before cleanup. After deleting eleven daily snapshots of **only** `main_pool/Main/media` dated November 13–23, the dashboard showed about 18.94 TiB available and 23.86 TiB used. November 24–26 media snapshots remained. `main_pool/Main/torrents` is a separate dataset and its snapshots were not selected. The pool's free space is shared, so deleting media snapshots can increase space available to torrents without deleting torrents.

Also removed 80 single-link media trash files totaling 2.82 GiB in apparent file size. A manifest on `dkr` is `/opt/dkr/config/media-trash-single-link-cleanup-2026-11-26.json`. File sizes and rounded pool numbers do not establish exact physical space reclaimed: hardlinks and snapshots can retain blocks. Measure the pool before and after a quiet interval with `zpool list -o name,size,alloc,free,freeing main_pool` and inspect dataset snapshots before further deletion.

The Radarr recycle folder `/mnt/Main/.recycle-bin/movies` had about 154 GiB of recent single-link files. Radarr's seven-day recycle cleanup was configured; retain the recovery window while replacements import. Confirm which movie is tracked and playable before purging any recycle item. The recycle folder lives under `Main`, outside the `media` dataset.

Regular Radarr now has a Plex Watchlist import list authenticated to the owner's Plex account. It adds movies under `/Main/media/movies` with `DirectPlay 1080p`; *The Conversation* (1974, TMDb 592) was added as a test and reached qBittorrent, category `movies-hl`, save path `/Main/media/.downloads/complete/movies`. At this writing it was queued with no metadata or bytes. Check completion, Radarr import, inode/link count, Plex availability, and whether the Plex Watchlist entry remains. The import list reads the watchlist; do not assume it removes entries after download. Plex's own automatic removal setting concerns playback of Plex Movies & Shows, not necessarily local library import.

### Retired torrents dataset snapshots

On November 26, the separate `main_pool/Main/torrents` NFS export was mounted read-only for inspection and its live directory was empty. qBittorrent's active downloads were under `/Main/media/.downloads`; the deployed Compose file had no `/Main/torrents` reference. TrueNAS still allocated 6.52 TiB to fourteen daily torrents snapshots (November 13–26). With owner authorization, all fourteen were deleted through TrueNAS. The snapshots list then showed 0 of 0 and `main_pool/Main/torrents` allocation fell to 219.38 KiB. The empty dataset and NFS share remain. Pool available initially moved from about 18.96 to 19.17 TiB while ZFS freed blocks; recheck later before claiming final physically reclaimed space. Do not mistake the small placeholder file at `/mnt/Main/torrents` on the parent NFS mount for the child dataset; inspect the child NFS export directly.
