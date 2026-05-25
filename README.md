# 2026-VK-EDU-Web-13-Kozlov-A

Репозиторий курса «WEB-технологии»: Django-приложение **CupOfQ** — вопросы и ответы с авторизацией, профилем, голосованием, realtime-обновлениями, фоновыми задачами, полнотекстовым поиском и боевой инфраструктурой gunicorn + nginx. **Ниже описана реализация ДЗ7**; предыдущие этапы — **в конце, в разделе «Архив»**.

## Домашнее задание 7 — инфраструктура: gunicorn + nginx

### 1. Gunicorn для Django

Django запускается через **gunicorn** с **двумя воркерами** (`workers = 2`) — конфиг лежит в [`gunicorn/django.conf.py`](./gunicorn/django.conf.py).

```bash
gunicorn -c gunicorn/django.conf.py application.wsgi:application
```

В `docker-compose.yml` команда сервиса `web` сначала прогоняет `migrate` и `collectstatic`, затем поднимает gunicorn на порту **8000**.

### 2. Отдельный WSGI-скрипт без Django

Отдельное WSGI-приложение лежит в [`wsgi_demo/app.py`](./wsgi_demo/app.py) и поднимается **тем же gunicorn'ом** (своим конфигом [`gunicorn/demo.conf.py`](./gunicorn/demo.conf.py)) на порту **8081**:

```bash
gunicorn -c gunicorn/demo.conf.py wsgi_demo.app:application
```

* `GET /?key=value&...` и `POST /` (form-urlencoded) — выводит HTML-таблицы с переданными **GET** и **POST** параметрами;
* `GET /static/sample.html` — отдаёт статический документ с диска через `open()` (используется в бенчмарках как «статика через gunicorn»);
* в Docker сервис называется `wsgi_demo`.

### 3. nginx — статика, /uploads/, gzip, кеш браузера, проксирование

Конфиг — [`nginx/nginx.conf`](./nginx/nginx.conf), укладывается в **46 строк** (требование ≤ 50). Что делает:

* `location ^~ /uploads/` (priority — `^~`) → `alias /srv/media/`, `expires 30d`, `Cache-Control: public, immutable` — пользовательские загрузки (Django `MEDIA_URL = /uploads/`);
* `location ~* \.(js|css|jpe?g|png|gif|svg|ico|webp|woff2?|ttf|eot|map|html)$` → `root /srv/static`, `expires 7d` — статика из `STATIC_ROOT` (`collectstatic` в `cupofq_static` volume);
* **gzip** включён (text/css, js, json, svg…), `gzip_comp_level 5`, `gzip_min_length 256`;
* `upstream django { server web:8000; }` и `upstream demo { server wsgi_demo:8081; }`;
* `location /` → `proxy_pass http://django` — все нестатические запросы проксируются на gunicorn;
* `location /cached/` и `/demo-cached/` — те же бекенды, но с `proxy_cache cupofq` (зона **10 MB**, **`max_size=100m`**, TTL **1 мин** для 200-х).

### 4. Сравнение производительности (ab, n=2000, c=50)

Полный отчёт — [`docs/benchmarks.md`](./docs/benchmarks.md), сырые выводы `ab` — [`docs/benchmarks_raw.md`](./docs/benchmarks_raw.md).

| # | Сценарий                                              | RPS    | Размер |
|---|-------------------------------------------------------|--------|--------|
| 1 | Статика через **nginx**                                | 11834  | 755 B  |
| 2 | Статика через **gunicorn** (WSGI)                      |   275  | 752 B  |
| 3 | Динамика через **gunicorn**                            |  1523  | 432 B  |
| 4 | Динамика через **nginx → gunicorn** (без кэша)         |  1318  | 432 B  |
| 5 | Динамика через **nginx → gunicorn** + **proxy_cache**  |  4770  | 432 B  |

* статика через nginx **в ~43 раза быстрее**, чем через WSGI;
* `proxy_cache` ускоряет динамический ответ **в ~3.6 раза**.

## Требования к окружению

* Python **3.11+** (локально; в Docker по `Dockerfile` — **Python 3.12**);
* **PostgreSQL** для полнотекстового поиска и Docker-стека;
* **Redis** для кэша и Celery;
* **Docker Desktop** — для полного стека ДЗ7 (nginx, gunicorn, wsgi_demo, centrifugo, maildev).

## Быстрый старт через Docker Compose

```powershell
copy .env.example .env.docker   # отредактировать ключи / пароли
docker compose up --build -d
```

| Сервис             | URL / порт с хоста                                  |
|--------------------|-----------------------------------------------------|
| Сайт (через nginx) | http://127.0.0.1/                                   |
| Django (gunicorn)  | http://127.0.0.1:8000/                              |
| WSGI-демо          | http://127.0.0.1:8081/?foo=bar                       |
| PostgreSQL         | `localhost:5433`                                    |
| Redis              | `localhost:6379`                                    |
| Centrifugo WS      | `ws://localhost:8001/connection/websocket`          |
| Maildev (письма)   | http://127.0.0.1:1080/                              |

Сервисы: `nginx`, `web`, `wsgi_demo`, `db`, `redis`, `centrifugo`, `maildev`, `celery_worker`, `celery_beat`.

После изменения Python-кода в celery-тасках:

```powershell
docker compose restart celery_worker celery_beat
```

После изменения JS / CSS / шаблонов (для nginx нужен обновлённый collectstatic):

```powershell
docker compose exec web python manage.py collectstatic --noinput
docker compose restart nginx
```

