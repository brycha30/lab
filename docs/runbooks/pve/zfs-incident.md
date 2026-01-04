Proxmox + Media Stack Incident Runbook

1. Environment Context

1.1 Host / Platform
- Hypervisor: Proxmox VE
- Hostname: pve2
- Hardware: Minisforum motherboard

Boot / VM Storage
- ZFS mirror: rpool
- Disks:
  - ata-TEAM_T253256GB_TPBF2212130080607072-part3 (256GB SATA SSD)
  - ata-TEAM_T2531TB_TPBG2212130010401358-part3 (1TB SATA SSD)

Swap
- zd0 (8G)

Block Devices (lsblk -d)
- sda 238.5G
- sdb 953.9G

1.2 Storage / Backups

Primary Backup Target
- TrueNAS via NFS

Proxmox Mount
- /mnt/pve/truenas-bu

Dump Directory
- /mnt/pve/truenas-bu/dump

TrueNAS Dataset
- main_pool/bu

ZFS Properties
- acltype = nfsv4
- aclmode = restricted
- aclinherit = passthrough

Local vzdump Temporary Directory
- /var/lib/vz/vzdump-tmp

1.3 Containers / Services

LXC 1031
- Hostname: docker
- Role: Media stack
- Bind mount excluded from backup:
  - mp0: /mnt/Main

Media Stack Paths (inside container rootfs)
- /root/docker-projects/docker-media-stack/
- Config directories under config/
  - Example: config/radarr-directors

LXC 1034
- Hostname: plex

Other LXC IDs Referenced
- 10006
- 1008

1.4 Networking / Application URLs

- https://radarr.md-chamberlain.com
- https://radarr-kids.md-chamberlain.com
- https://radarr-directors.md-chamberlain.com

Reverse Proxy
- Caddy with Cloudflare DNS-based TLS

2. Problem Statement

1. Web interfaces (Dashy, Radarr, etc.) became unresponsive during maintenance.
2. Proxmox backups (vzdump) hung or failed with:
   - Global lock waits
   - rsync: Operation not permitted
   - file has vanished
   - Permission errors writing to NFS
3. ZFS reported permanent checksum errors on VM disk files.
4. Required stabilization of backups, identification of storage root cause, and planning for hardware replacement.

3. Root Cause

3.1 Primary Root Cause

ZFS data corruption on rpool (SATA SSD mirror) affecting active VM disks.

zpool status -v rpool reported permanent errors in:
- /var/lib/vz/images/10006/vm-10006-disk-0.raw
- /mnt/ext/images/1034/vm-1034-disk-0.raw
- /mnt/ext/images/1008/vm-1008-disk-0.raw

Impact:
- Corruption caused backup instability
- Corruption propagated into running containers
- Media stack services hung during disk operations

3.2 Secondary Contributing Factors

- NFS ACL and permission mismatch prevented rsync from setting permissions and timestamps
- Live-changing files (e.g., Radarr Sentry envelopes) caused "file has vanished" errors during snapshot and suspend backups

4. Final Fix / Known-Good Configuration

4.1 NFS Permissions (TrueNAS)

- Map all users and groups to root
- Ensure dataset allows:
  - chmod
  - chown
  - timestamp updates

4.2 Proxmox vzdump Temporary Directory (Critical)

Create local tmpdir to avoid NFS ACL limitations:

mkdir -p /var/lib/vz/vzdump-tmp
chown root:root /var/lib/vz/vzdump-tmp
chmod 755 /var/lib/vz/vzdump-tmp

Configure /etc/vzdump.conf:

tmpdir: /var/lib/vz/vzdump-tmp

4.3 Cleanup Stuck Jobs and Locks

pkill -TERM -f "vzdump.*1031" || true
pkill -TERM -f "rsync.*vzdump-lxc-1031" || true
sleep 2
pkill -KILL -f "vzdump.*1031" || true
pkill -KILL -f "rsync.*vzdump-lxc-1031" || true
rm -f /run/vzdump.lock

Unlock containers if required:

pct unlock 1034

4.4 Backup Modes (Use Intentionally)

- For live media containers:
  - Use --mode stop (preferred)

- If snapshot fails:
  - Proxmox automatically falls back to suspend

Bind mount exclusion confirmed:

excluding bind mount point mp0 ('/mnt/Main')

4.5 Planned Storage Replacement

- Replace SATA SSD mirror with 2 identical M.2 NVMe drives (PCIe Gen4)
- Rebuild rpool as ZFS mirror on NVMe

Example compatible NVMe:
- WD_BLACK SN7100X NVMe (2TB)

5. Exact Commands Used

Run backup: LXC 1031 to NFS

vzdump 1031 --storage truenas-bu --mode snapshot --compress zstd

Run backup: LXC 1034 to local storage

vzdump 1034 --mode stop --compress zstd --storage local

Monitor progress

du -sh /var/lib/vz/vzdump-tmp/vzdumptmp*_1031
ps -ef | egrep 'vzdump|rsync|zstd'
pvesh get /nodes/pve2/tasks/<UPID>/log | tail -n 50

6. Verification Steps

NFS Write Tests

touch /mnt/pve/truenas-bu/dump/.pve-write-test
touch -t 202401010101.01 /mnt/pve/truenas-bu/dump/.pve-write-test
chmod 755 /mnt/pve/truenas-bu/dump

Confirm tmpdir growth

du -sh /var/lib/vz/vzdump-tmp/vzdumptmp*

Confirm archive creation

ls -lh /mnt/pve/truenas-bu/dump | grep vzdump-lxc-1031
ls -lh /var/lib/vz/dump | grep vzdump-lxc-1034

Check ZFS health

zpool status -v rpool

7. Warnings / Do-Not-Do-Again Notes

- Do NOT rely on NFS for vzdump temporary files
- Do NOT snapshot live, highly active containers (Radarr, Sonarr, Deluge)
- Do NOT ignore ZFS checksum errors
- Do NOT mix SSD sizes or models in ZFS mirrors long-term

Important:
- Backups will include corruption if source disks are corrupted

8. Notes for Next Actions

- Rebuild rpool on NVMe mirror
- Restore or rebuild affected containers:
  - 10006
  - 1034
  - 1008
- Standardize backup policy:
  - stop mode for media
  - snapshot mode for static services
- Document NVMe slot layout on Minisforum motherboard before installation
