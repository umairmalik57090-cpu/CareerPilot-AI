import hashlib
import json
from typing import Any

from ats_checker import calculate_ats_score
from groq_client import (
    generate_chat_completion,
    parse_json_response,
)

_ANALYSIS_CACHE: dict[str, dict[str, Any]] = {}


def get_cache_key(resume_text: str, target_role: str = "General") -> str:
    content = f"{target_role}::{resume_text.strip()}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def clear_analysis_cache() -> None:
    _ANALYSIS_CACHE.clear()


def analyze_resume_comprehensive(
    resume_text: str, parsed_resume: dict[str, Any], target_role: str = "General"
) -> dict[str, Any]:
    cache_key = get_cache_key(resume_text, target_role)
    if cache_key in _ANALYSIS_CACHE:
        cached_result = dict(_ANALYSIS_CACHE[cache_key])
        cached_result["from_cache"] = True
        return cached_result

    prompt = f"""
You are an expert senior recruiter, ATS specialist, and executive career coach.
Analyze the following resume for the target role: "{target_role}".

Resume Text:
{resume_text}

Parsed Structured Resume Data:
{json.dumps(parsed_resume, indent=2)}

Perform a complete career evaluation and return ONLY a valid JSON object with the exact key structure below:

{{
  "resume_score": 85,
  "ats_score": 78,
  "executive_summary": "High-level summary of candidate qualifications, standout achievements, and immediate gaps.",
  "strengths": ["Strength point 1", "Strength point 2", "Strength point 3"],
  "weaknesses": ["Weakness point 1", "Weakness point 2"],
  "missing_skills": ["Skill 1", "Skill 2", "Skill 3"],
  "interview_questions": [
    "Technical or behavioral question 1?",
    "Technical or behavioral question 2?",
    "Technical or behavioral question 3?",
    "Technical or behavioral question 4?",
    "Technical or behavioral question 5?"
  ],
  "career_roadmap": {{
    "thirty_day_plan": ["Action 1 for first 30 days", "Action 2 for first 30 days"],
    "sixty_day_plan": ["Action 1 for 60 days", "Action 2 for 60 days"],
    "ninety_day_plan": ["Action 1 for 90 days", "Action 2 for 90 days"],
    "weekly_goals": ["Goal 1", "Goal 2"],
    "resources": ["Resource 1", "Resource 2"],
    "projects": ["Project suggestion 1", "Project suggestion 2"]
  }},
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
  "missing_sections": ["Section 1", "Section 2"],
  "grammar_issues": ["Grammar check note 1"],
  "formatting_suggestions": ["Formatting tip 1"],
  "professional_summary_review": "Review of the professional summary section.",
  "technical_skills_review": "Review of technical skills depth and relevance.",
  "soft_skills_review": "Review of communication and soft skills demonstrated.",
  "keyword_suggestions": ["Keyword 1", "Keyword 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "ats_details": {{
    "formatting_score": 85,
    "keywords_score": 75,
    "experience_score": 80,
    "skills_score": 85,
    "education_score": 80,
    "projects_score": 75,
    "keywords": ["matched_keyword_1", "matched_keyword_2"],
    "suggestions": ["ATS suggestion 1", "ATS suggestion 2"]
  }}
}}

Rules:
- resume_score and ats_score must be integers between 0 and 100.
- All JSON keys listed above MUST be present in the output.
- Do not wrap the JSON in extra text outside the JSON object.
"""

    try:
        text_response = generate_chat_completion(
            prompt=prompt,
            system_prompt="You are an expert senior recruiter and career coach. Return ONLY valid JSON.",
            json_mode=True,
            temperature=0.3,
        )
        parsed = parse_json_response(text_response)

        local_ats = calculate_ats_score(parsed_resume)
        result = {
            "resume_score": int(parsed.get("resume_score", parsed.get("overall_score", 75))),
            "overall_score": int(parsed.get("resume_score", parsed.get("overall_score", 75))),
            "ats_score": int(parsed.get("ats_score", local_ats.get("overall_score", 70))),
            "executive_summary": str(
                parsed.get("executive_summary")
                or parsed.get("professional_summary_review")
                or "Resume parsed successfully. Review your strengths and career roadmap below."
            ),
            "strengths": parsed.get("strengths") or ["Clear technical background", "Structured work history"],
            "weaknesses": parsed.get("weaknesses") or ["Add more quantifiable achievements"],
            "missing_skills": parsed.get("missing_skills") or ["System Design", "Cloud Deployment"],
            "interview_questions": parsed.get("interview_questions") or [
                f"Describe your recent experience relative to {target_role}.",
                "How do you handle technical challenges under tight deadlines?",
                "Describe a project where you improved system performance.",
                "How do you prioritize competing work requests?",
                "Tell me about a time you worked with a cross-functional team.",
            ],
            "career_roadmap": parsed.get("career_roadmap") or {
                "thirty_day_plan": ["Refine resume and update online profiles", "Complete targeted skill reviews"],
                "sixty_day_plan": ["Build and showcase a portfolio project", "Practice technical interview questions"],
                "ninety_day_plan": ["Apply actively to target roles", "Conduct informational interviews"],
                "weekly_goals": ["Study key concepts 5 hours/week", "Apply to targeted openings"],
                "resources": ["Industry documentation", "Interactive interview platforms"],
                "projects": ["Build an end-to-end domain project", "Publish code to GitHub"],
            },
            "improvement_suggestions": parsed.get("improvement_suggestions") or parsed.get("recommendations") or [
                "Quantify bullet points with metrics and outcomes.",
                "Align keywords with modern industry job descriptions.",
            ],
            "missing_sections": parsed.get("missing_sections") or ["Certifications section"],
            "grammar_issues": parsed.get("grammar_issues") or ["No major grammar issues detected."],
            "formatting_suggestions": parsed.get("formatting_suggestions") or ["Ensure consistent font sizes and bullet spacing."],
            "professional_summary_review": parsed.get("professional_summary_review") or "Summary presents a solid foundation.",
            "technical_skills_review": parsed.get("technical_skills_review") or "Technical skills are relevant to target roles.",
            "soft_skills_review": parsed.get("soft_skills_review") or "Communication and teamwork demonstrated clearly.",
            "keyword_suggestions": parsed.get("keyword_suggestions") or ["Python", "SQL", "Git", "REST APIs"],
            "recommendations": parsed.get("recommendations") or parsed.get("improvement_suggestions") or [
                "Quantify achievements and match keywords to role descriptions."
            ],
            "ats_details": parsed.get("ats_details") or local_ats,
            "from_cache": False,
        }

        _ANALYSIS_CACHE[cache_key] = result
        return result
    except Exception as exc:
        print(f"[AI Engine] Analysis failed: {exc}")
        raise RuntimeError("Unable to generate AI response. Please try again.") from exc


