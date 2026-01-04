# Proxmox Container Inventory

## Proxmox Host
- Hostname: pve2

## Containers

### Docker LXC
- Container ID: 1031
- Hostname: docker
- IP Address: 192.168.1.31
- Type: Unprivileged LXC
- Purpose:
  - Docker engine
  - Media stack (Sonarr, Radarr, Deluge, Bazarr, etc.)
  - Dashy
- Notes:
  - Git runbook repo lives locally in this container
  - Persistent data stored on TrueNAS mounts

### Plex LXC
- Container ID: 1034
- Hostname: plex
- IP Address: 192.168.1.34
- Type: Unprivileged LXC
- Purpose:
  - Plex Media Server
- Ports:
  - 32400 (TCP)

### PBX LXC
- Container ID: 1008
- Hostname: pbx
- Purpose:
  - Incredible PBX
- Notes:
  - SIP and VoIP services

### Other Containers
- Vaultwarden
- Cloudflare Tunnel
- Invoice Ninja
- Additional service containers as deployed

## Design Notes
- Containers are unprivileged unless required
- Docker runs inside a dedicated LXC
- Network services use static IPs
- Reverse proxy and DNS used for service access

## Operational Rules
- Do not run application services directly on Proxmox host
- Keep container roles clearly separated
- Document new containers immediately
