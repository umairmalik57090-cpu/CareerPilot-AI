from typing import Any

from groq_client import evaluate_interview_response, generate_interview_questions as groq_questions


def generate_interview_questions(role: str, count: int = 10) -> list[str]:
    return groq_questions(role, count)


def evaluate_answer(role: str, question: str, answer: str) -> dict[str, Any]:
    feedback = evaluate_interview_response(role, question, answer)
    return {
        "confidence_score": feedback.get("confidence", 0),
        "technical_accuracy": feedback.get("technical_accuracy", 0),
        "communication": feedback.get("communication", 0),
        "strengths": feedback.get("strengths", []),
        "weaknesses": feedback.get("weaknesses", []),
        "improved_answer": feedback.get("sample_answer", ""),
    }
