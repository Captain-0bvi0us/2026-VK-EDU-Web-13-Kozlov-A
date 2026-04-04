# 2026-VK-EDU-Web-13-Kozlov-A

Репозиторий курса «WEB-технологии»: Django-приложение CupOfQ (ДЗ2).

## Требования

- Python 3.11+
- Для Docker: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Быстрый старт (локально)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Откройте в браузере: http://127.0.0.1:8000/

## Запуск через Docker Compose

Запустите Docker Desktop, затем из корня репозитория:

```powershell
docker compose up --build
```

Сайт: http://127.0.0.1:8000/ — каталог проекта смонтирован в контейнер (`./` → `/app`), загрузки в `media/` хранятся в volume `cupofq_media`.

## Переменные окружения (ДЗ2)

По заданию в репозитории есть **`.env.example`** (шаблон имён и заглушек), а локально создаётся **`.env`** (в Git не попадает).

1. Скопируйте шаблон: `copy .env.example .env` (PowerShell) или вручную.
2. При необходимости отредактируйте значения. Для учебного запуска достаточно содержимого из примера.

## Структура проекта (ДЗ2)

| Путь | Назначение |
|------|------------|
| `application/` | Настройки Django (`settings.py`, корневой `urls.py`) |
| `core/` | Вход, регистрация, профиль, страница «базовый шаблон», общие шаблоны и статика |
| `questions/` | Главная, горячее, тег, страница вопроса, форма «задать вопрос» |
| `manage.py` | CLI Django |
| `requirements.txt` | Зависимости Python |
| `Dockerfile`, `docker-compose.yml` | Контейнеризация |

### Маршруты (именованные)

| URL | Имя в шаблонах `{% url %}` |
|-----|----------------------------|
| `/` | `index` |
| `/hot/` | `hot` |
| `/tag/…/` | `tag` (аргумент `tag`) |
| `/question/…/` | `question_detail` (аргумент `pk`) |
| `/ask/` | `ask` |
| `/login/` | `login` |
| `/signup/` | `signup` |
| `/profile/` | `profile` |
| `/layout/` | `layout` (демо каркаса и ссылок) |
| `/admin/` | стандартная админка Django |

Данные на страницах — **заглушки**; пагинация вынесена в `questions.utils.paginate` (обработка `PageNotAnInteger` и `EmptyPage`).

### Статика

Файлы Bootstrap и стили CupOfQ лежат в `core/static/core/`. В шаблонах используется `{% static %}`. Каталоги `/static/` и `/media/` в **корне** репозитория в `.gitignore` (собранная статика и загрузки).

## ДЗ1 (архив)

Исходная статическая вёрстка была перенесена в шаблоны Django; отдельная папка `public/` удалена. 
