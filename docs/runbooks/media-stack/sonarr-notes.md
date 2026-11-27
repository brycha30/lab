# Sonarr media workflow

Verified November 26, 2026. Sonarr runs in Docker VM 1033 (`dkr`, 192.168.1.33) on port 8989. The deployed Compose file is `/opt/dkr/stack/docker-compose.yml`. The container TV root `/Main/media/tv` maps to `/mnt/Main/media/tv` on the host. Sonarr configuration is under `/opt/dkr/config/sonarr`.

The download client and Sonarr mount the same TrueNAS filesystem. Let Sonarr import completed downloads and verify a hardlink by comparing device, inode, and link count. A move removes the download name and can stop seeding; a copy consumes additional space.

For duplicate episodes, compare series, season, episode, and multi-part identity with Sonarr's `EpisodeFiles` records. Six untracked single-episode copies beside tracked episodes were removed on November 26; the manifest is `/opt/dkr/config/tv-duplicate-cleanup-2026-11-26.json`. The Big C season 4 has separately tracked Part 1 and Part 2 files sharing episode labels; retain both. An older Shogun folder has overlapping untracked files that still need individual review.

If an import fails, inspect Sonarr Activity/Queue, qBittorrent category and completed path, permissions, and mount health before moving files manually. Do not bulk delete a folder because filenames repeat an episode number.
