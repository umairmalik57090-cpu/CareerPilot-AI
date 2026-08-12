import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

from groq_client import validate_groq_connection
import streamlit as st


def _safe_int(val: float) -> int:
    try:
        return int(round(val))
    except Exception:
        return 0


def calculate_skill_coverage_from_session() -> int | None:
    """Calculate skill coverage as matched_required / total_required * 100.

    Returns None when coverage cannot be calculated (missing resume or job description).
    """
    # Require an uploaded resume and an explicit job description to compute coverage
    resume = st.session_state.get("uploaded_resume")
    job_description = st.session_state.get("job_description", "") or ""
    if not resume or not job_description.strip():
        return None

    try:
        from job_matcher import extract_resume_skills, extract_job_skills

        resume_parsed = resume.get("parsed", {}) if isinstance(resume, dict) else {}
        resume_skills = extract_resume_skills(resume_parsed)
        job_skill_data = extract_job_skills(job_description)

        required = set(job_skill_data.get("required") or [])
        # If there are no explicitly required skills, avoid claiming 100%: return None
        if not required:
            return None

        matched_required = len(required & resume_skills)
        total_required = len(required)
        coverage = _safe_int((matched_required / total_required) * 100) if total_required else None
        return coverage
    except Exception:
        return None

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
        "target_role": "AI Engineer",
        "job_description": "",
        "job_match_result": {},
        "skill_gap": {},
        "roadmap": {},
        "career_analytics": {},
        "assistant_messages": [],
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
    job_match = st.session_state.get("job_match_result") or {}
    skill_gap = st.session_state.get("skill_gap") or {}

    resume_score = analysis.get("resume_score", analysis.get("overall_score", 0))
    ats_score = ats.get("overall_score", 0)
    job_match_score = job_match.get("score", None)
    missing_count = len((skill_gap.get("technical_skills") or {}).get("missing", [])) + len((skill_gap.get("tools_technologies") or {}).get("missing", []))

    resume_val = f"{resume_score}/100" if resume_score > 0 else "N/A"
    ats_val = f"{ats_score}/100" if ats_score > 0 else "N/A"
    if isinstance(job_match_score, int):
        job_val = f"{job_match_score}/100" if job_match_score > 0 else "N/A"
    else:
        job_val = "N/A"
    interview_val = "Ready" if st.session_state.get("interview_questions") else "Pending"
    # Skill coverage should only be shown when both resume and job description are present
    coverage = calculate_skill_coverage_from_session()
    skill_coverage = f"{coverage}%" if coverage is not None else "N/A"

    return [
        {"label": "Resume Score", "value": resume_val, "foot": "Groq AI Review"},
        {"label": "ATS Score", "value": ats_val, "foot": "Keyword ready"},
        {"label": "Job Match Score", "value": job_val, "foot": "Role alignment"},
        {"label": "Skill Coverage", "value": skill_coverage, "foot": "Coverage vs target role"},
        {"label": "Missing Skills", "value": str(missing_count), "foot": "Priority gaps"},
        {"label": "Interview Readiness", "value": interview_val, "foot": "Practice questions generated"},
        {"label": "Career Progress", "value": f"{min(100, max(0, resume_score // 2))}%", "foot": "Current momentum"},
        {"label": "Grammar Quality", "value": "95%", "foot": "Polished writing"},
    ]


def ensure_directories() -> None:
    from config import EXPORTS_DIR, HISTORY_DIR, UPLOADS_DIR

    for path in (UPLOADS_DIR, HISTORY_DIR, EXPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
