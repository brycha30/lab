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

### qBittorrent tuning and Watchlist result

November 26: qBittorrent v5.3.1 queue limit changed from 50 active downloads / 40 active torrents to **12 downloads / 25 torrents**. Slow torrents remain excluded from these limits (2 KiB/s thresholds, 60-second inactivity), and uploads remain 10. Protocol encryption changed from `Require encryption` to `Allow encryption` to permit more peers; this is BitTorrent peer protocol compatibility, not the VPN tunnel. Anonymous mode remains enabled, network interface remains bound to `tun0`, DHT and PeX enabled, local peer discovery and router UPnP disabled. Gluetun exit IP in qBittorrent remained a Mullvad exit (`155.2.219.59`), and transfers resumed. Default save path is `/Main/media/.downloads/complete/unsorted`, incomplete path `/Main/media/.downloads/incomplete`; categories route movie downloads under `complete/movies`. TCP and μTP both enabled; 500 global connections, 100 per torrent. No global rate limit. Avoid changing the qBittorrent interface binding to `Any interface`.

*The Conversation* (1974, YTS) finished and Radarr imported a 1.8 GiB x264/AAC movie to `/Main/media/movies/The Conversation (1974) [tmdb-592]`. Host `stat` showed the library and completed-download files on device 44, inode 38942, link count 2, size 1,960,418,535 bytes: a verified hardlink. Plex's Discover detail page still displayed **Remove from Watchlist** after import, so downloading does not automatically remove that Watchlist entry. Keep the item until watched or implement a separately verified removal workflow; do not delete it in Radarr to manipulate Plex Watchlist.

Watchlist removal test: after the import, manually clicked **Remove from Watchlist** on the Plex Discover detail for *The Conversation*. The control changed to **Add to Watchlist**. Radarr still showed the movie as downloaded, monitored, and retained its 1.8 GiB YTS file. This verifies manual Watchlist removal does not delete the Radarr library file. It does not establish an automatic removal rule.

## Plex collection cleanup and deletion request (November 27, 2026)

Kometa generated 565 collections across Movies, Kids Movies, TV Shows, and Movies-Directors. At the owner's request, those collections were deleted through Plex's collection API. The four `Delete Requests` collections were preserved, one per library. This removed collection metadata, not media files. The collection inventory was saved on `dkr` as `/opt/dkr/config/kometa/collections-before-removal-20261127-001845.json`. Plex's native Categories tab still shows genres such as Action and Comedy.

The Kometa container is stopped with restart policy `no`. Its standalone Compose service now has profile `manual-kometa`, so a normal `docker compose up` does not start it. **Do not run Kometa manually with the old collection configuration**: `/opt/dkr/config/kometa/config.yml` still contains the collection rules because `watchlist-cleanup` reads Plex connection settings from that same file. A trial edit to remove those rules broke the helper's YAML parser; the file was restored from `config.before-collection-disable-20261127-002535.yml`, and the helper recovered.

*The Dry* (2021, Plex rating key 5901, TMDb 567797) was added to the Movies `Delete Requests` collection. Maintainerr imported it as a manual member at its 00:25 EST rule pass. The Movies rule is active, `deleteAfterDays=1`, `listExclusions=false`, and uses the Plex collection as its request queue. The stored addDate is `2026-11-27 05:00:00 UTC` (hour bucket), so inspect the next eligible rule pass on November 28 before claiming deletion. Verify removal from Plex and Radarr, filesystem cleanup, and absence of a Radarr exclusion. Until that pass, the deletion workflow is **partially verified**, not complete.

Maintainerr and `watchlist-cleanup` had lived in separate Compose projects with `network_mode: container:gluetun`. When Gluetun was recreated, both retained a stale container namespace. On November 27 the deployed `/opt/dkr/stack/docker-compose.yml` was backed up as `docker-compose.before-helpers-20261127-002645.yml`, then both helpers were added to the main `stack` project with `network_mode: service:gluetun` and `depends_on.gluetun.restart: true`. The old standalone `compose.yml` files were renamed `compose.yml.retired`. The Gluetun container ID did not change during migration. Maintainerr is healthy; watchlist cleanup recovered and completed a cycle with no errors. Keep helpers in the main stack when changing the VPN service.

