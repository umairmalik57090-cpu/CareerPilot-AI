import re
from typing import Any


def calculate_ats_score(parsed_resume: dict[str, Any], job_description: str | None = None) -> dict[str, Any]:
    text = " ".join(
        [
            " ".join(parsed_resume.get("skills", [])),
            " ".join(parsed_resume.get("experience", [])),
            " ".join(parsed_resume.get("education", [])),
            " ".join(parsed_resume.get("projects", [])),
        ]
    ).lower()

    keyword_hits = 0
    keywords = []
    if job_description:
        job_terms = re.findall(r"[A-Za-z+#.]+", job_description.lower())
        target_terms = [term for term in job_terms if len(term) > 3 and term not in {"the", "and", "for", "with", "your", "that", "from"}]
        for term in target_terms:
            if term in text:
                keyword_hits += 1
                keywords.append(term)

    skills_score = min(100, 20 + 10 * len(parsed_resume.get("skills", [])))
    experience_score = min(100, 25 + 5 * len(parsed_resume.get("experience", [])))
    education_score = min(100, 60 + 5 * len(parsed_resume.get("education", [])))
    projects_score = min(100, 50 + 8 * len(parsed_resume.get("projects", [])))
    formatting_score = 85 if parsed_resume.get("name") and parsed_resume.get("email") else 70

    if job_description:
        keyword_score = min(100, int((keyword_hits / max(1, len(target_terms))) * 100))
    else:
        keyword_score = 75

    overall_score = int((formatting_score * 0.2) + (keyword_score * 0.25) + (experience_score * 0.2) + (skills_score * 0.2) + (education_score * 0.1) + (projects_score * 0.05))

    return {
        "overall_score": max(0, min(100, overall_score)),
        "formatting_score": formatting_score,
        "keywords_score": keyword_score,
        "experience_score": experience_score,
        "skills_score": skills_score,
        "education_score": education_score,
        "projects_score": projects_score,
        "keywords": keywords[:10],
        "suggestions": [
            "Add more role-specific keywords to your summary.",
            "Include measurable achievements in each experience bullet.",
            "Match section headings to common ATS conventions.",
        ],
    }
