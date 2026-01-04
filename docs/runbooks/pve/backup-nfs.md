Proxmox Backup Runbook – NFS Storage, Unprivileged LXC, WebUI + CLI

1. Environment Context

1.1 Hosts

Proxmox Node:
- Hostname: pve2

NAS:
- TrueNAS

Backup Storage Type:
- NFSv4

1.2 Network

Proxmox ↔ NAS network:
- 10.10.10.0/24

NAS IP:
- 10.10.10.2

1.3 Storage

TrueNAS Dataset:
/mnt/main_pool/bu/proxmox

Mounted on Proxmox as:
/mnt/pve/nas-nfs-backup

Backup directory:
/mnt/pve/nas-nfs-backup/dump

1.4 Proxmox Backup Artifacts

Temporary directory:
/var/lib/vz/vzdump-tmp

Backup tool:
- vzdump

Compression:
- zstd

Containers involved:
- LXC: 1012, 1013, 1031, 1034, 1199, 1251, 1252
- QEMU VM: 1015

2. Problem Statement

Proxmox WebUI backups were extremely slow, appeared hung, or failed.

Observed errors:
- rsync: set_acl: Operation not supported (95)
- Permission denied during tar phase

Observed behavior:
- CLI backups completed much faster than WebUI backups
- Unprivileged LXC containers + NFS storage caused ACL and xattr issues
- WebUI backup jobs ignored CLI optimizations

3. Root Cause

3.1 Primary Causes

- Unprivileged LXC containers require backup temp files to be writable by UID/GID 100000
- Default vzdump temporary directory permissions were incompatible
- WebUI default backup mode was suspend, which:
  - Uses rsync-style syncing
  - Triggers ACL and xattr operations unsupported by NFS
  - Is slower and more failure-prone
- /var/log/journal inside containers caused excessive ACL/xattr errors and slowdown

4. Final Fix / Known-Good Configuration

4.1 Fix vzdump Temporary Directory Permissions (CRITICAL)

pkill -f "/usr/bin/vzdump" || true
rm -rf /var/lib/vz/vzdump-tmp/vzdumptmp*

chown 100000:100000 /var/lib/vz/vzdump-tmp
chmod 700 /var/lib/vz/vzdump-tmp

Verify permissions:
ls -ldn /var/lib/vz/vzdump-tmp

Expected:
drwx------ 2 100000 100000 ... /var/lib/vz/vzdump-tmp

4.2 Global vzdump Configuration

File:
/etc/vzdump.conf

Configuration:

compress: zstd
mode: stop
ionice: 7
tmpdir: /var/lib/vz/vzdump-tmp
exclude-path: /var/log/journal
rsyncopts: --no-acls --no-xattrs

Notes:
- mode: stop is the primary performance and reliability fix
- rsyncopts is ignored for LXC tar backups but safe to keep
- Excluding /var/log/journal prevents ACL and xattr failures

4.3 CLI Backup (Known-Fast, Known-Good)

Example:

vzdump 1012 \
  --storage nas-nfs-backup \
  --mode stop \
  --compress zstd \
  --ionice 7 \
  --exclude-path /var/log/journal

Typical performance:
- 4–20 GiB containers complete in seconds to a few minutes
- Throughput approximately 130–170 MiB/s

4.4 Batch Backup Loop (Used Successfully)

for id in 1013 1031 1034 1199 1251 1252; do
  echo "===== BACKING UP $id ====="
  vzdump $id \
    --storage nas-nfs-backup \
    --mode stop \
    --compress zstd \
    --ionice 7 \
    --exclude-path /var/log/journal || break
done

4.5 Proxmox WebUI Backup Job (Working)

Location:
Datacenter → Backup

Schedule:
- Sunday at 01:00

Retention:
- Keep last 4 backups

Settings:
- Mode: STOP
- Compression: zstd
- Storage: nas-nfs-backup

Verified:
- Fast and reliable
- Produces .tar.zst (LXC) and .vma.zst (QEMU) files

5. Verification Steps

Check running backup tasks:
tail -n 50 /var/log/pve/tasks/active | grep vzdump

Inspect task log:
cat /var/log/pve/tasks/*/UPID:pve2:*:vzdump:* | tail -n 80

Watch temporary directory growth:
ls -lh /var/lib/vz/vzdump-tmp

Watch backup output:
ls -lh /mnt/pve/nas-nfs-backup/dump | tail -n 30

Expected files:
- vzdump-lxc-<id>-<date>.tar.zst
- vzdump-qemu-<id>-<date>.vma.zst
- .log and .notes files

6. Warnings / Do-Not-Do-Again Notes

- Do NOT use mode: suspend for LXC backups on NFS
  - Causes rsync ACL/xattr failures
  - Much slower
  - Appears hung in WebUI

- Do NOT change /var/lib/vz/vzdump-tmp ownership back to root
  - Unprivileged LXC backups will fail

- Do NOT include /var/log/journal
  - Generates ACL/xattr errors
  - Causes massive slowdown

- Do NOT troubleshoot backup speed before checking backup mode
  - 90% of the issue was suspend vs stop

7. Known-Good State Summary

- Backups complete quickly
- WebUI and CLI behave consistently
- NFS storage works reliably
- Unprivileged LXC fully supported
- Retention policy active
- Restore-ready artifacts verified

Status:
STABLE

Last verified:
2025-12-31

Node:
pve2
