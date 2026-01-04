# MD-Chamberlain Homelab — Master Runbook (Authoritative)

## Conversation Metadata
- First discussed: UNKNOWN
- Last updated: 2025-12-31
- Scope: Proxmox, TrueNAS, OPNsense, Docker media stack, IPTV, Dashy, Omada, switching

## Repo Map (Source of Truth)

This section defines where authoritative information lives.  
`master.md` describes *what* is true. These files define *how* it is implemented.

### Core
- Master runbook: `master.md`
- Service access map (IPs, URLs, ports): `summaries/access-map.md`

### Proxmox (pve)
- Backup (NFS, unprivileged LXC, WebUI fixes): `pve/backup-nfs.md`
- Backups known-good baseline: `pve/backups/known-good.md`
- Storage layout + mounts: `pve/storage/layout.md`
- TrueNAS NFS issues + remediation: `pve/storage/nfs-issues.md`
- Network remediation (VLAN 99 cleanup): `pve/troubleshooting/vlan99.md`
- Plex buffering remediation: `pve/troubleshooting/plex-buffer.md`
- ZFS incident (historical): `pve/zfs-incident.md`
- Container inventory: `pve/ct-inventory.md`
- 10G migration (RJ45 → SFP+): `pve/network/10g-sfp.md`

### Firewall (fw)
- OPNsense upgrade failure recovery: `fw/upgrade-recovery.md`

### Docker Projects (dkr/projects)
- Media stack: `dkr/projects/media/`
- Gateway (Dashy entrypoint): `dkr/projects/gw/`
- Cloudflare DDNS + Caddy: `dkr/projects/cfddns/`
- LXC Docker setup notes: `dkr/projects/lxc-setup/`

### UI (Dashy)
- Dashy config: `ui/dashy.yml`
- Dashy CSS: `ui/custom.css`
- LAN dashboard notes: `ui/lan-ui.md`
- UI behavior notes: `ui/ui-notes.md`

### Decisions
- Proxmox hardware decisions: `decisions/hw/pve-hw.md`

---

## 1. Environment Overview (Authoritative)

### Core Hosts
- **Proxmox VE Host:** pve2  
  - IP: 192.168.1.26  
  - OS: Proxmox VE 8.x (Debian 12)
  - Storage (current): ZFS mirror (SATA SSDs)
  - Planned replacement: NVMe ZFS mirror

- **TrueNAS**
  - IP: 192.168.1.50 (LAN)
  - Backend subnet (historical): 10.10.10.2
  - Pools:
    - main_pool (media, torrents, backups)
    - bu (Proxmox backups)

- **Firewall**
  - Platform: OPNsense
  - LAN: igc0 — 192.168.1.1/24
  - WAN: igc1 (DHCP)
  - TESTLAN (historical): igc2 — 192.168.99.0/24 (VLAN 99, removed)

---

## 2. Network Architecture (Current State)

### Switching
- **Core / Aggregation:** TP-Link TL-SX3008F (10G SFP+)
- **Access / PoE:** TP-Link TL-SG3210XHP-M2 (2.5G PoE++)
- **Edge:** TL-SG1024 (unmanaged, non-critical)

### NIC Strategy
- **All 10G links:** Intel X520-DA2 (SFP+)
- **Cabling:** Passive DAC (10GBase-CU)
- **RJ45 10GBase-T:** Fully removed

### VLANs
- VLAN 1: Production LAN
- VLAN 99: ❌ Removed (test-only, caused instability)

---

## 3. Proxmox Architecture

### Storage Layout
- `/rpool` — ZFS mirror (boot + VM/LXC disks)
- `/mnt/pve/nas-nfs-backup` — NFS backup target
- `/mnt/Main` — Media (NFS, bind-mounted into containers)

### Containers (Key)
- 1031 — Docker media stack
- 1034 — Plex
- Others documented in `pve/ct-inventory.md`

---

## 4. Backup Strategy (Known-Good)

### Backup Tool
- vzdump + NFS
- Compression: zstd
- Mode: **STOP** (mandatory)

### Critical Rules
- tmpdir MUST be local:
  - `/var/lib/vz/vzdump-tmp`
  - Owned by UID/GID 100000 (unprivileged LXC)
- Never use suspend mode for LXC on NFS
- Always exclude `/var/log/journal`

### Reference
See:
- `pve/backups/known-good.md`
- `pve/backup-nfs.md`

---

## 5. TrueNAS + NFS Rules

### Absolute Rules
- Never nest NFS mounts
- Never mix CIFS and NFS on same paths
- Always fix dataset ownership server-side
- Use bind mounts for hierarchy

### Reference
See:
- `pve/storage/nfs-issues.md`

---

## 6. Media Stack Architecture

### Core Components
- Docker (LXC 1031)
- Deluge
- Sonarr / Radarr (+ Kids / Directors variants)
- Bazarr
- Prowlarr
- FlareSolverr
- VPN container (Gluetun / PIA)

### Storage Rules
- Media: NFS
- Configs: **Local disk only**
- SQLite configs NEVER on NAS

### CIFS Lessons
- CIFS caused kernel hangs, Deluge blocking, Sonarr stalls
- NFS preferred; local disk for torrents if instability returns

### Reference
See:
- `dkr/media-stack/first-response.md`
- `dkr/media-stack/cifs-hangs.md`
- `dkr/media-stack/vpn-config-recovery.md`

---

## 7. Plex Stability Rules

### Known Failure Causes
- Undersized rootfs
- Unbounded transcode cache
- Network path asymmetry (10G backend misuse)

### Fixes
- Expand LXC disk
- Auto-clean transcode cache
- Simplify network paths

### Reference
See:
- `pve/troubleshooting/plex-buffering-network-remediation.md`

---

## 8. Dashy + Internal Access

### Rules
- Use absolute HTTPS URLs for icons
- No relative icon paths
- Unbound DNS overrides REQUIRED
- Dashy schema is strict

### Reference
See:
- `ui/ui-notes.md`
- `ui/lan-ui.md`

---

## 9. IPTV Architecture (Final Decision)

### Clients
- Fire TV Cube (primary)
- TiviMate (preferred client)

### Reference
See:
- `summaries/iptv-media-client-architecture.md`
- `summaries/iptv-setup-fire-tv-cube-tivimate.md`

---

## 10. Rules of the Road (DO / DO NOT)

### DO
- Keep configs local
- Use STOP mode for backups
- Validate mounts with `findmnt`
- Label DAC cables
- Document changes immediately

### DO NOT
- Use SQLite on NAS
- Leave test VLANs in production
- Use suspend backups on NFS
- Ignore ZFS checksum errors
- Hot-swap NICs

---

## 11. Incident History (Reference Only)

Incidents are documented separately and are NOT baseline.

See:
- `pve/zfs-incident.md`
- `pve/troubleshooting/vlan99.md`
- `fw/upgrade-recovery.md`

---

## Status
✅ Stable  
✅ Documented  
✅ Recoverable  
✅ Ready for future expansion

This file is the authoritative reference for this homelab.
