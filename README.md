# 2026-VK-EDU-Web-13-Kozlov-A

Репозиторий курса «WEB-технологии»: Django-приложение **CupOfQ** — вопросы и ответы с авторизацией, профилем, голосованием, realtime-обновлениями, фоновыми задачами и полнотекстовым поиском. **Ниже описана реализация ДЗ6**; предыдущие этапы — **в конце, в разделе «Архив»**.

## Домашнее задание 6

### Redis + Celery + Celerybeat

- **Redis** — брокер Celery, cache backend Django и хранилище расписания RedBeat; отдельные DB: cache **1**, broker **2**, beat **3** (`application/settings.py`, `.env.example`).
- **Celery** — `application/celery.py`, автозагрузка задач из приложений; worker и beat в `docker-compose.yml`.
- **Периодические задачи** — расписание в `CELERY_BEAT_SCHEDULE` (`settings.py`): пересчёт популярных тегов и лучших участников каждые 10 минут.

### Кеширование сайдбара (`core/`)

- **Популярные теги** — 10 тегов с наибольшим числом вопросов за **3 месяца** (`core/tasks.py:recompute_popular_tags`).
- **Лучшие участники** — 10 пользователей с наибольшей суммой голосов за вопросы и ответы за **7 дней** (`core/tasks.recompute_best_members`).
- **Чтение данных** — `core/sidebar_context.py`: сначала Redis-кэш (`core/cache_keys.py`), при miss — пересчёт из БД и запись в кэш.
- **Вывод** — правая колонка в `core/templates/core/includes/sidebar.html`.

### Real-time через Centrifugo (`questions/` + `core/`)

- **Сервер** — сервис `centrifugo` в Docker, конфиг `centrifugo/config.json`, namespace `questions`.
- **Connection-token** — `GET /api/centrifugo/token/?question_id=<id>` (`core/views.centrifugo_token_view`); канал в claim `subs` JWT, без subscription-token.
- **Публикация** — celery-таска `questions/tasks.publish_new_answer` (HTTP API Centrifugo из `core/centrifugo.py`), вызывается из `question_detail` после сохранения ответа.
- **Клиент** — `core/static/core/js/question_realtime.js` + Centrifuge SDK на странице вопроса:
  - ответов не было → первый ответ появляется в списке без перезагрузки;
  - пользователь на странице, куда попадает новый ответ (`per_page=3`) → ответ добавляется в DOM;
  - пользователь на другой странице → `window.alert` (без вставки в текущий список); автор только что отправленного ответа alert не получает.

### Email-уведомления

- **SMTP** — настройки `EMAIL_*` в `settings.py` из env; в Docker — сервис **maildev** (SMTP `:1025`, веб-интерфейс `:1080`).
- **Отправка** — celery-таска `core/tasks.send_new_answer_email`: письмо автору вопроса при новом ответе (если указан email и ответ не от самого автора).

### Полнотекстовый поиск (`questions/`)

- **Индекс** — поле `Question.search_vector` (PostgreSQL `tsvector` + GIN), миграция `0003_question_search_vector.py`; пересчёт в `Question.save()`.
- **API** — `GET /api/search/suggest/?q=...` (`questions/views.search_suggest`): `SearchQuery` + `SearchRank` по заголовку и тексту (конфиг `russian`).
- **Подсказки** — `core/static/core/js/search_suggest.js`: debounce 250 мс, выпадающий список под полем в шапке (`core/templates/core/includes/header.html`).

## Требования к окружению

- Python **3.11+** (локально; в Docker по `Dockerfile` — **Python 3.12**).
- **PostgreSQL** — для полнотекстового поиска и Docker-стека (рекомендуется).
- **Redis** — для кэша и Celery (в Docker — сервис `redis`).
- Docker: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Быстрый старт (локально)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env.local
```

Отредактируйте **`.env.local`**: `DJANGO_SECRET_KEY`, Postgres, Redis, Centrifugo, SMTP. Шаблон — **`.env.example`**.

Для полного ДЗ6 локально нужны **Postgres**, **Redis**, **Centrifugo** и **SMTP** (или maildev). Celery worker и beat запускаются отдельно:

```powershell
python manage.py migrate
celery -A application worker -l info
celery -A application beat -l info -S redbeat.RedBeatScheduler
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Если **`POSTGRES_DB` не задан**, используется **SQLite** — полнотекстовый поиск переключится на fallback `icontains`.

## Запуск через Docker Compose

1. Создайте **`.env.docker`** по образцу **`.env.example`** (согласованные `POSTGRES_*`, `CENTRIFUGO_*` и т.д.).
2. Запустите Docker Desktop, затем из корня репозитория:

```powershell
docker compose up --build -d
```

| Сервис | URL / порт с хоста |
|--------|---------------------|
| Сайт | http://127.0.0.1:8000/ |
| PostgreSQL | `localhost:5433` |
| Redis | `localhost:6379` |
| Centrifugo WS | `ws://localhost:8001/connection/websocket` |
| Maildev (письма) | http://127.0.0.1:1080/ |

