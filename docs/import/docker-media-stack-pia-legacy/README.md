# Docker Media Stack

This is a self-hosted media automation stack running behind a Private Internet Access (PIA) VPN. It includes torrenting, subtitle fetching, and browser automation tools.

---

## 📦 Included Services

| Service           | Description                                | Port     |
|-------------------|--------------------------------------------|----------|
| Deluge            | Torrent client with VPN                    | 8112     |
| Sonarr            | TV episode automation                      | 8989     |
| Radarr            | Movie automation                           | 7878     |
| Jackett           | Indexer proxy for Sonarr/Radarr            | 9117     |
| Bazarr            | Subtitle downloader                        | *in-app* |
| FlareSolverr      | Captcha resolver used by Jackett           | 8191     |
| Firefox (jlesage) | Browser container for VPN leak testing     | 5800     |

---

## 🚀 Setup Instructions

1. Copy the example env:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your PIA credentials, paths, and timezone:
   ```ini
   USER=piauser
   PASS=piapassword
   ROOT=/root/docker-projects/docker-media-stack
   MAIN=/mnt/nfs/Main
   TZ=America/New_York
   ```

3. Start the stack:
   ```bash
   docker compose up -d
   ```

4. Access services from your Docker host IP:
   - Deluge: `http://<host>:8112`
   - Sonarr: `http://<host>:8989`
   - Radarr: `http://<host>:7878`
   - Jackett: `http://<host>:9117`
   - Firefox (VPN test): `http://<host>:5800`

---

## 🔐 Security Notes

- All traffic is routed through the VPN container.
- Do not expose this stack to the internet without reverse proxy and authentication.
- Always test VPN leaks using the Firefox container or external tools.

---

## 📟 Environment Variables

Bind mounts are used for persistent data:
- `${ROOT}/config/...` for application configs
- `${MAIN}` for shared media directories

There are **no Docker-managed volumes** in this stack.

---

## ✅ Tips

- Use `docker compose logs -f <service>` to debug.
- VPN healthcheck built-in to the stack.
- Restart stack safely:
  ```bash
  docker compose down && docker compose up -d
  ```

