import re
from typing import Any

SKILL_ALIAS_MAP = {
    "python": "Python",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "scikit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "computer vision": "Computer Vision",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "large language models": "LLMs",
    "llm": "LLMs",
    "llms": "LLMs",
    "cloud computing": "Cloud Computing",
    "data preprocessing": "Data Preprocessing",
    "model evaluation": "Model Evaluation",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "git and github": "Git/GitHub",
    "git/github": "Git/GitHub",
    "github": "Git/GitHub",
    "git": "Git/GitHub",
    "docker": "Docker",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "streamlit": "Streamlit",
    "flask": "Flask",
    "sql": "SQL",
    "kubernetes": "Kubernetes",
    "spark": "Spark",
    "airflow": "Airflow",
    "mlops": "MLOps",
    "generative ai": "Generative AI",
    "rest api design": "REST APIs",
    "api development": "REST APIs",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "aws s3": "AWS",
    "azure devops": "Azure",
    "gcp platform": "GCP",
}

SKILL_KEYS = sorted(SKILL_ALIAS_MAP.keys(), key=lambda phrase: len(phrase.split()), reverse=True)

SECTION_KEYWORDS = {
    "required": [
        "required skills",
        "requirements",
        "must have",
        "must-have",
        "required:",
        "minimum qualifications",
        "must be",
        "necessary skills",
        "required qualifications",
        "you have",
        "you are",
    ],
    "preferred": [
        "preferred skills",
        "preferred qualifications",
        "nice to have",
        "nice-to-have",
        "bonus points",
        "would be a plus",
    ],
    "responsibilities": [
        "responsibilities",
        "role responsibilities",
        "you will",
        "your responsibilities",
    ],
    "qualifications": [
        "qualifications",
        "desired qualifications",
        "experience with",
        "experience in",
        "experience using",
    ],
}

SECTION_LOOKUP = {
    key: value for key, keywords in SECTION_KEYWORDS.items() for value in keywords
}

def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9/\-+ ]", " ", (text or "").lower())


def extract_skills_from_text(text: str) -> set[str]:
    if not text:
        return set()

    normalized = _normalize_text(text)
    found_skills: set[str] = set()
    for alias in SKILL_KEYS:
        pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
        if re.search(pattern, normalized):
            found_skills.add(SKILL_ALIAS_MAP[alias])
    return found_skills


def split_job_description_sections(job_description: str) -> dict[str, str]:
    sections = {
        "required": "",
        "preferred": "",
        "responsibilities": "",
        "qualifications": "",
        "general": "",
    }

    current = "general"
    for raw_line in job_description.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        matched = False
        for section, keywords in SECTION_KEYWORDS.items():
            for keyword in keywords:
                if lower.startswith(keyword):
                    current = section
                    matched = True
                    # capture inline content that may follow the heading on the same line
                    # e.g. "Required Skills: Python, SQL"
                    try:
                        rest = line[len(keyword):].lstrip(":- ")
                        if rest:
                            sections[current] += rest + " "
                    except Exception:
                        pass
                    break
            if matched:
                break
        if matched:
            continue
        sections[current] += line + " "

    return sections


def extract_job_skills(job_description: str) -> dict[str, set[str]]:
    sections = split_job_description_sections(job_description)
    required = extract_skills_from_text(sections["required"] or sections["general"])
    preferred = extract_skills_from_text(sections["preferred"])
    responsibilities = extract_skills_from_text(sections["responsibilities"])
    qualifications = extract_skills_from_text(sections["qualifications"])

    all_skills = set()
    if required:
        all_skills |= required
    else:
        all_skills |= extract_skills_from_text(sections["general"])

    all_skills |= preferred | responsibilities | qualifications
    return {
        "required": required or all_skills,
        "preferred": preferred,
        "responsibilities": responsibilities,
        "qualifications": qualifications,
        "all": all_skills,
    }


def extract_resume_skills(resume: dict[str, Any]) -> set[str]:
    if not resume:
        return set()

    skills = set()
    for item in resume.get("skills", []):
        skills |= extract_skills_from_text(str(item))
    skills |= extract_skills_from_text(" ".join(str(item) for item in resume.get("experience", []) + resume.get("projects", []) + resume.get("education", []) + resume.get("certifications", [])))
    return skills


