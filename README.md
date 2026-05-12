# 2026-VK-EDU-Web-13-Kozlov-A



Репозиторий курса «WEB-технологии»: Django-приложение **CupOfQ** — вопросы и ответы с авторизацией, профилем, формами, голосованием (лайк/дизлайк) и отметкой верного ответа. **Ниже описана реализация ДЗ5**; предыдущие этапы — **в конце, в разделе «Архив»**.



## Домашнее задание 5



### Загрузка и отображение аватарок (`core/`)



- **Модель и форма**: **`ImageField`** в профиле, **`django.forms.ImageField`** в **`ProfileEditForm`**; файлы в **`MEDIA_ROOT`**, URL из **`MEDIA_URL`** и шаблонов.

- **Валидация на бэкенде**: допустимые расширения и ограничение размера файла; ошибки показываются пользователю.

- **Имена файлов**: непредсказуемые пути через **`upload_to`** (и при необходимости уникальные имена).

- **Интерфейс**: ссылки на **`/media`** и **`/static`** из настроек; корректное отображение при отсутствии аватара (заглушка или пусто).



### Лайки и дизлайки вопросов и ответов (AJAX, `questions/` + статика)



- **Голос**: у каждой пары (пользователь, вопрос или ответ) одна запись с **`value` +1 или −1**; **рейтинг** = сумма голосов (допускаются **отрицательные** значения).

- **Запрос**: **POST** на `question_vote` / `answer_vote`, параметр **`action`**: `up` / `down`; переключение и снятие голоса по тем же правилам, что на типичных Q&A.

- **Ответ сервера**: **`JsonResponse`** — успех: `ok`, **`score`**, **`vote`** (−1 / 0 / +1); ошибки: авторизация, свой контент, неверный `action` и т.д.

- **Клиент**: **jQuery** (`$.ajax`), общий скрипт **`core/static/core/js/cupofq.js`**; в каждый запрос — **CSRF** (заголовок **`X-CSRFToken`**, токен из cookie **`csrftoken`**). При **401** — редирект на страницу входа с **`next`**.

- **Интерфейс**: кнопки недоступны автору своего вопроса/ответа и гостю; подсветка **`is-up` / `is-down`** по аннотации **`viewer_vote`** в **`like_annotations.py`**; отрицательный счёт визуально выделен (**`text-danger`**).



### Отметка правильного ответа (AJAX)



- **POST** на **`mark_answer_correct`**: только **автор вопроса**; снимается флаг с остальных ответов этого вопроса, выбранный помечается верным.

- **Ответ**: JSON с признаком успеха и идентификаторами; после успеха страница **перезагружается**, чтобы без дублирования логики обновить блоки со всех ответов.



### Технические детали рейтинга



- Сумма голосов для списков и карточек считается через **подзапрос + `Sum(value)`**, чтобы при фильтрации по тегам не искажать итог из‑за JOIN.

- Команда **`fill_db`** создаёт случайные лайки и дизлайки для нагрузочного теста.



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



Пользователи = `ratio`, вопросы = `ratio * 10`, ответы = `ratio * 100`, теги = `ratio`, голоса (лайк/дизлайк) ≈ `ratio * 200`. Генерация — **Faker**, массовые вставки — **`bulk_create`**; для малых `ratio` из‑за уникальности связей может понадобиться **`ratio >= 10`**.



```powershell

python manage.py createsuperuser

```



## Структура проекта

| Путь | Назначение |
|------|------------|
| `application/` | `settings.py`, корневой `urls.py`; SQLite/Postgres из env; debug-toolbar при `DEBUG` |
| `core/` | Логин, регистрация, профиль, logout; `/user/<username>/`; `auth_utils`, `sidebar_context`, сигнал `Profile`; шаблоны и статика; templatetag пагинации |
| `questions/` | Модели и голоса (**`value` ±1**), вьюхи списков и вопроса, ask/answer, **JSON**-голосование и верный ответ; `presentation` (в т.ч. пагинация списков), `like_annotations` (**`viewer_vote`**); `fill_db` |
| `manage.py`, `requirements.txt`, Docker-файлы | см. корень репозитория |

### Маршруты (именованные)

| URL | Имя в шаблонах (`{% url %}`) |
|-----|------------------------------|
| `/` | `index` |
| `/hot/` | `hot` |
| `/tag/…/` | `tag` (аргумент `tag`) |
| `/question/…/` | `question_detail` (аргумент `pk`) |
| `/ask/` | `ask` |
| `/question/…/vote/` | `question_vote` (POST, **AJAX JSON**) |
| `/answer/…/vote/` | `answer_vote` (POST, **AJAX JSON**) |
| `/answer/…/correct/` | `mark_answer_correct` (POST, **AJAX JSON**, автор вопроса) |
| `/logout/` | `logout` (POST) |
| `/user/<username>/` | `public_user` |
| `/login/` | `login` |
| `/signup/` | `signup` |
| `/profile/` | `profile` |
| `/layout/` | `layout` (демо каркаса) |
| `/admin/` | админка Django |


Списки вопросов и ответы на странице вопроса читаются из БД; пагинация — **`questions.presentation.paginate`** (лишний номер страницы — **404**); компактные номера страниц — **`elided_page_numbers`** в `core/templatetags/pagination_tags`.



### Статика



В `core/static/core/`. Подключение jQuery — из CDN в **`base.html`**; логика голосов и отметки верного ответа — **`cupofq.js`**. В шаблонах — `{% static %}`. `/static/` и `/media/` в корне в `.gitignore`.



---



**Запуск:** при `DEBUG=true` установите зависимости из **`requirements.txt`** (в т.ч. toolbar). Для Postgres в `.env` нужен **psycopg** из `requirements.txt`; без `POSTGRES_DB` — SQLite.



## Архив



**ДЗ4**: полноценная **авторизация** (логин с безопасным **`next`**, регистрация с валидатором пароля, выход), **профиль** с полями пользователя и аватаром, **публичная страница** `/user/<username>/`; в **`questions`** — **ModelForm** для нового вопроса и ответа, теги через **get-or-create**, гость при ответе уходит на логин с **`next`**, после ответа — редирект с **якорем** к ответу; первичное **голосование POST + редирект** и **верный ответ** только автором вопроса; соблюдение требований к **CSRF**, **POST** и **PRG** в формах. Детали окружения, Docker и `fill_db` — в разделах выше (актуальны и для следующих ДЗ).



**ДЗ3**: модели данных и админка; выбор **PostgreSQL / SQLite** и **Docker Compose**; команда **`fill_db`**; выдача списков вопросов и страницы вопроса с **пагинацией**; при **`DEBUG`** — **django-debug-toolbar**.



**ДЗ2** — перенос вёрстки в шаблоны Django, каркас `core` и `questions`, именованные URL, списки и страница вопроса на заглушках, первый Docker Compose.



**ДЗ1** — статическая вёрстка; затем перенос в Django, папка `public/` удалена.


