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

The GitHub `stacks/stack/docker-compose.yml` is still an older sanitized template and does **not** match the full deployed Compose file. Reconcile it without copying live tokens, VPN keys, or application databases. The deployed `watchlist-cleanup.py` source and nonsecret deployment instructions were subsequently added to this branch; see the tracked-helper section below.

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
- [x] Confirm *Kingdom of Heaven* Roadshow director's cut finished and replaced the tracked AAC edition in the directors library. The 17.2 GiB EAC3 file is correctly edition-named.
- [ ] Check director playback and subtitles on Roku. The torrent data was removed after import; current link count 1 cannot establish whether the import originally hardlinked.
- [ ] Reconcile the sanitized GitHub Compose with deployed production in full, including all paths, env variables and helper script. The branch now contains the helper service definitions and a byte-verified helper script, but the Compose file remains a template requiring populated restore variables. Validate `docker compose config` in a clean checkout before merging.
- [x] Recheck TrueNAS pool: dashboard shows 24.18 TiB free and pool ONLINE on November 27.
- [ ] Confirm snapshot and recycle retention against the pool trend after the deletion timer runs.
- [ ] Review duplicate movie folders by Radarr instance and quality history, and inspect actual inode/link counts before reclaiming space. Do not remove a seeded hardlink until the library copy is verified.
- [ ] Review remaining artwork and Roku audio/playback exceptions on actual clients.
- [ ] Evaluate Usenet privacy, indexer/provider cost and retention before any subscription or migration; keep the existing VPN-bound torrent path working.

The 17 stalled torrents seen at 00:40 EST were *The Guardian* season 1 episode downloads, not 17 unrelated failures. Several have partial data. Retain them per the owner's earlier direction and look for viable sources through Sonarr before treating them as cleanup candidates. The directors torrent was actively transferring at about 3 MiB/s. The TrueNAS UI returned a connection error, so no new pool-space claim was made.

### Usenet decision note (November 27)

Do not subscribe or enable a new download client yet. The existing VPN-bound torrent workflow is importing and hardlinking. A Usenet trial would require both a provider and an indexer, adding recurring cost and credentials. SABnzbd can use TLS to a provider (commonly port 563), but TLS alone still exposes the provider destination to the network; keep any future client in the existing Gluetun namespace if the owner's anonymity preference applies. Use a separate download category rooted under `/Main/media/.downloads/complete/usenet` on the same filesystem, then verify import and hardlink before making it a preferred downloader. Check certificate verification and avoid disabling it to work around errors.

Provider pricing is fluid. On November 27, Newshosting publicly listed Lite at $10/month for 50 GB and Unlimited at $12.95/month on its site; UsenetServer described variable term pricing and 20 SSL connections. These are vendor claims, not a commitment or a complete cost comparison. Sources: https://www.newshosting.com/ , https://support.usenetserver.com/kb/article/176-how-much-does-the-service-cost/ , https://sabnzbd.org/wiki/extra/firewalls-and-virus-scanners , https://docs.linuxserver.io/images/docker-sabnzbd/ . Compare a provider, an indexer, cancellation terms, and actual completion on a small legal test before paying for a longer term.

### Duplicate-folder audit

A shallow scan of the three movie library roots found one folder with multiple video files: `UFC.310.Pantoja.vs.Asakura.PPV.1080p.WEB.h264-VERUM` under `/mnt/Main/media/movies`. It contains two 8,461,748,733-byte MKVs with different inodes (5237 and 5869), each link count 1, and matching modification time. The filenames differ. Content identity was not yet established, so neither was removed. Regular Radarr search did not show an existing `UFC 310` movie result. Compare content in bounded memory and verify Plex references before deleting one; this is potentially about 7.88 GiB of reclaimable apparent data, subject to snapshots.

### Guest-agent interruption during duplicate audit (November 27)

A Python content comparison mistakenly used `Path.read_bytes()` on each 8,461,748,733-byte UFC file inside the 8 GiB Docker VM. Linux OOM protection killed that Python process (the VM console logged `Out of memory: Killed process ... (python3)`); Proxmox subsequently reported `QEMU guest agent is not running`. The VM itself stayed running at about 3.68 GiB used, and qBittorrent's WebUI continued serving transfers through the Mullvad exit. The two files were not modified. Restore `qemu-guest-agent` from an authenticated guest console, check `journalctl -k` for the OOM event, and verify all 14 containers before further file work. Do **not** use `read_bytes()` for multi-gigabyte files; compare with bounded memory, for example `cmp -s -- FILE1 FILE2`, after checking service health. The qBittorrent queue later showed 75 torrents, 12 stalled, and the director's cut at 69.5% but stalled; inspect peer availability before changing the queue limits.