## Локальный запуск без Docker

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env.local
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn -c gunicorn/django.conf.py application.wsgi:application
# в соседних окнах:
celery -A application worker -l info
celery -A application beat -l info -S redbeat.RedBeatScheduler
gunicorn -c gunicorn/demo.conf.py wsgi_demo.app:application
```

Если **`POSTGRES_DB` не задан**, используется **SQLite** (поиск через `icontains`).

## Переменные окружения

В репозитории: **`.env.example`**. В Git не попадают: **`.env`**, **`.env.local`**, **`.env.docker`**.

* **Django**: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
* **Postgres**: `POSTGRES_*`
* **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_CACHE_DB`, `REDIS_BROKER_DB`, `REDIS_BEAT_DB`
* **Centrifugo**: `CENTRIFUGO_API_URL`, `CENTRIFUGO_API_KEY`, `CENTRIFUGO_HMAC_SECRET_KEY`, `CENTRIFUGO_WS_URL`, `CENTRIFUGO_NAMESPACE`
* **Email**: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`

## Наполнение базы

```powershell
python manage.py fill_db <ratio>
```

Пользователи = `ratio`, вопросы = `ratio*10`, ответы = `ratio*100`, теги = `ratio`, голоса ≈ `ratio*200`. Для малых `ratio` лучше **`ratio >= 10`**.

```powershell
python manage.py createsuperuser
```

## Проверка ДЗ7

1. **gunicorn (Django)** — `curl http://localhost:8000/` отдаёт главную;
2. **WSGI-демо** — `curl 'http://localhost:8081/?a=1&b=2'` показывает таблицу с GET-параметрами; `POST` — таблицу с POST-параметрами;
3. **nginx статика** — `curl http://localhost/sample.html` (HTTP 200, файл из `STATIC_ROOT`);
4. **nginx /uploads/** — загруженные аватары видны через `http://localhost/uploads/...`;
5. **nginx → gunicorn** — `curl http://localhost/` отдаёт главную (через прокси);
6. **proxy_cache** — `curl -I http://localhost/cached/` показывает `X-Cache-Status: MISS` при первом запросе и `HIT` при последующих.

## Структура проекта

| Путь                | Назначение |
|---------------------|------------|
| `application/`      | `settings.py`, `celery.py`, `wsgi.py`, корневой `urls.py` |
| `core/`             | auth, профиль, сайдбар, Centrifugo token, celery-таски кэша и email |
| `questions/`        | модели, вьюхи, realtime publish, поиск, `fill_db` |
| `wsgi_demo/`        | отдельный WSGI-скрипт (ДЗ7 п.4) + `static/sample.html` |
| `gunicorn/`         | конфиги gunicorn (Django + WSGI-демо) |
| `nginx/`            | `nginx.conf` (≤50 строк) |
| `centrifugo/`       | конфиг Centrifugo |
| `docs/`             | результаты бенчмарков `ab` |
| `docker-compose.yml`| db, redis, web (gunicorn), wsgi_demo, nginx, celery, centrifugo, maildev |

### Маршруты Django (именованные)

| URL                       | Имя                   | Примечание                |
|---------------------------|-----------------------|---------------------------|
| `/`                       | `index`               |                            |
| `/hot/`                   | `hot`                 |                            |
| `/tag/…/`                 | `tag`                 |                            |
| `/question/…/`            | `question_detail`     | realtime JS                |
| `/ask/`                   | `ask`                 |                            |
| `/question/…/vote/`       | `question_vote`       | POST, AJAX JSON           |
| `/answer/…/vote/`         | `answer_vote`         | POST, AJAX JSON           |
| `/answer/…/correct/`      | `mark_answer_correct` | POST, AJAX JSON           |
| `/api/search/suggest/`    | `search_suggest`      | GET, подсказки             |
| `/api/centrifugo/token/`  | `centrifugo_token`    | GET, WS-токен              |
| `/login/`, `/signup/`, `/profile/`, `/logout/` | | |
| `/user/<username>/`       | `public_user`         |                            |
| `/admin/`                 |                       | админка Django             |

---

## Архив

**ДЗ6**: **Redis + Celery + celerybeat** (брокер, cache backend, RedBeat schedule в трёх отдельных DB); кеш сайдбара (`recompute_popular_tags`, `recompute_best_members`) с fallback в БД; **Centrifugo** realtime через connection-token (без subscription-token), publish из celery-таски, JS на странице вопроса (3 сценария — пустой список, append на «своей» странице, alert на других); **email** через maildev + celery (`send_new_answer_email`); **полнотекстовый поиск** PostgreSQL (`SearchVectorField` + GIN-индекс, `SearchQuery + SearchRank`) с автодополнением (debounce 250 мс) и подсветкой `<mark>`.

**ДЗ5**: загрузка и отображение **аватаров** (`ImageField`, валидация расширения/размера, `upload_to` с UUID); **лайки/дизлайки** через AJAX (jQuery, `JsonResponse` с `score`/`vote`, CSRF); **отметка верного ответа** автором вопроса; рейтинг через `Subquery + Sum(value)` без искажений JOIN.

**ДЗ4**: авторизация (логин с `next`, регистрация, выход), профиль и `/user/<username>/`; ModelForm для вопроса и ответа, теги get-or-create, PRG и CSRF; первичное голосование POST + redirect.

**ДЗ3**: модели и админка; PostgreSQL / SQLite; Docker Compose; `fill_db`; списки и пагинация; debug-toolbar при `DEBUG`.

**ДЗ2** — перенос вёрстки в шаблоны Django, каркас `core` и `questions`, именованные URL, Docker Compose.

**ДЗ1** — статическая вёрстка; затем перенос в Django.
