# 2026-VK-EDU-Web-13-Kozlov-A

Репозиторий курса «WEB-технологии»: Django-приложение **CupOfQ** — вопросы и ответы с авторизацией, профилем, формами добавления контента, лайками и отметкой верного ответа. **Ниже в описана реализация ДЗ4**; предыдущие этапы курса — **кратко в конце, в разделе «Архив»**.

## Домашнее задание 4

### Авторизация и профиль (`core/`)

- **Логин** (`/login/`, `LoginForm`): POST, CSRF, ошибки и сохранение введённого логина; параметр **`next`** в GET/POST и скрытое поле в шаблоне; после успеха — редирект через **`core.auth_utils.get_safe_redirect_url`** (`url_has_allowed_host_and_scheme`, защита от open redirect).
- **Регистрация** (`/signup/`, `SignupForm`): создание пользователя; **`Profile`** создаётся сигналом `post_save`; пароль — **`validate_password`** и **`AUTH_PASSWORD_VALIDATORS`** в `application/settings.py`; опциональный аватар с промежуточным сохранением в storage при ошибках валидации (`signup_staging.py`).
- **Выход**: POST в шапке, **`logout_view`**; редирект по **`HTTP_REFERER`** с той же проверкой безопасности, иначе на главную.
- **Профиль** (`/profile/`, `@login_required`, `ProfileEditForm`): email, имя, фамилия, загрузка и удаление аватара в **`save()`** формы; после успешного POST — редирект на `profile` (PRG).
- **Имя в интерфейсе**: при пустом ФИО показывается логин (`core.utils.user_display_name`).
- **Публичная страница** `/user/<username>/` — карточка участника (в шапке/сайдбаре ссылки на активных авторов).

### Вопросы и ответы (`questions/`)

- **`/ask/`** (`@login_required`, `QuestionForm`, **ModelForm**): заголовок, текст, теги через `tags_input`; теги **get-or-create** в **`save()`**; редирект на созданный вопрос.
- **Страница вопроса** `/question/<id>/`: `AnswerForm` (**ModelForm**); гость при POST уходит на логин с `next`; после ответа — редирект на страницу пагинации ответов и **якорь** `#answer-<id>`.
- **Лайки**: POST `question_vote` / `answer_vote`; признак «лайкнул ли зритель» — аннотации в **`like_annotations.py`**; «вниз» снимает лайк (счёт не уходит в минус).
- **Верный ответ**: только автор вопроса, POST `mark_answer_correct`; у остальных ответов этого вопроса снимается флаг.

### Требования к формам (п. 6 методички)

- Валидация и вывод ошибок в формах; отправка **POST** и **CSRF**; после успеха — **редирект**; логика **`clean*` / `save()`** в формах; для гостей недоступные действия — disabled и подсказки («Войдите, чтобы…»).

## Требования к окружению

- Python **3.11+** (локально; в Docker по `Dockerfile` — **Python 3.12**).
- **PostgreSQL** — если подключаетесь к БД по переменным из `.env` (локально или в Docker).
- Docker: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Быстрый старт (локально)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env.local
```

Отредактируйте **`.env.local`**: задайте `DJANGO_SECRET_KEY` и при необходимости параметры Postgres. Шаблон переменных — **`.env.example`**.

```powershell
python manage.py migrate
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Если **`POSTGRES_DB` не задан или пустой**, используется **SQLite** (`db.sqlite3`). Для Postgres с хоста задайте в `.env.local` учётные данные; при занятом порте 5432 на Windows удобно **`POSTGRES_PORT=5433`** (как в `.env.example`).

## Запуск через Docker Compose

1. Создайте **`.env.docker`** по образцу **`.env.example`** (согласованные `POSTGRES_*` с сервисом `db`).
2. Запустите Docker Desktop, затем из корня репозитория:

```powershell
docker compose up --build -d
```

- Сайт: http://127.0.0.1:8000/
- PostgreSQL с хоста: порт **`5433`** (`POSTGRES_PUBLISH_PORT` в `docker-compose`; внутри сети у `web` хост БД — `db`, порт `5432`).
- Проект в контейнере: `./` → `/app`; загрузки в **`cupofq_media`**, данные БД — **`cupofq_pgdata`**.