At the subsequent WebUI check, qBittorrent's visible list had 71 torrents and filtering by `The Guardian` returned no rows; Sonarr's queue contained only *The Neighborhood* S07E16. The previously observed Guardian entries are therefore no longer in either active queue. This pass did not establish whether Sonarr removed them, they completed/imported, or another cleanup rule acted. Inspect Sonarr history and files before attempting to regrab. Radarr-Kids Media Management shows `/KidsMain/media/kidsmovies` as its sole root, hardlinks enabled, extra subtitle files enabled, and a seven-day recycle cleanup. The qB category `movies-kids-hl` alone is not evidence that a title is appropriate for children; *Suicide Squad* (2016) appeared queued under it and needs a library ownership check.

### Recovery and Plex manual requests (November 27)

The QEMU guest agent recovered without a restart: `qm agent 1033 ping` succeeded; `systemctl is-active qemu-guest-agent` returned `active`. The VM had 4.5 GiB available memory and 3.4 GiB swap in use after the OOM. `docker compose config --quiet` succeeded. The **main** `/opt/dkr/stack` Compose project has 13 running services (not 14); earlier counts conflated a separate project. `maintainerr` and `watchlist-cleanup` both report `running`.

The owner added UFC 310: Pantoja vs. Asakura (Plex key 7373), UFC Fight Night 259: Lopes vs. Silva (key 7371), and UFC 320: Ankalaev vs. Pereira 2 (key 7389) to the Movies `Delete Requests` collection. Along with *The Dry* (key 5901), Maintainerr's SQLite `collection_media` table shows four members with `addDate=2026-11-27 05:00:00 UTC`, `isManual=1`, `includedByRule=0`. Logs confirm Plex collection sync. **Manual membership is eligible for the same one-day collection-handler deletion timer**; it is only ignored by rule matching/eviction. Maintainerr's documentation confirms this distinction: https://docs.maintainerr.info/3.30.2/collections/#manual-membership-badge . Inspect after the next eligible handler pass, including Plex, Radarr ownership, filesystem, torrent hardlinks, and no exclusions. One UFC Fight Night item was already marked `In Trash` in Plex; do not infer its backing file still exists.

Maintainerr shares Gluetun's namespace. On November 27, the deployed Compose file added TCP 6246 to Gluetun's published ports and `FIREWALL_INPUT_PORTS`. Caddy routes `maintainerr.md-chamberlain.com` through the existing `local_only_http` snippet to `http://192.168.1.33:6246`, with Cloudflare DNS challenge TLS. The OPNsense `maintainerr` A override for 192.168.1.33 was applied. Dashy's Media Stack section now links to `https://maintainerr.md-chamberlain.com`. The HTTPS page opened the Maintainerr Overview and Dashy displayed its tile.

Adding a Gluetun published port recreated that VPN container. The main project's 11 dependent apps were recreated to bind the new network namespace; Maintainerr itself was recreated earlier. The separate `/opt/dkr/plex-plugins` Overseerr service also required `docker compose up -d --force-recreate --no-deps overseerr`. After startup, HTTP checks on 6246, 8080, 6767 returned 200; Radarr 7878 and Prowlarr 9696 returned login redirects (302), Sonarr 8989 returned 401, and Overseerr 5055 returned 307. The main project again reported 13 running services. Gluetun reported healthy and Mullvad exit `155.2.219.59` (Brazil). qBittorrent's UI opened its login page after restart; transfer status still requires an authenticated check. Recreate dependencies after any future Gluetun recreation, and verify endpoints before declaring recovery. On November 27 after allocation settled, TrueNAS Datasets showed `main_pool` 17.35 TiB used and 24.33 TiB available, compared with the earlier 23.91 TiB used and 18.93 TiB available reading. Available space increased about 5.40 TiB, but intervening writes and deletions mean this is a net pool change, not a precise per-operation reclaim figure.


### Post-restart transfer check (November 27)

qBittorrent WebUI was reauthenticated. It reported Connected, external IP `155.2.219.59` (Mullvad), 67 torrents, 13 active, and no errors. *Kingdom of Heaven* Roadshow director's cut was at 88.4% and transferring around 2.1 MiB/s, later 89.5% around 2.7 MiB/s. Radarr-directors queue contained the matching Bluray-1080p release with `Directors / Extended Editions (GOOD)` and one active download. Existing library file remained a 3.6 GiB AAC 5.1 RARBG edition with `.en.srt`. Verify its replacement, edition name, hardlink and playback after completion.

Radarr-Kids tracks *Suicide Squad* (2016, PG-13) at `/KidsMain/media/kidsmovies/Suicide Squad (2016)` with an existing 3.2 GiB HDTV-1080p AAC 2.0 file and English subtitle. It also queued a YTS upgrade under `movies-kids-hl`. This is a library classification decision, not merely a mislabeled orphan torrent. Do not remove the existing file or change the movie's ownership until deciding the intended age policy and preserving it in the regular library if appropriate.


### Director's cut import (November 27, later check)

