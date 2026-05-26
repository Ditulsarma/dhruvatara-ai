"""
ধ্ৰুৱতৰা AI - Configuration
Centralized configuration for database path and other settings.
On Railway, the database is stored in /data/ which is a persistent volume.
Locally, it falls back to the current directory.
"""
import os

# Database path: use /data/ on Railway (persistent volume), else local directory
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "dhrubatara.db"))

# If /data exists (Railway volume mount), use it
if os.path.isdir("/data"):
    DB_PATH = "/data/dhrubatara.db"