После изменения **`requirements.txt`**:

```powershell
docker compose build web
docker compose up -d
```

## Переменные окружения

В репозитории: **`.env.example`**. В Git не попадают: **`.env`**, **`.env.local`**, **`.env.docker`** (`.gitignore`).

- **`DJANGO_SECRET_KEY`**, **`DJANGO_DEBUG`**, **`DJANGO_ALLOWED_HOSTS`**
- при **`DJANGO_DEBUG=true`** подключается **django-debug-toolbar** (нужен пакет из `requirements.txt`)
- **`POSTGRES_*`** — подключение к БД (в compose для `web` задаётся через `environment`)

Сначала загружается **`.env`**, затем при запуске **не** в Docker поверх подмешивается **`.env.local`**.

## Наполнение базы

```powershell
python manage.py fill_db <ratio>
```

Пользователи = `ratio`, вопросы = `ratio * 10`, ответы = `ratio * 100`, теги = `ratio`, лайки ≈ `ratio * 200`. Генерация — **Faker**, массовые вставки — **`bulk_create`**; для малых `ratio` из‑за уникальности связей может понадобиться **`ratio >= 10`**.

```powershell
python manage.py createsuperuser
```

## Структура проекта

| Путь | Назначение |
|------|------------|
| `application/` | `settings.py`, корневой `urls.py`; SQLite/Postgres из env; debug-toolbar при `DEBUG` |
| `core/` | Логин, регистрация, профиль, logout; `/user/<username>/`; `auth_utils`, `sidebar_context`, сигнал `Profile`; шаблоны и статика; templatetag пагинации |
| `questions/` | Модели и лайки, вьюхи списков и вопроса, ask/answer, голосование и верный ответ; `presentation` (в т.ч. пагинация списков), `like_annotations`; `fill_db` |
| `manage.py`, `requirements.txt`, Docker-файлы | см. корень репозитория |

### Маршруты (именованные)

| URL | Имя в шаблонах `{% url %}` |
|-----|----------------------------|
| `/` | `index` |
| `/hot/` | `hot` |
| `/tag/…/` | `tag` (аргумент `tag`) |
| `/question/…/` | `question_detail` (аргумент `pk`) |
| `/ask/` | `ask` |
| `/question/…/vote/` | `question_vote` (POST) |
| `/answer/…/vote/` | `answer_vote` (POST) |
| `/answer/…/correct/` | `mark_answer_correct` (POST, автор вопроса) |
| `/logout/` | `logout` (POST) |
| `/user/<username>/` | `public_user` |
| `/login/` | `login` |
| `/signup/` | `signup` |
| `/profile/` | `profile` |
| `/layout/` | `layout` (демо каркаса) |
| `/admin/` | админка Django |

Списки вопросов и ответы на странице вопроса читаются из БД; пагинация — **`questions.presentation.paginate`** (лишний номер страницы — **404**); компактные номера страниц — **`elided_page_numbers`** в `core/templatetags/pagination_tags`.

### Статика

В `core/static/core/`. В шаблонах — `{% static %}`. `/static/` и `/media/` в корне в `.gitignore`.

---

**Запуск:** при `DEBUG=true` установите зависимости из **`requirements.txt`** (в т.ч. toolbar). Для Postgres в `.env` нужен **psycopg** из `requirements.txt`; без `POSTGRES_DB` — SQLite.

## Архив

**ДЗ3** (кратко): модели данных и админка; выбор **PostgreSQL / SQLite** и **Docker Compose**; команда **`fill_db`**; выдача списков вопросов и страницы вопроса с **пагинацией**; при **`DEBUG`** — **django-debug-toolbar**. Подробности запуска и переменных — в разделах выше (они нужны и для ДЗ4).

**ДЗ2** — перенос вёрстки в шаблоны Django, каркас `core` и `questions`, именованные URL, списки и страница вопроса на заглушках, первый Docker Compose.

**ДЗ1** — статическая вёрстка; затем перенос в Django, папка `public/` удалена.
