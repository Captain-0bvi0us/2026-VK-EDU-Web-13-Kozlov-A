"""Общий контекст для сайдбара"""


def sidebar_context(request):
    return {
        "popular_tags": [
            {"name": "perl", "slug": "perl", "size": "sm"},
            {"name": "python", "slug": "python", "size": "lg"},
            {"name": "осень", "slug": "autumn", "size": "warm"},
            {"name": "TechnoPark", "slug": "technopark", "size": "sm"},
            {"name": "MySQL", "slug": "mysql", "size": "lg"},
            {"name": "кофе", "slug": "coffee", "size": "accent"},
            {"name": "django", "slug": "django", "size": "md"},
            {"name": "Mail.Ru", "slug": "mail-ru", "size": "sm"},
        ],
        "best_members": [
            {"name": "Мистер Фримен", "slug": "freeman"},
            {"name": "Доктор Хаус", "slug": "house"},
            {"name": "Бендер", "slug": "bender"},
            {"name": "Королева Виктория", "slug": "victoria"},
            {"name": "В. Пупкин", "slug": "pupkin"},
        ],
    }
