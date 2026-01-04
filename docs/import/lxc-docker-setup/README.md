# LXC Docker Bootstrap Setup Guide

This guide walks through setting up a robust Docker LXC container environment on Proxmox, with GitHub integration and a media stack including VPN, Caddy, Dashy, and more.

---

## LXC Creation Parameters

- **Type:** Unprivileged
- **Base OS:** Debian 12
- **Hostname:** docker
- **IP Address:** `192.168.1.31`
- **Resources:**
  - Disk: 100GB
  - CPU: 2 cores
  - RAM: 4096MB
  - Swap: 4096MB
- **Special Features:**
  - Nesting: enabled
  - FUSE: enabled
  - UID/GID Mapping: included below

Created via [Proxmox Community Helper Scripts](https://community-scripts.github.io/ProxmoxVE/scripts?id=docker).

---

## GitHub SSH Setup

### 1. Generate SSH Key:

```bash
ssh-keygen -t ed25519 -C "brycha30@github"
```

Press enter through the prompts.

### 2. Copy Public Key:

```bash
cat ~/.ssh/id_ed25519.pub
```

### 3. Add Key to GitHub:

- Go to: [https://github.com/settings/keys](https://github.com/settings/keys)
- New SSH key → Title: `docker-lxc`
- Paste the key → Save

### 4. Verify Connection:

```bash
ssh -T git@github.com
```

Expected output:

```
Hi brycha30! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## GitHub Repo Cloning

```bash
mkdir -p ~/docker-projects && cd ~/docker-projects

git clone git@github.com:brycha30/docker-media-stack.git
git clone git@github.com:brycha30/cloudflare-ddns.git
git clone git@github.com:brycha30/lxc-docker-setup.git
```

➡️  **Default branch for all repos is now `main`.**

If any repo is still using `master`, update with:

```bash
git branch -m master main
git push -u origin main
```

Then update GitHub default branch in repo settings → Branches.

---

## Media Stack Deployment

### `.env` File Example:

```env
TZ=America/New_York
PUID=1000
PGID=1000
ROOT=/root/docker-projects/docker-media-stack
MAIN=/mnt/nfs/Main
USER=p5505972
PASS="R4!NxPHh*xG28i^e#5zsvBn#"
```

### `.gitignore` Example:

```gitignore
.env
*.log
config/**/logs/
config/**/MediaCover/
config/**/Images/
config/**/*.db
pia-credentials
*.zip
```

### Launch Stack:

```bash
cd ~/docker-projects/docker-media-stack
docker compose up -d
```

✅ `kasm-firefox` is removed. Using `jlesage/firefox` on port 5800.

Services Included:
- `vpn` – PIA WireGuard container (exposes ports: 8112, 8989, 9117, 7878, 6881, 58846, 8191, 6901, **5800**)
- `deluge` – Torrent client
- `sonarr`, `radarr`, `jackett`, `bazarr` – Media managers
- `flaresolverr` – Used by Jackett if needed
- `firefox` – Lightweight container browser for VPN testing

---

## Mounting NFS Share to LXC

### 1. Edit the LXC container config from Proxmox host:

```bash
nano /etc/pve/lxc/1031.conf
```

### 2. Add this line to mount the share with correct permissions:

```bash
mp0: /mnt/pve/nfs-share,mp=/mnt/nfs,backup=0,uid=1000,gid=1000
```

### 3. Add the following lines for UID/GID mapping and required features:

```ini
lxc.idmap: u 0 100000 1000
lxc.idmap: g 0 100000 1000
lxc.idmap: u 1000 1000 1
lxc.idmap: g 1000 1000 1
lxc.idmap: u 1001 101000 64535
lxc.idmap: g 1001 101000 64535
features: fuse=1
swap: 4096
```

### 4. Restart the container:

```bash
pct restart 1031
```

You should now see the mounted folder in:

```bash
ls /mnt/nfs
```

Ensure it’s accessible by user `bryan` with UID/GID `1000`.

---

## Optional Tools to Install Inside LXC

```bash
apt update && apt install -y htop curl git unzip iputils-ping nano net-tools
```

---

## Cloudflare DDNS + Caddy Integration

Clone Caddy & DDNS config:

```bash
cd ~/docker-projects && git clone git@github.com:brycha30/cloudflare-ddns.git
```

Edit `.env` to include your Cloudflare token and domain:

```env
CF_API_TOKEN=your_cloudflare_token
CF_DOMAIN=md-chamberlain.com
```

Edit Caddyfile to point to the correct internal services, using reverse proxy rules and TLS via DNS.

---

## Maintenance Tips

- Backup `~/docker-projects` regularly
- Push `.env`-safe changes to GitHub
- Avoid committing secrets or credentials
- Keep this README and repo synced

---

**This guide is designed to make full system rebuilds easy, fast, and reproducible.**

