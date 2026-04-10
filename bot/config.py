from __future__ import annotations
"""
ORIA Bot — Configuration

Reads from the project's shared config.env (same file as Flask).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load the shared config.env from the project root (one level up from bot/)
_env_path = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(_env_path)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
FLASK_API_BASE_URL: str = os.getenv("FLASK_API_BASE_URL", "http://127.0.0.1:5001")
WEB_APP_URL: str = os.getenv("WEB_APP_URL", "http://127.0.0.1:5001")

# C-02: Shared API key for Flask ↔ Bot authentication
BOT_API_KEY: str = os.getenv("BOT_API_KEY", "")

# Admin IDs for broadcasting (comma-separated, optional)
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

# Port for the internal aiohttp server (Proactive Notifications)
NOTIFIER_PORT: int = int(os.getenv("NOTIFIER_PORT", "5002"))
