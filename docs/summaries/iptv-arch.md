# IPTV / Media Client Architecture – Runbook Summary

## 1. Environment Context

### Network / Hosts
- **LAN subnet:** 192.168.1.0/24
- **Gateway / Firewall:** 192.168.1.1 (OPNsense)
- **DNS:** Unbound on OPNsense
- **VPN:** WireGuard (selective, per-device)

### Relevant Systems
- **pve2 (Proxmox host):** 192.168.1.26  
- **TrueNAS:**  
  - IPs: 192.168.1.50 (1GbE), 192.168.1.51 (10GbE)  
  - Pools:
    - `/mnt/main_pool/Main`
    - `/mnt/main_pool/frigate`
    - `/mnt/main_pool/bu`
    - `/mnt/zfs_mirror/sdb`
- **Docker media container:** 192.168.1.31
- **Plex:** 192.168.1.34:32400
- **OPNsense VPN box (alt hardware):** Intel i3-N305, 4× Intel I226-V 2.5GbE

### Client / Playback Devices
- **Nvidia Shield TV Pro** (primary recommendation)
- **Mini PC options evaluated:**
  - Intel i3-N305
  - Intel N100 / N95 / N150
- **Remote types:** 2.4 GHz USB air mouse (G10S / G20S / MX3 Pro)

### Storage Paths Used for Media / DVR
- NAS mount via SMB (Shield):
  - `smb://<NAS_IP>/<share>`
- NAS internal:
  - `/mnt/main_pool/Main/media`
  - `/mnt/main_pool/Main/torrents`

---

## 2. Problem Statement

User wanted:
- Best IPTV *architecture* (not provider endorsement)
- Hardware decision: **Mini PC vs Nvidia Shield TV Pro**
- Ability to:
  - Watch IPTV reliably (HD / 4K)
  - Record IPTV streams (DVR)
  - Store recordings on NAS
  - Avoid buffering, instability, and over-complex builds
- Prior assistant responses were constrained or blocked when discussing IPTV services directly.

---

## 3. Root Cause

- **Provider discussion blocked** → led to incomplete answers.
- **Overthinking hardware**: N305 mini PC considered when use case is *client playback + DVR*, not server-side transcoding.
- **Recording responsibility confusion**:
  - Mini PC = server-style workload
  - Shield = client/DVR using NAS as storage

---

## 4. Final Fix / Known-Good Configuration

### Recommended Architecture (Final)

**Nvidia Shield TV Pro + NAS DVR**

- Shield handles:
  - IPTV playback
  - EPG
  - Recording scheduling
- NAS handles:
  - Storage only (no transcoding)
- IPTV app handles DVR logic

### IPTV Client Apps (DVR-capable)
- **TiviMate (Premium required for DVR)**
- IPTV Extreme Pro
- Kodi + PVR (advanced, optional)

### Why Shield Pro Wins
- Stable Android TV OS
- Excellent codec support (H.264 / H.265 / HDR / Dolby Vision)
- AI upscaling for lower-bitrate IPTV
- Native SMB mounting
- No Windows/Linux maintenance
- Works perfectly with NAS-backed DVR

---

## 5. Exact Configuration Steps

### Nvidia Shield → NAS Mount
1. Settings → Device Preferences → Storage
2. Add Network Storage (SMB)
3. Server: `<NAS_IP>`
4. Share: `<share_name>`
5. Auth: NAS username/password
6. Mount as internal or removable storage

### TiviMate DVR Path
Settings → Recording → Recording folder
/storage/<mounted_nas_share>/iptv_recordings

yaml
Copy code

### Network Requirements
- Shield **must be wired Ethernet**
- NAS **must be wired Ethernet**
- Avoid Wi-Fi for DVR

### VPN Usage
- Optional
- If used, install VPN **on Shield only**
- Do NOT VPN the NAS

---

## 6. Commands / Config Snippets

### NAS (SMB service)
- Enable SMB service
- Create dataset/share
- Permissions:
  - Read/Write
  - User-based auth (recommended)

_No shell commands required on Shield._

---

## 7. Verification Steps

1. Play live IPTV channel → confirm no buffering
2. Start recording from IPTV app
3. Verify file creation on NAS:
/mnt/main_pool/Main/media/iptv_recordings

yaml
Copy code
4. Playback recorded file from Shield
5. Reboot Shield → recordings persist
6. Record while watching another channel (requires ≥2 IPTV connections)

---

## 8. Warnings / “Do Not Do This Again”

- ❌ Do NOT use Shield internal storage for long-term DVR
- ❌ Do NOT record over Wi-Fi
- ❌ Do NOT overbuild (N305) unless running server workloads
- ❌ Do NOT run VPN on NAS
- ❌ Do NOT expect Roku remotes to control PCs
- ❌ Do NOT assume IPTV recording = zero bandwidth (counts as active stream)

---

## 9. Optional Alternatives (If Requirements Change)

- **Mini PC (N305)** only if:
- Running Plex/Jellyfin server
- Running TVHeadend
- Need multi-stream transcoding
- **Intel N100/N95 mini PC** acceptable but unnecessary for IPTV-only use

---

## 10. Final Decision (Locked)

**Use Nvidia Shield TV Pro + NAS-backed DVR via TiviMate Premium**

This is the simplest, most stable, and lowest-maintenance solution for the stated requirements.
