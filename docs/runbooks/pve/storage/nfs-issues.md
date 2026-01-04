Runbook: Proxmox ↔ TrueNAS NFS Mount Issues (Main / media / torrents)

1. Environment Context

Hosts

Proxmox VE Host
- Hostname: pve2
- OS: Proxmox VE 8.x (Debian 12)
- Primary IP: 192.168.1.26

Docker LXC Container
- CT ID: 1031
- Hostname: docker
- IP: 192.168.1.31
- Privileged: unprivileged: 0

TrueNAS
- Hostname: truenas
- IP: 10.10.10.2
- ZFS Pool: main_pool

Storage Paths (TrueNAS)

- Dataset root:
/mnt/main_pool/Main

- Sub-datasets:
/mnt/main_pool/Main/media
/mnt/main_pool/Main/torrents

Storage Paths (Proxmox)

- /mnt/Main
- /mnt/Main/media
- /mnt/Main/torrents

Network

- NFS over TCP
- NFS version: 4.2
- Client address (Proxmox): 10.10.10.1
- No VLAN changes during this task

2. Problem Statement

After migrating from CIFS/SMB to NFSv4.2, containers lost write access to:
- /mnt/Main/media
- /mnt/Main/torrents

Symptoms observed:
- Permission denied when accessing subdirectories
- Too many levels of symbolic links
- Hung tasks and blocked processes
- Confusing autofs and duplicate mount behavior
- Media paths worked under CIFS but failed under NFS

3. Root Cause

1. Improper NFS mount topology
- Parent dataset (/mnt/main_pool/Main) mounted at /mnt/Main
- Sub-datasets (media, torrents) also mounted directly under /mnt/Main
- This created nested NFS mounts inside another NFS mount, which is unsafe

2. Systemd automount recursion
- x-systemd.automount on nested paths caused:
  - autofs loops
  - “too many levels of symbolic links” errors

3. TrueNAS dataset ownership mismatch
- media dataset owned by root:root
- CIFS masked ownership via uid/gid mount options
- NFS enforces server-side ownership strictly

4. Final Fix / Known-Good Configuration

Design Rules (Critical)

- NEVER mount an NFS dataset inside another NFS mount
- Mount sub-datasets outside, then bind-mount into tree
- Do NOT use x-systemd.automount for NFS datasets
- Ownership must be correct on TrueNAS

5. Final /etc/fstab Configuration (pve2)

Main dataset:
10.10.10.2:/mnt/main_pool/Main /mnt/Main nfs4 _netdev,nofail,noatime,nfsvers=4.2,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0

Sub-datasets mounted OUTSIDE the tree:
10.10.10.2:/mnt/main_pool/Main/media /mnt/_Main_media nfs4 _netdev,nofail,noatime,nfsvers=4.2,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0
10.10.10.2:/mnt/main_pool/Main/torrents /mnt/_Main_torrents nfs4 _netdev,nofail,noatime,nfsvers=4.2,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0

Bind mounts into Main:
 /mnt/_Main_media    /mnt/Main/media    none  bind  0  0
 /mnt/_Main_torrents /mnt/Main/torrents none  bind  0  0

6. Required TrueNAS Ownership Fix

Commands executed on TrueNAS:

chown -R 1000:1000 /mnt/main_pool/Main/media
chown -R 1000:1000 /mnt/main_pool/Main/torrents
chmod -R 2770 /mnt/main_pool/Main/media
chmod -R 2770 /mnt/main_pool/Main/torrents

UID/GID 1000:1000 matches container user.

7. Exact Cleanup and Apply Commands (pve2)

umount -lf /mnt/Main/media 2>/dev/null || true
umount -lf /mnt/Main/torrents 2>/dev/null || true
umount -lf /mnt/_Main_media 2>/dev/null || true
umount -lf /mnt/_Main_torrents 2>/dev/null || true
umount -lf /mnt/Main 2>/dev/null || true

rm -rf /mnt/_Main_media /mnt/_Main_torrents

mkdir -p /mnt/Main /mnt/Main/media /mnt/Main/torrents
mkdir -p /mnt/_Main_media /mnt/_Main_torrents

systemctl daemon-reload
mount -a

8. Verification Steps

Confirm mount topology:

findmnt -T /mnt/Main -o TARGET,SOURCE,FSTYPE
findmnt -T /mnt/Main/media -o TARGET,SOURCE,FSTYPE
findmnt -T /mnt/Main/torrents -o TARGET,SOURCE,FSTYPE

Expected results:
- /mnt/Main → NFS
- /mnt/Main/media → bind → _Main_media → NFS
- /mnt/Main/torrents → bind → _Main_torrents → NFS

Confirm no duplicate mounts:

nfsstat -m

Must NOT show:
- Duplicate mounts of the same dataset
- Nested /mnt/Main/media NFS mounts

Write tests:

touch /mnt/Main/.perm_test && rm /mnt/Main/.perm_test
touch /mnt/Main/media/.perm_test && rm /mnt/Main/media/.perm_test
touch /mnt/Main/torrents/.perm_test && rm /mnt/Main/torrents/.perm_test

All must succeed.

Container verification:

pct exec 1031 -- findmnt -T /mnt/Main/media
pct exec 1031 -- touch /mnt/Main/media/.ct_test && rm /mnt/Main/media/.ct_test

9. Warnings / Do-Not-Do-Again Notes

DO NOT mount NFS sub-datasets directly inside parent NFS mounts.

DO NOT use x-systemd.automount with NFS datasets.

DO NOT rely on CIFS-style uid/gid masking assumptions.

DO NOT mix CIFS and NFS mounts for the same paths.

ALWAYS fix ownership on TrueNAS datasets.

Keep NFS mounts flat; use bind mounts for hierarchy.

Verify every change using findmnt and nfsstat -m.

10. Status

- Host mounts: CLEAN
- Duplicate mounts: REMOVED
- Permissions: SERVER-ENFORCED and CORRECT
- Ready to proceed with Docker and media stack fixes
