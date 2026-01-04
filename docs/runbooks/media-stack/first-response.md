# Docker Media Stack — First Response Playbook

## Applies To
- Proxmox host: pve2
- Docker LXC: 1031 (hostname: docker)
- Plex LXC: 1034
- Storage: TrueNAS via NFS (/mnt/Main)

## Goal
Quickly determine whether an outage is caused by:
- Docker
- The container itself
- Storage (most common cause)

---

## Step 1 — Check container status (on Proxmox)
Command:
pct status 1031
pct status 1034

If containers are running but services are unreachable, continue.

---

## Step 2 — Enter the Docker container
Command:
pct enter 1031

---

## Step 3 — Check for stuck I/O (MOST COMMON CAUSE)
Command:
ps -eo state,pid,comm,wchan:32 --sort=state | awk '$1 ~ /D/ {print}' | head -n 40

If processes are in state "D":
- DO NOT restart Docker yet

Check kernel logs:
dmesg -T | egrep -i "blocked for more than|cifs|smb|nfs|i/o error|reset|ext4|zfs" | tail -n 60

---

## Step 4 — Verify mounts are healthy
Command:
findmnt -rno TARGET,SOURCE,FSTYPE,OPTIONS | egrep -i "nfs|cifs|smb|mnt/Main"
df -hT | egrep -i "mnt|nfs|cifs|smb"

Test responsiveness (these should return instantly):
ls -lah /mnt/Main | head
time ls -lah /mnt/Main/docker-projects >/dev/null

If these hang → STORAGE OR NETWORK ISSUE.

---

## Step 5 — Check Docker health
Command:
systemctl is-active docker
docker ps
docker info | head

---

## Step 6 — Restart Docker (only if storage is healthy)
Command:
systemctl restart docker

For a specific stack:
cd /mnt/Main/docker-projects/<stack>
docker compose down
docker compose up -d

---

## Step 7 — If the container itself is unresponsive
From Proxmox host:
pct exec 1031 -- uptime
pct exec 1031 -- free -h
pct exec 1031 -- df -hT

If pct exec hangs → kernel I/O wait → storage/network problem.

---

## Step 8 — LAST RESORT (storage confirmed broken)
Command:
umount -lf /mnt/Main
mount -a

---

## When Asking for Help
Provide:
1. pct status for 1031 and 1034
2. Output showing D-state processes
3. dmesg storage-related errors
4. Whether ls /mnt/Main returns instantly or hangs
