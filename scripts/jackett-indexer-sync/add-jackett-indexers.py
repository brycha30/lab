import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from file
load_dotenv('/root/scripts/.env.indexers')

# Dry run mode
DRY_RUN = True

# Pull vars from environment
JACKETT_API_KEY = os.getenv("JACKETT_API_KEY")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")

JACKETT_URL = os.getenv("JACKETT_URL")
SONARR_URL = os.getenv("SONARR_URL")
RADARR_URL = os.getenv("RADARR_URL")