def analyze_resume(resume_text: str, parsed_resume: dict[str, Any]) -> dict[str, Any]:
    try:
        return analyze_resume_comprehensive(resume_text, parsed_resume)
    except RuntimeError:
        local_ats = calculate_ats_score(parsed_resume)
        msg = "Unable to generate AI response. Please try again."
        return {
            "resume_score": 70,
            "overall_score": 70,
            "ats_score": local_ats.get("overall_score", 70),
            "executive_summary": msg,
            "strengths": ["Resume uploaded successfully."],
            "weaknesses": ["Detailed AI breakdown unavailable."],
            "missing_skills": ["Review job descriptions for missing skills."],
            "interview_questions": [
                "Tell me about a difficult problem you solved recently.",
                "How do you approach learning new technologies quickly?",
                "Describe a project you are particularly proud of.",
            ],
            "career_roadmap": {
                "thirty_day_plan": ["Update resume and portfolio"],
                "sixty_day_plan": ["Practice interview scenarios"],
                "ninety_day_plan": ["Apply to top candidate positions"],
                "weekly_goals": ["Study core engineering topics"],
                "resources": ["Official documentation"],
                "projects": ["Build a key portfolio application"],
            },
            "improvement_suggestions": ["Add measurable metrics to bullet points."],
            "missing_sections": ["Certifications"],
            "grammar_issues": ["None detected."],
            "formatting_suggestions": ["Keep consistent formatting."],
            "professional_summary_review": msg,
            "technical_skills_review": "AI analysis unavailable.",
            "soft_skills_review": "AI analysis unavailable.",
            "keyword_suggestions": ["Python", "SQL"],
            "recommendations": ["Add measurable metrics."],
            "ats_details": local_ats,
            "error_message": msg,
            "from_cache": False,
        }