qBittorrent reached 100% for *Kingdom of Heaven* Roadshow (`movies-directors-hl`). Radarr-directors held it as `Downloaded - Waiting to Import` because the new release scored 1000 for `Directors / Extended Editions (GOOD)`, below the existing AAC/x264 file's 1700. Manual import of the specific 17.2 GiB `hallowed` MKV completed. Radarr now shows one file named `Kingdom of Heaven (2005){edition- Directors Cut} - Bluray-1080p Proper x264EAC3-hallowed [tmdb-1495].mkv`, 18,470,677,081 bytes, `Downloaded`. File details report 3:13:53 runtime, 1920x804 x264, English EAC3 5.1 at 640 kbit/s, and embedded English subtitles. The former 3.6 GiB AAC file is no longer the tracked movie file. Inspect the Radarr recycle bin for its recovery copy, verify inode/link count against the completed torrent, and test Plex/Roku playback. Proxmox's browser session expired before the inode check; do not assert hardlinking from paths alone.

### Director's cut inode and recycle check (November 27, later)

On `dkr`, the imported 18,470,677,081-byte MKV under `/mnt/Main/media/movies-directors/Kingdom of Heaven (2005) {tmdb-1495}` reported device 99, inode 38190, **link count 1**. Searches under `/mnt/Main/media/.downloads/complete/movies-directors` and the wider `.downloads` tree found no matching completed torrent file. The completed `movies-directors` folder contained zero files. The library currently has no seeding-side hardlink. This does **not** establish whether the manual import initially moved, copied, or hardlinked it: Radarr-directors has `Use Hardlinks instead of Copy` enabled, and its qBittorrent client has `Remove Completed` enabled. qBittorrent currently has zero `movies-directors-hl` torrents, so the torrent data may have been removed after import and the library link count would then fall to one. Check Radarr history and download-client removal logs before assigning a cause. The old 3,882,613,625-byte AAC MP4 and 82,522-byte subtitle are in `/mnt/Main/.recycle-bin/movies/Kingdom of Heaven (2005) {tmdb-1495}`, outside the media dataset. Keep the recovery copy until director playback is checked, then let the seven-day recycle policy handle it. This is distinct from the verified automatic hardlinks for *The Conversation* and *Gone Baby Gone*. Investigate why the director torrent data vanished and correct the custom-format score that blocked its automatic upgrade before another director test.

### November 27 live configuration and capacity check

Chrome access recovered. Radarr-directors confirms `Use Hardlinks instead of Copy` and `Automatically import completed downloads` are enabled. Its qBittorrent client uses category `movies-directors-hl`, `Remove Completed` is enabled, and no post-import category is set. qBittorrent currently lists zero torrents in `movies-directors-hl`. Radarr history shows the *Kingdom of Heaven* release grabbed and imported at 06:40, then the former file deleted. The new tracked file scores +1000 for `Directors / Extended Editions (GOOD)`; the old AAC/x264 file had scored 1700, which prevented the automatic upgrade before manual import. The H.264 custom format matches the release title regex `\\b(x264|h\\.264|h264|avc)\\b`; the current renamed file reports x264 video but scores no H.264 format. Diagnose the original release-title match and audio preferences before altering the profile broadly. A link count of one after torrent removal cannot prove the import method.

TrueNAS dashboard showed `main_pool` ONLINE, 24.18 TiB free, 42.12% used, and 0 of 10 disks with errors. This is about 0.15 TiB less free than the earlier 24.33 TiB reading; it is a point-in-time net pool reading, not cleanup attribution.

The deployed main Compose project and GitHub branch each list 13 services. The branch template now includes the deployed `maintainerr` and `watchlist-cleanup` container safeguards (capabilities dropped, no-new-privileges, 5 MiB x 2 log rotation; the cleanup helper is read-only with `/tmp` tmpfs). Downloaded the branch template to `/tmp/media-stack-pr-compose.yml` on `dkr` and ran `docker compose -f /tmp/media-stack-pr-compose.yml --env-file /opt/dkr/stack/.env config --quiet`; it returned success, but warned that `CONFIG_ROOT`, `WATCHLIST_CLEANUP_ROOT`, `KIDS_MAIN`, and related template variables are unset in the live `.env`, substituting blank values. This proves syntax only. A restore requires a populated `.env` based on the repository example, actual path parity, the tracked helper script, and a test deployment. Keep the PR draft until those are verified.

### Tracked cleanup helper (November 27)

The deployed `/opt/dkr/watchlist-cleanup/watchlist-cleanup.py` was added to `stacks/stack/watchlist-cleanup.py`. A download of the branch file on `dkr` matched the live 2,530-byte file byte for byte with `cmp -s`; SHA-256 for both was `67a611b58e56399b2abb7252639f083daaeac21fa201d7c7aa54586e6b8e80f53`. The source contains no embedded credentials. It reads Plex and Seerr tokens from private mounted configuration at runtime. The new `stacks/stack/README.md` documents restore inputs and warns that the helper processes every Seerr user who has a Plex token. This tracks the source but does not yet prove a clean restore or remove the live template environment gap.
