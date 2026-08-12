from typing import Any


def build_roadmap(target_role: str, resume_skills: list[str] | None = None, skill_gap: dict[str, Any] | None = None) -> dict[str, Any]:
    role = (target_role or "AI Engineer").strip() or "AI Engineer"
    resume_skills = [str(item).strip() for item in (resume_skills or []) if str(item).strip()]
    skill_gap = skill_gap or {}

    role_templates = {
        "AI Engineer": ["Python", "SQL", "Machine Learning", "MLOps", "Deep Learning"],
        "Machine Learning Engineer": ["Python", "Statistics", "Pytorch", "ML Pipelines", "Model Deployment"],
        "Data Scientist": ["Python", "Statistics", "SQL", "Pandas", "Machine Learning"],
        "Python Developer": ["Python", "Git", "SQL", "APIs", "Testing"],
        "Web Developer": ["HTML", "CSS", "JavaScript", "React", "APIs"],
        "Data Analyst": ["SQL", "Excel", "Python", "Dashboarding", "Statistics"],
        "Software Engineer": ["Python", "Git", "System Design", "Testing", "APIs"],
    }

    template = role_templates.get(role, ["Python", "Git", "SQL", "Cloud", "Project Delivery"])
    phase_templates = [
        {"phase": "Phase 1 — Foundation", "items": [
            {"skill": item, "priority": "High", "difficulty": "Beginner", "project": f"Build a mini project in {item}", "completed": False}
            for item in template[:3]
        ]},
        {"phase": "Phase 2 — Core Skills", "items": [
            {"skill": item, "priority": "High", "difficulty": "Intermediate", "project": f"Create a portfolio artifact for {item}", "completed": False}
            for item in template[3:5]
        ]},
        {"phase": "Phase 3 — Advanced Skills", "items": [
            {"skill": "System Design" if role in {"Software Engineer", "AI Engineer"} else "Model Optimization", "priority": "Medium", "difficulty": "Advanced", "project": "Design and explain a scalable solution architecture", "completed": False},
            {"skill": "Production Deployment" if role in {"AI Engineer", "Machine Learning Engineer"} else "Portfolio Delivery", "priority": "Medium", "difficulty": "Advanced", "project": "Ship a complete end-to-end project to GitHub", "completed": False},
        ]},
        {"phase": "Phase 4 — Projects", "items": [
            {"skill": "Portfolio Project 1", "priority": "High", "difficulty": "Intermediate", "project": f"Build a role-specific project for {role}", "completed": False},
            {"skill": "Portfolio Project 2", "priority": "High", "difficulty": "Intermediate", "project": "Add a case study with before/after metrics", "completed": False},
            {"skill": "Portfolio Project 3", "priority": "Medium", "difficulty": "Intermediate", "project": "Deploy the project with documentation and screenshots", "completed": False},
        ]},
        {"phase": "Phase 5 — Job Preparation", "items": [
            {"skill": "Resume", "priority": "High", "difficulty": "Beginner", "project": "Tailor the resume to the target role and include metrics", "completed": False},
            {"skill": "LinkedIn", "priority": "High", "difficulty": "Beginner", "project": "Rewrite the headline and about section", "completed": False},
            {"skill": "Interview Practice", "priority": "High", "difficulty": "Intermediate", "project": "Practice STAR answers and technical cases", "completed": False},
        ]},
    ]

    for phase in phase_templates:
        for item in phase["items"]:
            item["completed"] = bool(item["skill"].lower() in [skill.lower() for skill in resume_skills])

    return {
        "role": role,
        "phases": phase_templates,
        "skill_gap_summary": skill_gap.get("technical_skills", {}),
    }
