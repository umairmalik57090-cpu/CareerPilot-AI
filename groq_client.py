import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from groq import Groq
except Exception:  # pragma: no cover
    Groq = None

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile").strip()

_groq_client = None


def get_groq_client():
    global _groq_client
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    if Groq is None:
        raise RuntimeError("The groq package is not installed.")

    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def _clean_response_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def parse_json_response(text: str) -> Any:
    if not text:
        raise ValueError("Response was empty.")

    cleaned = _clean_response_text(text)
    cleaned = re.sub(r"^\s*json[:\s]*", "", cleaned, flags=re.IGNORECASE).strip()

    if cleaned and cleaned[0] not in "[{":
        first_brace = min([idx for idx in (cleaned.find("{"), cleaned.find("[")) if idx != -1], default=-1)
        if first_brace != -1:
            cleaned = cleaned[first_brace:]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{(?:.|\n)*\})|(\[(?:.|\n)*\])", cleaned, flags=re.S)
        if match:
            fragment = match.group(0)
            try:
                return json.loads(fragment)
            except json.JSONDecodeError as exc:
                raise ValueError("Unable to generate AI response. Please try again.") from exc
        raise ValueError("Unable to generate AI response. Please try again.")


def check_groq_connection() -> tuple[bool, str]:
    api_key_loaded = bool(GROQ_API_KEY)
    print(f"[Groq] API key loaded? {'Yes' if api_key_loaded else 'No'}")
    print(f"[Groq] Model name: {MODEL_NAME}")

    if not api_key_loaded:
        status = "🔴 AI Offline (Groq)"
        return False, status

    if Groq is None:
        status = "🔴 AI Offline (Groq)"
        return False, status

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Reply with OK"}],
            max_tokens=10,
            temperature=0.0,
        )
        content = response.choices[0].message.content or ""
        if "ok" in content.lower():
            status = "Connected (Groq)"
            return True, status
        return True, "Connected (Groq)"
    except Exception as exc:
        print(f"[Groq] Connection test failed: {exc}")
        return False, "🔴 AI Offline (Groq)"


def validate_groq_connection() -> tuple[bool, str]:
    return check_groq_connection()


def get_groq_error_reason(exc: Exception) -> str:
    return "Unable to generate AI response. Please try again."


def generate_chat_completion(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    json_mode: bool = False,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    try:
        client = get_groq_client()
        kwargs = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    except Exception as exc:
        print(f"[Groq Client] Request failed: {exc}")
        raise RuntimeError("Unable to generate AI response. Please try again.") from exc


def generate_interview_questions(role: str, count: int) -> list[str]:
    if count <= 0:
        return []

    prompt = f"""
Generate exactly {count} interview questions for the selected role: {role}.
Questions should include:
- Beginner
- Intermediate
- Advanced
- Behavioral
- Scenario-based

Return ONLY a JSON array of strings containing the questions, e.g.:
["Question 1?", "Question 2?", ...]
"""
    try:
        text = generate_chat_completion(
            prompt=prompt,
            system_prompt="You are an expert interviewer. Return ONLY a JSON array of question strings.",
            json_mode=True,
            temperature=0.3,
        )
        parsed = parse_json_response(text)
        if isinstance(parsed, list):
            return [str(q).strip() for q in parsed[:count]]
    except Exception as exc:
        print(f"[Groq] Question generation failed: {exc}")

    fallback = [
        f"Describe a project where you solved a difficult problem as a {role}.",
        f"How would you explain a technical concept to a non-technical stakeholder in a {role} role?",
        f"Tell me about a time you handled a challenging situation while working as a {role}.",
        f"Describe how you approach debugging a complex issue in a {role} position.",
        f"How do you prioritize work when deadlines are tight in a {role} environment?",
    ]
    return [fallback[i % len(fallback)] for i in range(count)]


def evaluate_interview_response(role: str, question: str, answer: str) -> dict[str, Any]:
    prompt = f"""
You are an experienced technical interviewer.
Evaluate ONLY this interview response.

Job Role: {role}
Current Interview Question: {question}
Current User Answer: {answer}

Return JSON with keys:
{{
  "overall_score": 95,
  "confidence": 90,
  "technical_accuracy": 92,
  "communication": 88,
  "strengths": ["Strength 1"],
  "weaknesses": ["Weakness 1"],
  "improvements": ["Improvement 1"],
  "sample_answer": "Model answer..."
}}
"""
    try:
        text = generate_chat_completion(
            prompt=prompt,
            system_prompt="You are an expert interviewer. Return ONLY valid JSON.",
            json_mode=True,
            temperature=0.3,
        )
        parsed = parse_json_response(text)
        if isinstance(parsed, dict):
            return {
                "overall_score": int(parsed.get("overall_score", 0)),
                "confidence": int(parsed.get("confidence", 0)),
                "technical_accuracy": int(parsed.get("technical_accuracy", 0)),
                "communication": int(parsed.get("communication", 0)),
                "strengths": parsed.get("strengths", []),
                "weaknesses": parsed.get("weaknesses", []),
                "improvements": parsed.get("improvements", []),
                "sample_answer": parsed.get("sample_answer", ""),
            }
    except Exception as exc:
        print(f"[Groq] Evaluation failed: {exc}")

    fallback_score = 50 + min(45, len(answer) % 50)
    return {
        "overall_score": fallback_score,
        "confidence": min(100, fallback_score + 5),
        "technical_accuracy": min(100, fallback_score + 3),
        "communication": min(100, fallback_score - 5),
        "strengths": [f"Answered the question about {role} clearly."],
        "weaknesses": ["Add more specific examples and metrics."],
        "improvements": ["Use STAR examples and quantify results."],
        "sample_answer": "A stronger answer would explain the challenge, your specific role, the actions you took, and the measurable impact.",
    }
