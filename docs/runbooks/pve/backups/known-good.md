# Proxmox Backups — Known-Good Configuration (vzdump + NFS)

## Environment
- Proxmox host: pve2
- Workloads: unprivileged LXC containers
- Backup target: TrueNAS via NFS
- NFS mount on Proxmox: /mnt/pve/nas-nfs-backup
- TrueNAS dataset: /mnt/main_pool/bu/proxmox

## Problems Encountered
1. Very slow backups when tmpdir was on NFS
2. rsync ACL/xattr failures involving /var/log/journal
3. Permission errors for unprivileged containers (uid 100000)
4. WebUI backups behaving differently than CLI
5. Hung vzdump processes

## Root Cause
- vzdump tmp directory on NFS caused slow performance and ACL issues
- systemd journal files do not support ACLs well on NFS
- tmpdir permissions incorrect for uid 100000
- suspend mode uses rsync, which is slow on NFS
- stop mode uses tar, which is fast and reliable

## Final Fix (Known-Good)

1) Create LOCAL tmpdir on Proxmox (ZFS or local storage)

Command:
mkdir -p /var/lib/vz/vzdump-tmp
chown 100000:100000 /var/lib/vz/vzdump-tmp
chmod 700 /var/lib/vz/vzdump-tmp

2) Configure /etc/vzdump.conf

File contents:
compress: zstd
mode: stop
ionice: 7
tmpdir: /var/lib/vz/vzdump-tmp
exclude-path: /var/log/journal

Notes / Warnings
- Do NOT rely on rsyncopts (ignored by vzdump)
- stop mode avoids rsync entirely
- exclude-path prevents journal ACL errors

## Storage Verification

Command:
df -hT /mnt/pve/nas-nfs-backup
ls -lh /mnt/pve/nas-nfs-backup/dump

## Manual Test (CLI)

Command:
vzdump 1012 --storage nas-nfs-backup --mode stop --compress zstd --ionice 7 --exclude-path /var/log/journal

Expected Result
- Local tmpdir fills quickly
- Final .tar.zst written to NFS
- Backup completes in seconds to minutes

## Monitoring a Running Backup

Command:
tail -n 50 /var/log/pve/tasks/active
ps -ef | egrep 'vzdump|tar|zstd|lxc-usernsexec'

## Emergency Cleanup (Hung Jobs)

Command:
pkill -f "/usr/bin/vzdump"
rm -rf /var/lib/vz/vzdump-tmp/vzdumptmp*

## Success Criteria
- Backup speeds greater than 100MB/s
- No rsync ACL errors
- .tar.zst files created cleanly
- WebUI and CLI behave the same

WARNING
This configuration is known-good.
Do not change tmpdir or mode without a reason.
