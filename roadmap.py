import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq_client import generate_chat_completion

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def generate_skill_gap_analysis(
    role: str, resume_text: str, comprehensive_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    if comprehensive_data:
        missing = comprehensive_data.get("missing_skills", [])
        roadmap = comprehensive_data.get("career_roadmap", {})
        return {
            "missing_skills": missing or ["Python", "SQL", "System Design"],
            "recommended_certifications": roadmap.get("resources", ["AWS Cloud Practitioner"]),
            "recommended_projects": roadmap.get("projects", ["Build a portfolio analytics dashboard"]),
            "learning_priorities": roadmap.get("weekly_goals", ["Practice coding interviews", "Improve project storytelling"]),
        }

    return {
        "missing_skills": ["Python", "SQL", "System Design"],
        "recommended_certifications": ["AWS Cloud Practitioner"],
        "recommended_projects": ["Build a portfolio analytics dashboard"],
        "learning_priorities": ["Practice coding interviews", "Improve project storytelling"],
    }


def generate_roadmap(
    role: str, resume_text: str, comprehensive_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    if comprehensive_data and "career_roadmap" in comprehensive_data:
        crm = comprehensive_data["career_roadmap"]
        if isinstance(crm, dict) and crm.get("thirty_day_plan"):
            return crm

    return {
        "thirty_day_plan": ["Refine resume and LinkedIn profile", "Complete one portfolio project"],
        "sixty_day_plan": ["Build two project demos", "Practice interviews"],
        "ninety_day_plan": ["Apply to 20 roles", "Improve case-study storytelling"],
        "weekly_goals": ["Code 5 hours weekly", "Read 2 articles weekly"],
        "resources": ["YouTube: Python for Data Science", "Book: Designing Data-Intensive Applications"],
        "projects": ["Build a full-stack AI app", "Create a dashboard with analytics"],
    }


def rewrite_resume_section(section_name: str, content: str) -> str:
    prompt = f"""
    Rewrite this resume section professionally and concisely for maximum recruiters' impact.
    Section: {section_name}
    Content: {content}

    Return ONLY the rewritten section text.
    """
    try:
        response = generate_chat_completion(
            prompt=prompt,
            system_prompt="You are an expert resume writer. Return only the improved text.",
            temperature=0.3,
        )
        return response.strip() or content
    except Exception:
        return f"Professional rewrite for {section_name}: {content}"


def generate_linkedin_suggestions(
    profile_text: str, comprehensive_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    if comprehensive_data:
        summary = comprehensive_data.get("executive_summary", "")
        skills = comprehensive_data.get("keyword_suggestions", ["Python", "Machine Learning", "Streamlit"])
        suggestions = comprehensive_data.get("improvement_suggestions", ["Add project outcomes", "Mention measurable impact"])
        return {
            "headline": "AI Engineer & Software Specialist | Turning Ideas into Solutions",
            "about_section": summary or "I build modern software products with high impact and measurable results.",
            "skills": skills[:5],
            "suggestions": suggestions[:4],
        }

    return {
        "headline": "AI Engineer | Building practical ML systems",
        "about_section": "I build products that turn ideas into reliable AI solutions.",
        "skills": ["Python", "Machine Learning", "Streamlit"],
        "suggestions": ["Add project outcomes", "Mention measurable impact"],
    }


def generate_career_tips() -> dict[str, Any]:
    return {
        "resume_tips": ["Tailor each resume to the role", "Quantify achievements"],
        "interview_tips": ["Use STAR stories", "Practice with mock interviews"],
        "career_advice": ["Build a portfolio that signals execution", "Stay active in the community"],
        "salary_negotiation_tips": ["Anchor your range on market data", "Discuss impact and ownership"],
        "linkedin_tips": ["Keep your headline specific", "Share your work regularly"],
        "portfolio_suggestions": ["Show before/after metrics", "Document your decision-making"],
    }
