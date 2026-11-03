
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY не найден в .env")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


def check_connection():
    client = get_client()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Ответь одним словом: работает."}
        ],
        temperature=0
    )

    return response.choices[0].message.content


def generate_text(prompt: str) -> str:
    client = get_client()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Ты создаёшь точные учебные тесты по предоставленному источнику."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq вернул пустой ответ.")

    return content
