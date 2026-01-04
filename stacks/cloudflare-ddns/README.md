# Cloudflare DDNS + Caddy Config

This Docker stack sets up:

- **Caddy** as a reverse proxy with HTTPS support
- Automatic certificate management using Cloudflare DNS challenge
- Optional dynamic DNS via Cloudflare's API

---

## 📦 Services

| Service       | Description                              |
|---------------|------------------------------------------|
| **Caddy**     | Reverse proxy with HTTPS via Cloudflare DNS |

---

## 🚀 Usage

1. Copy the `.env.example` to `.env` and fill in your Cloudflare credentials:

```bash
cp .env.example .env