Сервисы: `web`, `db`, `redis`, `centrifugo`, `maildev`, `celery_worker`, `celery_beat`.

После изменения **`requirements.txt`** или Dockerfile:

```powershell
docker compose build web celery_worker celery_beat
docker compose up -d
```

После изменения Python-кода в celery-тасках перезапустите worker:

```powershell
docker compose restart celery_worker celery_beat
```

## Переменные окружения

В репозитории: **`.env.example`**. В Git не попадают: **`.env`**, **`.env.local`**, **`.env.docker`**.

- **Django**: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
- **Postgres**: `POSTGRES_*`
- **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_CACHE_DB`, `REDIS_BROKER_DB`, `REDIS_BEAT_DB`
- **Centrifugo**: `CENTRIFUGO_API_URL`, `CENTRIFUGO_API_KEY`, `CENTRIFUGO_HMAC_SECRET_KEY`, `CENTRIFUGO_WS_URL`, `CENTRIFUGO_NAMESPACE`
- **Email**: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`

Сначала загружается **`.env`**, затем при запуске **не** в Docker поверх подмешивается **`.env.local`**.

## Наполнение базы

```powershell
python manage.py fill_db <ratio>
```

Пользователи = `ratio`, вопросы = `ratio * 10`, ответы = `ratio * 100`, теги = `ratio`, голоса ≈ `ratio * 200`. Даты в `fill_db` сдвинуты так, чтобы сайдбар (теги за 3 месяца, рейтинг за неделю) показывал данные после генерации. Для малых `ratio` может понадобиться **`ratio >= 10`**.

```powershell
python manage.py createsuperuser
```

## Проверка ДЗ6

1. **Сайдбар** — после `fill_db` и ожидания beat (или ручного `recompute_*` в shell) в правой колонке есть теги и участники.
2. **Realtime** — две вкладки на `/question/<id>/`; на второй вкладке новый ответ появляется без F5; на `?page=2` — alert.
3. **Email** — у автора вопроса указан email в профиле; после ответа письмо в http://127.0.0.1:1080/.
4. **Поиск** — ввод в шапке (от 2 символов), подсказки с debounce.

## Структура проекта

| Путь | Назначение |
|------|------------|
| `application/` | `settings.py`, `celery.py`, корневой `urls.py` |
| `core/` | auth, профиль, сайдбар, Centrifugo token, celery-таски кэша и email |
| `questions/` | модели, вьюхи, realtime publish, поиск, `fill_db` |
| `centrifugo/` | конфиг Centrifugo |
| `docker-compose.yml` | db, redis, web, celery, centrifugo, maildev |

### Маршруты (именованные)

| URL | Имя | Примечание |
|-----|-----|------------|
| `/` | `index` | |
| `/hot/` | `hot` | |
| `/tag/…/` | `tag` | |
| `/question/…/` | `question_detail` | realtime JS |
| `/ask/` | `ask` | |
| `/question/…/vote/` | `question_vote` | POST, AJAX JSON |
| `/answer/…/vote/` | `answer_vote` | POST, AJAX JSON |
| `/answer/…/correct/` | `mark_answer_correct` | POST, AJAX JSON |
| `/api/search/suggest/` | `search_suggest` | GET, подсказки |
| `/api/centrifugo/token/` | `centrifugo_token` | GET, WS-токен |
| `/login/`, `/signup/`, `/profile/`, `/logout/` | | |
| `/user/<username>/` | `public_user` | |
| `/admin/` | | админка Django |

Списки и ответы на странице вопроса — из БД; пагинация ответов **`per_page=3`** (`questions.presentation.paginate`).

### Статика

В `core/static/core/`: **`cupofq.js`** (голоса, верный ответ), **`question_realtime.js`**, **`search_suggest.js`**. jQuery и Centrifuge — CDN в шаблонах.

---

**Запуск:** при `DEBUG=true` нужен **django-debug-toolbar** из `requirements.txt`. Для Postgres — **psycopg**; без `POSTGRES_DB` — SQLite (поиск через `icontains`).

## Архив

**ДЗ5**: загрузка и отображение **аватаров** (`ImageField`, валидация расширения/размера, `upload_to` с UUID); **лайки/дизлайки** вопросов и ответов через **AJAX** (`cupofq.js`, CSRF, `JsonResponse` с `score`/`vote`); **отметка верного ответа** автором вопроса (POST + reload); рейтинг через подзапрос `Sum(value)` без искажений при JOIN.

**ДЗ4**: авторизация (логин с **`next`**, регистрация, выход), профиль и **`/user/<username>/`**; ModelForm для вопроса и ответа, теги get-or-create, PRG и CSRF; первичное голосование POST + redirect.

**ДЗ3**: модели и админка; PostgreSQL / SQLite; Docker Compose; **`fill_db`**; списки вопросов и пагинация; debug-toolbar при **`DEBUG`**.

**ДЗ2** — перенос вёрстки в шаблоны Django, каркас `core` и `questions`, именованные URL, Docker Compose.

**ДЗ1** — статическая вёрстка; затем перенос в Django.
