# lab

Consolidated homelab repo (sanitized): Docker Compose stacks and config.

## Repo layout
- `stacks/gw`     - Caddy + Dashy gateway stack
- `stacks/omada`  - Omada Controller stack
- `stacks/stack`  - Media/VPN stack (compose)

## Secrets / env files
This repo does **not** store real secrets.

### Recommended pattern
1. Copy `.env.example` to `.env` (local only, not committed)
2. Symlink that `.env` into each stack folder (or use `--env-file`)

### Example (central env + symlinks)
```bash
cp .env.example .env
ln -sf /opt/lab/.env /opt/lab/stacks/gw/.env
ln -sf /opt/lab/.env /opt/lab/stacks/omada/.env
ln -sf /opt/lab/.env /opt/lab/stacks/stack/.env
Bring a stack up
bash
Copy code
cd stacks/gw
docker compose up -d
Alternative (no symlinks)
bash
Copy code
cd stacks/gw
docker compose --env-file /opt/lab/.env up -d
Notes
Current production runtime may still be under /opt/dkr. This repo is the sanitized source of truth.

Do not commit real .env files or credentials.
```
