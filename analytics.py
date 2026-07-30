import json
from typing import Any

import pandas as pd


def build_dashboard_charts(history_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not history_entries:
        return []

    chart_data = pd.DataFrame(history_entries)
    if chart_data.empty:
        return []

    score_data = chart_data[["resume_score", "ats_score"]].copy()
    score_data.index = range(1, len(score_data) + 1)

    readiness_data = pd.DataFrame(
        {
            "Metric": ["Resume", "ATS", "Interview", "Grammar"],
            "Score": [80, 75, 70, 65],
        }
    ).set_index("Metric")

    return [
        {"type": "line", "title": "Resume vs ATS Score Trend", "data": score_data},
        {"type": "bar", "title": "Readiness Snapshot", "data": readiness_data},
    ]
