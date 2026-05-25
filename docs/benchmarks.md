# Нагрузочное тестирование (ab)

Все измерения сделаны утилитой **Apache Benchmark** (`jordi/ab` в docker), запущенной из одной docker-сети с сервисами проекта, чтобы исключить накладные расходы внешней маршрутизации.

Параметры одинаковые для всех тестов:

```
ab -n 2000 -c 50 <url>
```

* **n** — 2000 запросов суммарно
* **c** — 50 одновременных соединений
* gunicorn у обоих сервисов запущен с **2 воркерами** (`workers = 2`)
* документы примерно одинакового размера: статика **755 B** (`/sample.html`) и **752 B** (`/static/sample.html`), динамика **432 B** (`/`)

## Сводная таблица

| # | Сценарий                                              | RPS, mean | TTRP, ms (mean) | Document, B |
|---|-------------------------------------------------------|-----------|-----------------|-------------|
| 1 | Статика напрямую через **nginx**                       | **11834** |   4.2           | 755         |
| 2 | Статика через **gunicorn** (WSGI-демо, `open()`)       |    275    | 181.8           | 752         |
| 3 | Динамика напрямую через **gunicorn**                   |   1523    |  32.8           | 432         |
| 4 | Динамика через **nginx → gunicorn** (без кэша)         |   1318    |  37.9           | 432         |
| 5 | Динамика через **nginx → gunicorn** + **proxy_cache**  |   4770    |  10.5           | 432         |

> Полный вывод `ab` для каждого теста — в [`benchmarks_raw.md`](./benchmarks_raw.md).

## Ответы на вопросы методички

### 1) Насколько быстрее статика по сравнению с WSGI?

`nginx static` против `gunicorn static`: **11834 / 275 ≈ 43×**.

То есть отдача статического документа напрямую через nginx примерно **в 30 раз быстрее**, чем отдача того же файла через WSGI-приложение на gunicorn. Это ожидаемо:

* у nginx — `sendfile`, нулевые копирования в kernel-space, многопоточная сетевая обработка;
* WSGI-сервер для каждого запроса проходит цикл worker'ов Python, `open()`/`read()`, формирование заголовков, GIL.

### 2) Во сколько раз ускоряет работу proxy_cache?

`nginx → gunicorn (cache)` против `nginx → gunicorn (no cache)`: **4770 / 1318 ≈ 3.6×**.

Включение `proxy_cache` ускоряет работу примерно в **3 раза**. После первого `MISS` все последующие запросы отвечает сам nginx из памяти/диска, и upstream gunicorn вообще не дергается. Дополнительный эффект — снижение нагрузки на backend.

## Наблюдения

* «Обернуть gunicorn в nginx» **без** `proxy_cache` стоит ~10-15% производительности (1523 → 1318 RPS): два хопа TCP + парсинг заголовков. Плата за единый фронт-эндпоинт со статикой, gzip, кешированием браузера и единой точкой входа.
* С `proxy_cache` nginx+gunicorn (4770 RPS) обгоняет голый gunicorn (1523 RPS) **в ~3 раза** на том же документе — для большинства запросов backend не вызывается совсем.
* Статика через WSGI (gunicorn `open()`-and-`read()`) **в ~43 раза медленнее** статики через nginx — иллюстрация, почему в проде статику всегда отдают front-сервером.

## Воспроизведение

```powershell
docker compose up -d

# 1. nginx static
docker run --rm --network 2026-vk-edu-web-13-kozlov-a_default jordi/ab `
  -n 2000 -c 50 "http://nginx/sample.html"

# 2. gunicorn static
docker run --rm --network 2026-vk-edu-web-13-kozlov-a_default jordi/ab `
  -n 2000 -c 50 "http://wsgi_demo:8081/static/sample.html"

# 3. gunicorn dynamic
docker run --rm --network 2026-vk-edu-web-13-kozlov-a_default jordi/ab `
  -n 2000 -c 50 "http://wsgi_demo:8081/?foo=bar&hello=world"

# 4. nginx -> gunicorn (no cache)
docker run --rm --network 2026-vk-edu-web-13-kozlov-a_default jordi/ab `
  -n 2000 -c 50 "http://nginx/demo/?foo=bar&hello=world"

# 5. nginx -> gunicorn (proxy_cache) — сначала прогреть curl'ом
curl http://localhost/demo-cached/?foo=bar&hello=world
docker run --rm --network 2026-vk-edu-web-13-kozlov-a_default jordi/ab `
  -n 2000 -c 50 "http://nginx/demo-cached/?foo=bar&hello=world"
```
