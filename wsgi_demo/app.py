""" Простой WSGI-скрипт без Django.

* Запускается gunicorn'ом на ``localhost:8081``.
* ``GET /`` и ``POST /`` — отдают HTML со списком GET и POST параметров.
* ``GET /static/sample.html`` — отдаёт статический документ с диска
  (используется для бенчмарка «статика через WSGI/gunicorn»).
"""

from __future__ import annotations

import os
from html import escape
from urllib.parse import parse_qsl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

_HEADER_HTML = "Content-Type", "text/html; charset=utf-8"


def _read_post(environ) -> list[tuple[str, str]]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    if length <= 0:
        return []
    body = environ["wsgi.input"].read(length) or b""
    ctype = (environ.get("CONTENT_TYPE") or "").lower()
    if "application/x-www-form-urlencoded" not in ctype:
        return []
    return parse_qsl(body.decode("utf-8", errors="replace"), keep_blank_values=True)


def _render_params(get_params, post_params) -> bytes:
    def section(title: str, items: list[tuple[str, str]]) -> str:
        if not items:
            return f"<h2>{escape(title)}</h2><p><em>пусто</em></p>"
        rows = "".join(
            f"<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>"
            for k, v in items
        )
        return (
            f"<h2>{escape(title)}</h2>"
            "<table border='1' cellspacing='0' cellpadding='4'>"
            "<thead><tr><th>имя</th><th>значение</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    body = (
        "<!doctype html><html lang='ru'><head>"
        "<meta charset='utf-8'><title>WSGI demo</title></head><body>"
        "<h1>WSGI demo (ДЗ7)</h1>"
        f"{section('GET-параметры', get_params)}"
        f"{section('POST-параметры', post_params)}"
        "</body></html>"
    )
    return body.encode("utf-8")


def _serve_static(path: str, start_response):
    full = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip("/")))
    if not full.startswith(STATIC_DIR) or not os.path.isfile(full):
        start_response("404 Not Found", [_HEADER_HTML])
        return [b"<h1>404</h1>"]
    with open(full, "rb") as f:
        data = f.read()
    ctype = "text/html; charset=utf-8" if full.endswith(".html") else "application/octet-stream"
    headers = [
        ("Content-Type", ctype),
        ("Content-Length", str(len(data))),
    ]
    start_response("200 OK", headers)
    return [data]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path.startswith("/static/"):
        return _serve_static(path[len("/static/"):], start_response)

    get_params = parse_qsl(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    post_params = _read_post(environ) if environ["REQUEST_METHOD"] == "POST" else []
    body = _render_params(get_params, post_params)
    headers = [_HEADER_HTML, ("Content-Length", str(len(body)))]
    start_response("200 OK", headers)
    return [body]
