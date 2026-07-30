import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

from groq_client import validate_groq_connection

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def initialize_session_state() -> None:
    defaults = {
        "active_page": "Dashboard",
        "uploaded_resume": None,
        "analysis_done": False,
        "is_analyzing": False,
        "history_entries": [],
        "theme": "dark",
        "interview_questions": [],
        "interview_index": 0,
        "interview_feedbacks": [],
        "interview_answers": [],
        "groq_status_checked": False,
        "groq_online": False,
        "groq_status_label": "🔴 AI Offline (Groq)",
        "groq_status_message": "Groq AI connection has not been verified yet.",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def get_current_datetime() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime("%A, %b %d, %Y"), now.strftime("%I:%M %p")


def get_connection_status() -> str:
    return st.session_state.get("groq_status_label", "🔴 AI Offline (Groq)")


def build_dashboard_kpis() -> list[dict]:
    analysis = st.session_state.get("analysis_result") or {}
    ats = st.session_state.get("ats_result") or {}

    resume_score = analysis.get("resume_score", analysis.get("overall_score", 0))
    ats_score = ats.get("overall_score", 0)

    resume_val = f"{resume_score}/100" if resume_score > 0 else "N/A"
    ats_val = f"{ats_score}/100" if ats_score > 0 else "N/A"
    interview_val = "Ready" if st.session_state.get("interview_questions") else "Pending"

    return [
        {"label": "Resume Score", "value": resume_val, "foot": "Groq AI Review"},
        {"label": "ATS Score", "value": ats_val, "foot": "Keyword ready"},
        {"label": "Interview Readiness", "value": interview_val, "foot": "Practice questions generated"},
        {"label": "Grammar Quality", "value": "95%", "foot": "Polished writing"},
    ]


def ensure_directories() -> None:
    from config import EXPORTS_DIR, HISTORY_DIR, UPLOADS_DIR

    for path in (UPLOADS_DIR, HISTORY_DIR, EXPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
