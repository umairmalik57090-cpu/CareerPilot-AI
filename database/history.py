import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
HISTORY_DIR = BASE_DIR / "history"
DB_PATH = HISTORY_DIR / "careerpilot_history.db"
LEGACY_PATH = HISTORY_DIR / "analysis_history.json"


def ensure_storage() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            target_role TEXT,
            resume_score INTEGER,
            ats_score INTEGER,
            job_match_score INTEGER,
            missing_skills INTEGER,
            interview_readiness INTEGER,
            summary TEXT,
            raw_data TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _load_legacy_history() -> list[dict[str, Any]]:
    if not LEGACY_PATH.exists():
        return []
    try:
        data = json.loads(LEGACY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def get_history_records() -> list[dict[str, Any]]:
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM analysis_history ORDER BY id DESC"
    ).fetchall()
    conn.close()

    records = []
    for row in rows:
        raw = json.loads(row["raw_data"]) if row["raw_data"] else {}
        records.append({
            "id": row["id"],
            "created_at": row["created_at"],
            "target_role": row["target_role"],
            "resume_score": row["resume_score"],
            "ats_score": row["ats_score"],
            "job_match_score": row["job_match_score"],
            "missing_skills": row["missing_skills"],
            "interview_readiness": row["interview_readiness"],
            "summary": row["summary"],
            "raw_data": raw,
        })

    legacy = _load_legacy_history()
    if legacy and not records:
        return legacy
    return records


def add_history_record(record: dict[str, Any]) -> int:
    ensure_storage()
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "created_at": record.get("created_at") or now,
        "target_role": record.get("target_role") or "General",
        "resume_score": int(record.get("resume_score", 0) or 0),
        "ats_score": int(record.get("ats_score", 0) or 0),
        "job_match_score": int(record.get("job_match_score", 0) or 0),
        "missing_skills": int(record.get("missing_skills", 0) or 0),
        "interview_readiness": int(record.get("interview_readiness", 0) or 0),
        "summary": record.get("summary") or "Resume analyzed",
        "raw_data": json.dumps(record.get("raw_data") or record, ensure_ascii=False),
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """
        INSERT INTO analysis_history (created_at, target_role, resume_score, ats_score, job_match_score, missing_skills, interview_readiness, summary, raw_data)
        VALUES (:created_at, :target_role, :resume_score, :ats_score, :job_match_score, :missing_skills, :interview_readiness, :summary, :raw_data)
        """,
        row,
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def delete_history_record(record_id: int) -> None:
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analysis_history WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def clear_history_records() -> None:
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analysis_history")
    conn.commit()
    conn.close()
    if LEGACY_PATH.exists():
        LEGACY_PATH.write_text("[]", encoding="utf-8")


def delete_user_data() -> None:
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analysis_history")
    conn.commit()
    conn.close()
    for path in [LEGACY_PATH, BASE_DIR / "uploads", BASE_DIR / "exports"]:
        if path.is_dir():
            for child in path.iterdir():
                if child.is_file():
                    child.unlink()
        elif path.exists() and path.is_file():
            path.unlink()
