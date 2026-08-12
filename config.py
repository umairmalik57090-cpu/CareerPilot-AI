import os
from pathlib import Path

from dotenv import load_dotenv

APP_CONFIG = {
    "title": "CareerPilot AI",
    "subtitle": "AI-Powered Career Intelligence & Interview Preparation Platform",
    "tagline": "Build a better resume, match your strengths to jobs, and prepare with confidence.",
    "icon": "🚀",
    "theme": "dark",
    "version": "0.2.0",
}

SIDEBAR_ITEMS = {
    "🏠 Dashboard": "Dashboard",
    "📄 Resume Analysis": "Resume Analysis",
    "🎯 ATS Checker": "ATS Checker",
    "🔍 Job Matcher": "Job Matcher",
    "🧠 Skill Gap": "Skill Gap",
    "🗺️ Career Roadmap": "Career Roadmap",
    "🎤 Interview Coach": "Interview Coach",
    "💬 AI Career Assistant": "AI Assistant",
    "📊 Career Analytics": "Career Analytics",
    "🕐 History": "History",
    "⚙️ Settings": "Settings",
    "ℹ️ About": "About",
}

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
HISTORY_DIR = BASE_DIR / "history"
EXPORTS_DIR = BASE_DIR / "exports"

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

DEFAULT_MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
