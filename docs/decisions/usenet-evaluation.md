# Optional Usenet path for the media stack

Status: evaluation only, November 26, 2026. Do not change the working qBittorrent workflow or start a paid subscription merely to add another client.

## Why evaluate it

SABnzbd can provide an independent download path when a torrent lacks seeds. Prowlarr supports both torrent and Usenet indexers, while Radarr/Sonarr support SABnzbd as a download client. Usenet typically requires a provider and a separate indexer account, which adds recurring cost and failure points. SSL connections are available, and the torrent VPN policy does not need to be copied blindly to SABnzbd.

## Proposed layout

- Keep qBittorrent under Gluetun for torrents.
- Add SABnzbd as a separate service with its own config volume and a completed Usenet directory on the same `/mnt/Main` filesystem as `/mnt/Main/media`.
- Give SABnzbd, Radarr, and Sonarr a consistent view of that mount; keep Usenet and torrent completed folders separate.
- Configure category mapping for movies, kids movies, directors, and TV. Test one item per category before enabling automatic grabs.
- Add a Usenet indexer in Prowlarr and sync it to the appropriate apps. Add SABnzbd as a download client in each relevant app, with explicit categories.
- Test import, cleanup, failure handling, and free space. Usenet completion normally moves the file rather than retaining a seeding hardlink. Do not assume a hardlink just because torrent imports use one.

## Decision gate

Choose a reputable provider and indexer only after comparing current pricing, retention, connection limits, completion, and cancellation terms. Account signup and payment require the owner's selection and credentials. No provider, indexer, or subscription has been selected yet. Measure whether current failed or slow requests justify this extra expense before making it the preferred source.

References: [Servarr Docker Guide](https://wiki.servarr.com/docker-guide), [Prowlarr](https://wiki.servarr.com/prowlarr), [SABnzbd configuration](https://sabnzbd.org/wiki/configuration/).