The GitHub `stacks/stack/docker-compose.yml` is still an older sanitized template and does **not** match the full deployed Compose file. Reconcile it without copying live tokens, VPN keys, or application databases. The `watchlist-cleanup.py` script and its nonsecret deployment instructions also need a reviewed source home.

### Import verification (November 27, 2026)

*Gone Baby Gone* (2007) reached 100% in qBittorrent under category `movies-hl`, save path `/Main/media/.downloads/complete/movies`. Radarr then showed **Downloaded** at `/Main/media/movies/Gone Baby Gone (2007) [tmdb-4771]` with one 1.5 GiB x264/AAC YTS movie file and an `.srt` subtitle. This confirms the import and subtitle sidecar, but its inode and link count were not checked in this pass. qBittorrent displayed about 24.34 TiB free on its mounted path; that is not a measured TrueNAS pool available value and should not replace the earlier pool measurement.

The active queue showed 37 Radarr records and qBittorrent showed 17 stalled downloads during this check. Review those entries by tracker and availability before changing concurrency again or deleting them. The GitHub Compose reconciliation remains open because the deployed stack includes 14 services and mount differences; a partial template edit would misleadingly imply it mirrors production.

### Subsequent verification

On November 27, host `find` showed *Gone Baby Gone*'s imported MP4 and the completed torrent MP4 share device 44 and inode 38123, size 1,612,005,469 bytes, and link count 2. This confirms the import is a hardlink. The library also contains an `.srt` sidecar. *Apocalypto* (2006) has an `.en.srt` English subtitle sidecar beside its MKV under `/mnt/Main/media/movies/Apocalypto (2006) [tmdb-1579]`. These are filesystem checks; playback and subtitle rendering on Roku remain to be checked. All 14 services in the main media Compose project reported `running` at this check.

## Completion checklist (November 27)

- [x] Keep qBittorrent on Gluetun/tun0 and verify Mullvad exit; tune queue to 12 downloads / 25 torrents.
- [x] Keep download and import paths on the same mounted filesystem; verify hardlinks for *The Conversation* and *Gone Baby Gone*.
- [x] Restore Maintainerr and watchlist cleanup after Gluetun recreation; both now in the main Compose project.
- [x] Remove unwanted Kometa collections while preserving four `Delete Requests` collections; disable ordinary Kometa startup.
- [x] Confirm *Apocalypto* English subtitle sidecar exists.
- [ ] Test *The Dry* automatic deletion after the one-day grace period on November 28: Plex, Radarr, library file, completed torrent cleanup, and no exclusion. A follow-up is scheduled for 03:00 EST.
- [ ] Confirm *Kingdom of Heaven* Roadshow director's cut finishes, replaces the existing edition in the directors library, is correctly named and hardlinked, and plays with desired audio/subtitles. At this writing the torrent was 67% downloaded; the existing library file is an AAC edition.
- [ ] Reconcile the sanitized GitHub Compose with deployed production in full, including all paths, env variables and helper script. The branch now contains the helper service definitions, but the script is not yet tracked and the repository file remains a template. Validate `docker compose config` in a clean checkout before merging.
- [ ] Assess TrueNAS pool free space and snapshot/recycle behavior after allocation settles. Its browser UI showed a connection error during this pass; qBittorrent's 24.34 TiB mounted-path display is not a pool measurement.
- [ ] Review duplicate movie folders by Radarr instance and quality history, and inspect actual inode/link counts before reclaiming space. Do not remove a seeded hardlink until the library copy is verified.
- [ ] Review remaining artwork and Roku audio/playback exceptions on actual clients.
- [ ] Evaluate Usenet privacy, indexer/provider cost and retention before any subscription or migration; keep the existing VPN-bound torrent path working.

The 17 stalled torrents seen at 00:40 EST were *The Guardian* season 1 episode downloads, not 17 unrelated failures. Several have partial data. Retain them per the owner's earlier direction and look for viable sources through Sonarr before treating them as cleanup candidates. The directors torrent was actively transferring at about 3 MiB/s. The TrueNAS UI returned a connection error, so no new pool-space claim was made.
