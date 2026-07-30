import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from docx import Document

from config import HISTORY_DIR, UPLOADS_DIR
from utils import ensure_directories


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def validate_resume_file(uploaded_file) -> None:
    if uploaded_file is None:
        raise ValueError("No file was selected.")
    if getattr(uploaded_file, "size", None) in (None, 0):
        raise ValueError("The selected file is empty.")
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def extract_text_from_file(file_path: str | os.PathLike[str]) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    if suffix == ".txt":
        return read_resume_text(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def extract_text_from_pdf(file_path: str | os.PathLike[str]) -> str:
    doc = fitz.open(file_path)
    texts = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(text for text in texts if text).strip()


def extract_text_from_docx(file_path: str | os.PathLike[str]) -> str:
    document = Document(file_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs).strip()


def read_resume_text(file_path: str | os.PathLike[str]) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def parse_resume(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    name = ""
    email = ""
    phone = ""
    skills: list[str] = []
    education: list[str] = []
    experience: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []

    if lines:
        name = lines[0]

    email_match = re.search(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", cleaned)
    if email_match:
        email = email_match.group(1)

    phone_match = re.search(r"(?:\+?\d[\d .-]{8,}\d)", cleaned)
    if phone_match:
        phone = phone_match.group(0).strip()

    skill_section = extract_section(cleaned, ["Skills", "Technical Skills", "Core Skills"])
    if skill_section:
        skills = [item.strip() for item in re.split(r"[,;\n]", skill_section) if item.strip()]

    education_section = extract_section(cleaned, ["Education", "Academic Background"])
    if education_section:
        education = [item.strip() for item in re.split(r"\n|;", education_section) if item.strip()]

    experience_section = extract_section(cleaned, ["Experience", "Work Experience", "Professional Experience"])
    if experience_section:
        experience = [item.strip() for item in re.split(r"\n(?=\d|[A-Z])", experience_section) if item.strip()]

    projects_section = extract_section(cleaned, ["Projects", "Portfolio"])
    if projects_section:
        projects = [item.strip() for item in re.split(r"\n|;", projects_section) if item.strip()]

    certification_section = extract_section(cleaned, ["Certifications", "Licenses"])
    if certification_section:
        certifications = [item.strip() for item in re.split(r"\n|;", certification_section) if item.strip()]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
    }


def extract_section(text: str, headings: list[str]) -> str:
    for heading in headings:
        pattern = re.compile(rf"{re.escape(heading)}\s*[:\-]?\s*(.*?)(?=(?:\n[A-Z][A-Za-z &/]+\s*[:\-]?|$))", re.IGNORECASE | re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return ""


def save_uploaded_resume(uploaded_file) -> tuple[str, str]:
    ensure_directories()
    validate_resume_file(uploaded_file)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", uploaded_file.name)
    destination = UPLOADS_DIR / safe_name
    with destination.open("wb") as handle:
        handle.write(uploaded_file.getbuffer())
    return str(destination), safe_name


def build_history_entry(uploaded_file, parsed_resume: dict[str, Any], saved_path: str) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "resume_name": uploaded_file.name,
        "resume_score": 0,
        "ats_score": 0,
        "role": "Resume Upload",
        "saved_path": saved_path,
        "parsed": parsed_resume,
    }


def save_history_entry(entry: dict[str, Any]) -> None:
    ensure_directories()
    history_path = HISTORY_DIR / "analysis_history.json"
    entries = []
    if history_path.exists():
        try:
            entries = json.loads(history_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
    entries.append(entry)
    history_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def load_history_entries() -> list[dict[str, Any]]:
    ensure_directories()
    history_path = HISTORY_DIR / "analysis_history.json"
    if not history_path.exists():
        return []
    try:
        return json.loads(history_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
