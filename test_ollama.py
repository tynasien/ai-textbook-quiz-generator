
from backend.app.services.ollama_service import (
    check_connection,
    generate_quiz
)

print(check_connection())

result = generate_quiz(
    context="""
    Железо является химическим элементом и относится к металлам.
    Кислород является химическим элементом и относится к неметаллам.
    Медь также относится к металлам.
    """,
    question_count=2,
    difficulty="easy"
)

for question in result["questions"]:
    print("\nВопрос:", question["question"])
    print("Варианты:", question["options"])
    print("Правильный ответ:", question["correct_answer"])
    print("Объяснение:", question["explanation"])
