import re
from typing import Any

TECHNICAL_SKILLS = {
    "python": {"strong": ["python", "sql", "pandas", "numpy", "scikit-learn", "pytorch"], "moderate": ["api", "git", "flask", "django", "linux"]},
    "data": {"strong": ["machine learning", "ai", "statistics", "data analysis", "etl"], "moderate": ["tableau", "power bi", "excel"]},
    "cloud": {"strong": ["aws", "azure", "gcp", "docker", "kubernetes"], "moderate": ["ci/cd", "terraform", "linux"]},
    "web": {"strong": ["html", "css", "javascript", "react", "streamlit"], "moderate": ["rest apis", "node.js", "typescript"]},
}

SOFT_SKILLS = {
    "strong": ["leadership", "communication", "teamwork", "problem solving", "collaboration"],
    "moderate": ["presentation", "stakeholder management", "mentoring", "analytical thinking"],
}

TOOLS_TECH = ["python", "sql", "git", "docker", "aws", "azure", "excel", "power bi", "tableau", "linux", "streamlit", "pandas", "numpy"]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _priority_for(skill: str) -> str:
    high = {"docker", "kubernetes", "aws", "azure", "spark", "mlops", "deep learning", "nlp", "system design"}
    medium = {"sql", "pandas", "numpy", "linux", "git", "ci/cd", "rest api", "statistics"}
    if skill.lower() in high:
        return "High Priority"
    if skill.lower() in medium:
        return "Medium Priority"
    return "Low Priority"


def _recommendation_for(skill: str) -> str:
    mapping = {
        "docker": "Learn containerization basics and build a small multi-service app to practice image creation and deployment.",
        "kubernetes": "Study pods, deployments, and service networking to understand production orchestration workflows.",
        "aws": "Practice EC2, S3, IAM, and Lambda to gain hands-on cloud deployment fundamentals.",
        "azure": "Build a small cloud deployment flow using Azure services and understand resource provisioning.",
        "deep learning": "Complete a small CNN or transformer project and learn model training, evaluation, and tuning.",
        "sql": "Strengthen joins, window functions, and query optimization with a practical dataset project.",
        "git": "Practice version control workflows, branching, rebasing, and PR reviews in a real repository.",
        "mlops": "Learn CI/CD pipelines, experiment tracking, and model deployment workflows for production systems.",
        "system design": "Design scalable APIs and data flows, then document trade-offs for reliability and performance.",
        "nlp": "Build a text-classification or summarization project and work on preprocessing and embeddings.",
    }
    return mapping.get(skill.lower(), f"Practice {skill.title()} in a small project and document your learning outcomes.")


def analyze_skill_gaps(resume: dict[str, Any], job_description: str, target_role: str = "General") -> dict[str, Any]:
    resume_skills = {str(skill).strip().lower() for skill in resume.get("skills", [])}
    text = _normalize(job_description)
    job_terms = [term for term in re.findall(r"[A-Za-z][A-Za-z+#. /-]{1,}", text) if len(term) > 2]
    job_terms = [term.lower().strip() for term in job_terms]
    strong = []
    moderate = []
    missing = []

    for skill_group in TECHNICAL_SKILLS.values():
        for skill in skill_group["strong"] + skill_group["moderate"]:
            if skill in resume_skills:
                strong.append(skill)
            elif skill in job_terms:
                missing.append(skill)

    for skill in job_terms:
        if skill in resume_skills and skill not in strong:
            moderate.append(skill)

    soft_strong = [item for item in SOFT_SKILLS["strong"] if item in text]
    soft_moderate = [item for item in SOFT_SKILLS["moderate"] if item in text]
    missing_soft = [item for item in SOFT_SKILLS["strong"] + SOFT_SKILLS["moderate"] if item not in (soft_strong + soft_moderate)]

    tool_strong = [tool for tool in TOOLS_TECH if tool in resume_skills]
    tool_moderate = [tool for tool in TOOLS_TECH if tool not in tool_strong and tool in job_terms]
    missing_tools = sorted({tool for tool in job_terms if tool in tool_moderate or tool not in tool_strong and tool in {"docker", "aws", "azure", "kubernetes", "spark", "mlops", "git"}}, key=lambda item: item)

    missing_items = []
    seen = set()
    for skill in sorted(set(missing + missing_tools), key=lambda item: item):
        if skill in seen:
            continue
        seen.add(skill)
        missing_items.append({
            "skill": skill.title(),
            "priority": _priority_for(skill),
            "recommendation": _recommendation_for(skill),
        })

    return {
        "target_role": target_role,
        "technical_skills": {
            "strong": sorted(set(strong), key=lambda item: item),
            "moderate": sorted(set(moderate), key=lambda item: item),
            "missing": missing_items,
        },
        "soft_skills": {
            "strong": soft_strong,
            "moderate": soft_moderate,
            "missing": [
                {"skill": item.title(), "priority": "Medium Priority", "recommendation": f"Practice {item.title()} through team-based projects and peer feedback."}
                for item in missing_soft[:4]
            ],
        },
        "tools_technologies": {
            "strong": sorted(set(tool_strong), key=lambda item: item),
            "moderate": sorted(set(tool_moderate), key=lambda item: item),
            "missing": [
                {"skill": item.title(), "priority": _priority_for(item), "recommendation": _recommendation_for(item)}
                for item in sorted(set(missing_tools))
            ],
        },
    }
