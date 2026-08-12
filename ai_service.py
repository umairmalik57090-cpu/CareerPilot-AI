import os
from pathlib import Path

from dotenv import load_dotenv

from groq_client import check_groq_connection, generate_chat_completion

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_ai_provider() -> str:
    return "Groq"


def get_ai_status() -> tuple[bool, str]:
    return check_groq_connection()


def call_model(prompt: str, system_prompt: str = "You are a helpful AI assistant.", **kwargs) -> str:
    return generate_chat_completion(prompt=prompt, system_prompt=system_prompt, **kwargs)


def safe_ai_call(action: str, prompt: str, system_prompt: str = "You are a helpful AI assistant.", **kwargs) -> str:
    try:
        return call_model(prompt, system_prompt=system_prompt, **kwargs)
    except Exception as exc:  # pragma: no cover - runtime safety
        raise RuntimeError(f"{action} failed: {exc}") from exc
