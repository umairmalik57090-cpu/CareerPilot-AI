import os
from pathlib import Path

from dotenv import load_dotenv

APP_CONFIG = {
    "title": "CareerPilot AI",
    "subtitle": "Your Personal AI Resume & Interview Coach",
    "tagline": "Build a Better Resume. Prepare Smarter. Land Your Dream Job.",
    "icon": "🚀",
    "theme": "dark",
    "version": "0.1.0",
}

SIDEBAR_ITEMS = {
    "Dashboard": "Home",
    "Resume Analysis": "Resume Analysis",
    "ATS Checker": "ATS Checker",
    "Interview Coach": "Interview Coach",
    "Skill Gap": "Skill Gap",
    "Career Roadmap": "Career Roadmap",
    "History": "History",
    "Settings": "Settings",
    "About": "About",
}

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
HISTORY_DIR = BASE_DIR / "history"
EXPORTS_DIR = BASE_DIR / "exports"

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

DEFAULT_MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
