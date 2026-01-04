# GitHub Setup: Jackett Indexer Scripts

This guide documents how to set up, version control, and manage your custom Jackett-to-Sonarr/Radarr indexer automation script in a Docker LXC container.

---

## 1. Project Structure

Place your scripts in:
```bash
/root/scripts/
```

Example contents:
```bash
/root/scripts/
├── add-jackett-indexers.py
├── .env.indexers
├── requirements.txt
└── README.md
```

---

## 2. Create requirements.txt

Create a `requirements.txt` file containing:
```txt
requests
python-dotenv
```

Install the required dependencies:
```bash
pip3 install -r /root/scripts/requirements.txt
```

---

## 3. Create README.md

Basic `README.md` example:
```markdown
# Jackett to Sonarr/Radarr Indexer Script

This script automates adding all Jackett indexers to Sonarr and Radarr.

## Setup

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Configure `.env.indexers` with API keys and URLs:
   ```env
   JACKETT_API_KEY=xxxxx
   SONARR_API_KEY=xxxxx
   RADARR_API_KEY=xxxxx
   JACKETT_URL=http://192.168.190.10:9117
   SONARR_URL=http://192.168.190.10:8989
   RADARR_URL=http://192.168.190.10:7878
   SONARR_USER=bryan
   SONARR_PASS='B!RYan?'
   RADARR_USER=bryan
   RADARR_PASS='B!RYan?'
   ```

3. Run script (dry run first):
   ```bash
   DRY_RUN=1 python3 add-jackett-indexers.py
   ```

## Notes
- Compatible with Debian 12 inside Docker LXC.
- Logs and debug info are printed to console.
```

---

## 4. Create .gitignore

```bash
cat <<EOF > /root/scripts/.gitignore
.env.indexers
__pycache__/
*.pyc
EOF
```

---

## 5. Initialize Git Repository

```bash
cd /root/scripts
git init
git remote add origin git@github.com:brycha30/jackett-indexer-sync.git
git checkout -b main
git add .
git commit -m "Initial commit: Jackett indexer sync script"
git push -u origin main
```

---

## ✅ Done
Your automation script and environment are now version-controlled in GitHub. You can clone this setup onto any system with:
```bash
git clone git@github.com:brycha30/jackett-indexer-sync.git
```

