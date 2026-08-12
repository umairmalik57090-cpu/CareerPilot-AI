import json
from typing import Any

import pandas as pd


def build_dashboard_charts(history_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not history_entries:
        return []

    chart_data = pd.DataFrame(history_entries)
    if chart_data.empty:
        return []

    chart_data["analysis"] = [f"Analysis {idx + 1}" for idx in range(len(chart_data))]
    chart_data = chart_data.fillna(0)

    score_data = chart_data[["analysis", "resume_score", "ats_score", "job_match_score"]].copy()
    score_data = score_data.set_index("analysis")

    latest = chart_data.iloc[-1:]
    readiness_data = latest[["resume_score", "ats_score", "job_match_score", "skill_coverage", "interview_readiness"]].T
    readiness_data.columns = [latest.iloc[0]["analysis"]]

    return [
        {"type": "line", "title": "Resume vs ATS Score Trend", "data": score_data},
        {"type": "bar", "title": "Readiness Snapshot", "data": readiness_data},
    ]
