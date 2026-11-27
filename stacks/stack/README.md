# Media stack Compose draft

This directory records the main media Compose project deployed on `dkr` at `/opt/dkr/stack`. The file is a sanitized template. The live `.env`, application databases, Plex/Seerr tokens, and WireGuard key remain on the host.

## Restore inputs

1. Copy `../../.env.example` to a private `.env` beside the Compose file and fill in the actual PUID, PGID, VPN values, NAS paths, and Gluetun LAN/firewall values. Keep `.env` out of Git.
2. Confirm the NAS mounts exist before starting containers: `/mnt/Main` and `/mnt/KidsMain`. The download and library paths must resolve to the intended shared filesystem for hardlinks.
3. Install the tracked helper source at `/opt/dkr/watchlist-cleanup/watchlist-cleanup.py`, or change `WATCHLIST_CLEANUP_ROOT` to its actual directory. Its writable state directory is `/opt/dkr/watchlist-cleanup/state`.
4. Restore the private application config directories under `CONFIG_ROOT` from backup. The helper reads the Plex server URL and token from the local Kometa config and user Plex tokens from the read-only Seerr database mount. Never commit either file.
5. Run `docker compose --env-file .env config --quiet` from the intended deployment directory. Inspect `docker compose config --services`, resolved mounts, and ports before `up`. A syntax pass with missing variables is insufficient; Compose may substitute blank paths.

The helper source in this branch was compared with the deployed 2,530-byte file on November 27, 2026 using `cmp -s` and matching SHA-256 digests. The live main project and this template each list 13 services. The template's syntax passed on `dkr`, but the live `.env` does not provide all template path variables. Do not replace the running Compose file until a populated restore configuration has been compared and tested.

## Watchlist helper behavior

The helper checks movie watchlists every five minutes for every Seerr user with a stored Plex token. It removes a movie from that user's Plex Watchlist when the same Plex server has a matching library item backed by an accessible media file. It does not delete media or Radarr entries. `--dry-run --once` performs one pass without removal; `--once` performs one normal pass. The status JSON under `/state` and logs contain user names and movie titles; keep them private. There is currently no per-user allowlist and no TV watchlist handling.

The helper runs read-only with only `/state` and `/tmp` writable. Maintainerr's separate `Delete Requests` collection handles deletion after its one-day timer. Do not conflate removing a Plex Watchlist item with deleting a library file.
