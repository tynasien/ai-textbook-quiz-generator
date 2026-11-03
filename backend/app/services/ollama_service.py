
import json
import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def check_connection() -> str:
    """Проверяет подключение к Ollama."""
    try:
        response = httpx.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        available = [model["name"] for model in models]

        if not any(OLLAMA_MODEL in name for name in available):
            raise ValueError(
                f"Модель {OLLAMA_MODEL} не найдена. "
                "Сначала загрузите её через ollama pull."
            )

        return f"Ollama подключена. Модель: {OLLAMA_MODEL}"

    except httpx.HTTPError as error:
        raise ValueError(f"Не удалось подключиться к Ollama: {error}")


def generate_quiz(
    context: str,
    question_count: int = 5,
    difficulty: str = "medium"
) -> dict:
    """Генерирует тест по тексту учебника через Ollama."""

    if not context.strip():
        raise ValueError("Текст учебника не должен быть пустым.")

    if not 1 <= question_count <= 20:
        raise ValueError("Количество вопросов должно быть от 1 до 20.")

    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Некорректная сложность теста.")

    prompt = f"""
Создай ровно {question_count} тестовых вопросов по тексту учебника.

Сложность: {difficulty}.

Правила:
1. Используй только информацию из текста.
2. Не придумывай факты.
3. Каждый вопрос должен иметь ровно 4 варианта ответа.
4. Только один вариант должен быть правильным.
5. Правильный ответ должен дословно совпадать с одним из вариантов.
6. Добавь короткое объяснение.
7. Пиши на русском языке.
8. Не добавляй Markdown.

Верни только JSON:
{{
  "questions": [
    {{
      "question": "Вопрос",
      "options": ["Ответ 1", "Ответ 2", "Ответ 3", "Ответ 4"],
      "correct_answer": "Ответ 1",
      "explanation": "Объяснение"
    }}
  ]
}}

Текст учебника:
<context>
{context}
</context>
"""

    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты создаёшь точные учебные тесты."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=180
        )
        response.raise_for_status()

        content = response.json()["message"]["content"]
        result = json.loads(content)

        questions = result.get("questions")

        if not isinstance(questions, list) or len(questions) != question_count:
            raise ValueError("Модель вернула неправильное количество вопросов.")

        for question in questions:
            options = question.get("options", [])

            if (
                not isinstance(options, list)
                or len(options) != 4
                or question.get("correct_answer") not in options
                or not question.get("question")
                or not question.get("explanation")
            ):
                raise ValueError("Модель вернула некорректный вопрос.")

        return result

    except httpx.HTTPError as error:
        raise ValueError(f"Ошибка запроса к Ollama: {error}")
    except (KeyError, json.JSONDecodeError):
        raise ValueError("Ollama вернула некорректный JSON.")
