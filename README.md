# 2026-VK-EDU-Web-13-Kozlov-A

Репозиторий курса «WEB-технологии»: Django-приложение **CupOfQ**. Документация ниже ориентирована на **ДЗ3**: модели и админка, PostgreSQL, Docker и `.env`, команда наполнения БД, read-only выдача данных с пагинацией и debug-toolbar.

## Требования

- Python **3.11+** (локально; в Docker по `Dockerfile` используется **Python 3.12**)
- Для полного сценария ДЗ3: **PostgreSQL** (локально или только в Docker)
- Для Docker: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Быстрый старт (локально)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env.local
```

Отредактируйте **`.env.local`**: задайте `DJANGO_SECRET_KEY` и при необходимости параметры Postgres (см. ниже). Файл **`.env.example`** в репозитории — шаблон имён переменных без реальных секретов.

Дальше:

```powershell
python manage.py migrate
python manage.py runserver
```

Откройте в браузере: http://127.0.0.1:8000/

Если **`POSTGRES_DB` не задан или пустой**, используется **SQLite** (файл `db.sqlite3` в корне проекта). Для Postgres с хоста задайте в `.env.local` `POSTGRES_DB`, пользователя, пароль; при занятом порте 5432 на Windows удобно **`POSTGRES_PORT=5433`** (как в `.env.example`).

## Запуск через Docker Compose

1. Создайте **`.env.docker`** по образцу **`.env.example`** (одинаковые `POSTGRES_*` с сервисом `db`).
2. Запустите Docker Desktop, затем из корня репозитория:

```powershell
docker compose up --build -d
```

- Сайт: http://127.0.0.1:8000/
- PostgreSQL с хоста по умолчанию: порт **`5433`** (переменная `POSTGRES_PUBLISH_PORT` в `docker-compose`; внутри сети compose у `web` хост БД — `db`, порт `5432`).
- Каталог проекта смонтирован в контейнер (`./` → `/app`), загрузки в `media/` — в volume **`cupofq_media`**, данные БД — в **`cupofq_pgdata`**.

После изменения **`requirements.txt`** пересоберите веб-образ (и зависимости в контейнере обновятся):

```powershell
docker compose build web
docker compose up -d
```

## Переменные окружения (ДЗ3)

В репозитории лежит **`.env.example`**. В Git не попадают: **`.env`**, **`.env.local`**, **`.env.docker`** (см. `.gitignore`).

- **`DJANGO_SECRET_KEY`** — секрет Django.
- **`DJANGO_DEBUG`** — `true` или `false`; при `true` подключается **django-debug-toolbar** (панель отладки справа). Чтобы её не показывать, поставьте `false`.
- **`DJANGO_ALLOWED_HOSTS`** — хосты через запятую.
- **`POSTGRES_DB`**, **`POSTGRES_USER`**, **`POSTGRES_PASSWORD`**, **`POSTGRES_HOST`**, **`POSTGRES_PORT`** — подключение к БД (в `docker-compose` для сервиса `web` хост/порт к Postgres заданы через `environment`).

Сначала загружается **`.env`**, затем при запуске **не** в Docker (нет `DJANGO_RUN_IN_DOCKER`) поверх подмешивается **`.env.local`**.

## Наполнение базы (ДЗ3)

```powershell
python manage.py fill_db <ratio>
```

Пользователей = `ratio`, вопросов = `ratio * 10`, ответов = `ratio * 100`, тегов = `ratio`, суммарно лайков (вопросы + ответы) = `ratio * 200`. Данные генерирует **Faker**, вставки — **`bulk_create`**. Из-за уникальности пар «пользователь + сущность» для малых `ratio` команда может потребовать **увеличить `ratio`** (для наших формул обычно с **`ratio >= 10`** всё сходится).

Суперпользователь для `/admin/`:

```powershell
python manage.py createsuperuser
```

## Структура проекта

| Путь | Назначение |
|------|------------|
| `application/` | Настройки Django (`settings.py`, корневой `urls.py`); выбор SQLite/Postgres из env; debug-toolbar при `DEBUG` |
| `core/` | Вход, регистрация, профиль, базовый шаблон, общие шаблоны и статика, include пагинации, templatetag `elided_page_numbers` |
| `questions/` | Модели, менеджеры выборок, вьюхи, `utils.paginate`, команда `fill_db` |
| `manage.py` | CLI Django |
| `requirements.txt` | Зависимости Python (секции в файле: ASGI, Django, Faker, Pillow, PostgreSQL, dotenv, SQL, tzdata, django-debug-toolbar) |
| `Dockerfile`, `docker-compose.yml` | Образ приложения и сервисы `db` + `web` |

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

Данные на страницах вопросов — из **базы**. Пагинация: **`questions.utils.paginate`** (номер страницы вне диапазона — **404**). Компактный ряд номеров в шаблоне — фильтр **`elided_page_numbers`** в `core/templatetags/pagination_tags`.

### Статика

Файлы Bootstrap и стили CupOfQ лежат в `core/static/core/`. В шаблонах используется `{% static %}`. Каталоги `/static/` и `/media/` в **корне** репозитория в `.gitignore` (собранная статика и загрузки).

## Архив

**ДЗ2** — перенос готовой вёрстки в шаблоны Django, базовый каркас приложений `core` и `questions`, именованные URL, страницы списков и вопроса на заглушках, функция пагинации, первичный Docker Compose.

**ДЗ1** — исходная статическая вёрстка; затем она была перенесена в шаблоны Django, отдельная папка `public/` удалена.
