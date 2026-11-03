
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY не найден в .env")

    return genai.Client(api_key=api_key)


def check_connection():
    client = get_client()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    response = client.models.generate_content(
        model=model,
        contents="Ответь одним словом: работает."
    )

    if not response.text:
        raise ValueError("Gemini вернул пустой ответ.")

    return response.text.strip()


def generate_text(prompt: str) -> str:
    client = get_client()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    )

    if not response.text:
        raise ValueError("Gemini вернул пустой ответ.")

    return response.text
