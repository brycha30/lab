# Proxmox Storage Layout

## Proxmox Host
- Hostname: pve2

## Local Storage
- ZFS rpool
- Purpose:
  - Proxmox OS
  - Local VM/LXC disks
  - vzdump temporary directory

## vzdump Temporary Directory
- Path: /var/lib/vz/vzdump-tmp
- Location: local ZFS storage (NOT NFS)
- Reason:
  - Avoid NFS performance issues
  - Prevent ACL/xattr failures
  - Required for fast, reliable backups

## Network Storage (TrueNAS)

### NFS Backup Target
- Proxmox mount: /mnt/pve/nas-nfs-backup
- TrueNAS dataset: /mnt/main_pool/bu/proxmox
- Purpose:
  - Store completed Proxmox backups (.tar.zst)
- Notes:
  - Used only for final backup output
  - Not used for tmpdir or live container data

## Design Rules
- Never place vzdump tmpdir on NFS
- Prefer stop-mode backups for NFS targets
- Keep Proxmox host lean; services live in LXCs
- Treat TrueNAS as backup + bulk storage only

## Known Failure Mode
- Symptom:
  - Backups extremely slow or hang
- Cause:
  - tmpdir on NFS or rsync-based backup mode
- Fix:
  - Move tmpdir to local ZFS
  - Use stop mode with tar + zstd
