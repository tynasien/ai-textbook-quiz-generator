import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Загружаем настройки из .env в корне проекта
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


def get_client() -> OpenAI:
    """Создаёт клиент OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "API-ключ не найден. Проверь файл .env в корне проекта."
        )

    return OpenAI(api_key=api_key)


def check_api_connection() -> str:
    """Проверяет, отвечает ли языковая модель."""
    client = get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.responses.create(
        model=model,
        input="Ответь одним словом: работает."
    )

    return response.output_text.strip()


def generate_quiz(
    context: str,
    question_count: int = 5,
    difficulty: str = "medium",
) -> dict:
    """Генерирует тестовые вопросы на основе текста учебника."""
    if not context.strip():
        raise ValueError("Текст учебника не должен быть пустым.")

    if not 1 <= question_count <= 20:
        raise ValueError("Количество вопросов должно быть от 1 до 20.")

    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError(
            "Сложность должна быть easy, medium или hard."
        )

    client = get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = f"""
Ты — помощник для создания учебных тестов.

Создай ровно {question_count} тестовых вопросов
по предоставленному тексту.

Сложность: {difficulty}.

Правила:
1. Используй только информацию из предоставленного текста.
2. Не придумывай факты, которых нет в тексте.
3. У каждого вопроса должно быть ровно 4 варианта ответа.
4. Только один вариант ответа должен быть правильным.
5. Добавь короткое объяснение правильного ответа.
6. Все вопросы и ответы пиши на русском языке.
7. Не добавляй Markdown и текст вне JSON.

Верни JSON следующего формата:
{{
  "questions": [
    {{
      "question": "Текст вопроса",
      "options": [
        "Вариант A",
        "Вариант B",
        "Вариант C",
        "Вариант D"
      ],
      "correct_answer": "Точный текст правильного варианта",
      "explanation": "Объяснение ответа"
    }}
  ]
}}

Текст учебника:
<context>
{context}
</context>
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты создаёшь точные учебные тесты. "
                    "Используй только предоставленный источник."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Модель вернула пустой ответ.")

    result = json.loads(content)
    questions = result.get("questions")

    if not isinstance(questions, list) or len(questions) != question_count:
        raise ValueError("Модель вернула некорректное количество вопросов.")

    for question in questions:
        options = question.get("options", [])
        if (
            not isinstance(options, list)
            or len(options) != 4
            or question.get("correct_answer") not in options
            or not question.get("question")
            or not question.get("explanation")
        ):
            raise ValueError(
                "Модель вернула вопрос с некорректной структурой."
            )

    return result