def _extract_years(value: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*years?", (value or "").lower())
    if not matches:
        return 0.0
    return float(matches[0])


def calculate_job_match(resume: dict[str, Any], job_description: str, target_role: str = "General") -> dict[str, Any]:
    # To keep a single source of truth, delegate to calculate_job_match_score
    resume_skills = extract_resume_skills(resume)
    job_skill_data = extract_job_skills(job_description)

    required_skills = job_skill_data.get("required", set())
    preferred_skills = job_skill_data.get("preferred", set())

    # derive experience numbers
    def _extract_required_experience_from_job(text: str) -> float:
        m = re.search(r"(\d+(?:\.\d+)?)\+?\s*years?", (text or "").lower())
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return 0.0
        return 0.0

    job_required_years = _extract_required_experience_from_job(job_description)

    def _extract_resume_years(parsed_resume: dict[str, Any]) -> float:
        if not parsed_resume:
            return 0.0
        years = 0.0
        for item in parsed_resume.get("experience", []):
            years += _extract_years(str(item))
        if years == 0.0:
            combined = " ".join(str(x) for x in (parsed_resume.get("skills", []) + parsed_resume.get("projects", []) + parsed_resume.get("education", [])))
            years = _extract_years(combined)
        return years

    resume_years = _extract_resume_years(resume)

    return calculate_job_match_score(
        resume_skills=resume_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        candidate_experience_years=resume_years,
        required_experience_years=job_required_years,
        target_role=target_role,
        all_job_skills=job_skill_data.get("all", set()),
        parsed_resume=resume,
    )


def calculate_job_match_score(
    resume_skills: set[str],
    required_skills: set[str],
    preferred_skills: set[str],
    candidate_experience_years: float | None = None,
    required_experience_years: float | None = None,
    target_role: str = "General",
    all_job_skills: set[str] | None = None,
    parsed_resume: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Centralized scoring function that returns a consistent structure used across the app.
    """
    all_job_skills = all_job_skills or set()

    matched_required = sorted([s for s in required_skills if s in resume_skills])
    missing_required = sorted([s for s in required_skills if s not in resume_skills])

    matched_preferred = sorted([s for s in preferred_skills if s in resume_skills])
    missing_preferred = sorted([s for s in preferred_skills if s not in resume_skills])

    # Partial matches: tokens overlap between job skill phrase and resume skills
    partial_matches: set[str] = set()
    for skill in (all_job_skills - set(matched_required) - set(matched_preferred)):
        skill_tokens = set(re.findall(r"[a-z0-9]+", skill.lower()))
        for resume_skill in resume_skills:
            resume_tokens = set(re.findall(r"[a-z0-9]+", resume_skill.lower()))
            if skill_tokens & resume_tokens:
                partial_matches.add(skill)
                break

    # Percentages
    required_pct = None
    if required_skills:
        required_pct = int(round((len(matched_required) / len(required_skills)) * 100))

    preferred_pct = None
    if preferred_skills:
        preferred_pct = int(round((len(matched_preferred) / len(preferred_skills)) * 100))

    experience_pct = None
    if required_experience_years and candidate_experience_years is not None and required_experience_years > 0:
        experience_pct = int(round(min(candidate_experience_years / required_experience_years, 1.0) * 100))

    # Aggregate final score with weights and normalization
    weights = {"required": 50, "preferred": 20, "experience": 30}
    components: list[tuple[int, int]] = []  # list of (pct, weight)
    total_weight = 0
    if required_pct is not None:
        components.append((required_pct, weights["required"]))
        total_weight += weights["required"]
    if preferred_pct is not None:
        components.append((preferred_pct, weights["preferred"]))
        total_weight += weights["preferred"]
    if experience_pct is not None:
        components.append((experience_pct, weights["experience"]))
        total_weight += weights["experience"]

    final_score = None
    if total_weight > 0 and components:
        final_score = int(round(sum(p * w for p, w in components) / total_weight))

    # Build missing skills detailed with priority
    missing_detailed: list[dict[str, str]] = []
    for s in missing_required:
        missing_detailed.append({"skill": s, "priority": "High", "reason": "Required by the target role but not detected in the resume."})
    for s in missing_preferred:
        missing_detailed.append({"skill": s, "priority": "Medium", "reason": "Preferred skill not detected in the resume."})

    # Recommended path: required missing first then preferred
    recommended_path: list[dict[str, str]] = []
    for s in missing_required + missing_preferred:
        difficulty = "Intermediate"
        low = s.lower()
        if any(k in low for k in ("deep learning", "tensorflow", "pytorch", "model")):
            difficulty = "Advanced"
        elif any(k in low for k in ("git", "sql", "docker", "rest", "api")):
            difficulty = "Intermediate"
        else:
            difficulty = "Beginner"
        why = "Important for the role."
        focus = "Hands-on projects and focused tutorials."
        recommended_path.append({"skill": s, "why": why, "focus": focus, "difficulty": difficulty})

    # Why score explanation
    why_parts: list[str] = []
    if required_pct is not None:
        why_parts.append(f"Your resume matches {len(matched_required)} of {len(required_skills)} required skills.")
    else:
        why_parts.append("No explicit required skills found in the job description.")
    if preferred_pct is not None:
        why_parts.append(f"You match {len(matched_preferred)} preferred skills.")
    if missing_required:
        why_parts.append(f"Missing required skills include: {', '.join(missing_required[:6])}.")
    if experience_pct is not None:
        why_parts.append(f"Experience alignment: {experience_pct}% (required ~{required_experience_years} yrs; resume ~{candidate_experience_years} yrs).")

    why_text = " ".join(why_parts)

    return {
        "score": final_score if final_score is not None else None,
        "matching_skills": sorted(list((set(required_skills) | set(preferred_skills) | set(all_job_skills)) & set(resume_skills))),
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "missing_skills": missing_required + missing_preferred,
        "missing_skills_detailed": missing_detailed,
        "partial_matches": sorted(partial_matches),
        "preferred_skills": sorted(list(preferred_skills)),
        "required_skills": sorted(list(required_skills)),
        "skill_coverage": required_pct,
        "experience_gap": {
            "job_required_years": required_experience_years if required_experience_years else None,
            "resume_years": candidate_experience_years if candidate_experience_years is not None else None,
            "alignment_pct": experience_pct,
        },
        "score_breakdown": {
            "required_match": required_pct,
            "preferred_match": preferred_pct,
            "experience_alignment": experience_pct,
            "overall": final_score if final_score is not None else None,
        },
        "why_score": why_text,
        "recommended_path": recommended_path if recommended_path else [],
        "target_role": target_role,
    }
