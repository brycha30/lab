# Service Access Map (MD-Chamberlain)

## Core Infrastructure
- Proxmox host (pve2): 192.168.1.26
- OPNsense: 192.168.1.1
- TrueNAS: 192.168.1.10 (NAS services / NFS targets)

## Key Containers
- Docker LXC (1031): 192.168.1.31
- Plex LXC (1034): 192.168.1.34
- PBX LXC (1008): (IP to confirm)

## Reverse Proxy / Friendly Domains
- Dashy: https://lan.md-chamberlain.com
- Plex: https://plex.md-chamberlain.com  (backend: 192.168.1.34:32400)
- OPNsense: https://opnsense.md-chamberlain.com
- Proxmox: https://pve2.md-chamberlain.com
- Invoice Ninja: https://invoice.md-chamberlain.com
- AdGuard: http://adguard.md-chamberlain.com
- Firefox Docker: https://firefox.md-chamberlain.com

## Media Stack (Docker LXC 1031)
- Sonarr: https://sonarr.md-chamberlain.com (typical port: 8989)
- Radarr: https://radarr.md-chamberlain.com (typical port: 7878)
- Radarr-Kids: https://radarr-kids.md-chamberlain.com
- Radarr-Directors: https://radarr-directors.md-chamberlain.com
- Bazarr: https://bazarr.md-chamberlain.com
- Bazarr-Kids: https://bazarr-kids.md-chamberlain.com
- Deluge: https://deluge.md-chamberlain.com
- Jackett: https://jackett.md-chamberlain.com
- FlareSolverr: https://flaresolverr.md-chamberlain.com
- Frigate: https://frigate.md-chamberlain.com

## Notes
- Domain access is via Caddy reverse proxy + Cloudflare DNS-based TLS
- Internal services should be LAN-only where intended
- Do not store secrets in GitHub; document secret locations only
