"""Данные-заглушки для вьюх (ДЗ2)."""

VOTE_CYCLE = ("up", "down", "none")


def build_questions(count: int = 30):
    questions = []
    for i in range(1, count + 1):
        questions.append(
            {
                "id": i,
                "title": "Как построить лунный парк?" if i == 1 else f"Вопрос №{i}: !демка!",
                "text": "Ребят, не могу разобраться. Накидайте вариантов. С чего начать?"
                if i <= 1
                else f"Краткое описание вопроса номер {i}.",
                "answer_count": (i % 7) + 1,
                "created": f"{(i % 28) + 1} марта 2026, {10 + (i % 12):02d}:20",
                "tags": [
                    {"name": "блэкджек", "slug": "blackjack"},
                    {"name": "bender", "slug": "bender"},
                ]
                if i % 2 == 0
                else [{"name": "django", "slug": "django"}],
                "score": (i % 11) - 3,
                "vote_state": VOTE_CYCLE[i % 3],
            }
        )
    return questions


def build_answers(question_id: int, count: int = 18):
    answers = []
    for j in range(1, count + 1):
        answers.append(
            {
                "id": j,
                "text": (
                    "Прежде всего спасибо за вопрос. Начните с полета на Луну и проектирования парка."
                    if j == 1
                    else f"Ответ номер {j}: Пример карточки с ответом."
                ),
                "author": "Мистер Фримен" if j % 2 else "Доктор Хаус",
                "created": f"3 марта 2026, {14 + j % 10}:00",
                "score": 5 - (j % 4),
                "vote_state": VOTE_CYCLE[j % 3],
                "is_correct": j == 1,
            }
        )
    return answers
