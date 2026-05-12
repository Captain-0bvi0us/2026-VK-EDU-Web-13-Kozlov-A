import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _env_list(key: str, default: str) -> list[str]:
    raw = os.environ.get(key, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


if os.environ.get("DJANGO_RUN_IN_DOCKER", "").strip().lower() not in ("1", "true", "yes", "on"):
    load_dotenv(BASE_DIR / ".env.local", override=True)


def _database_config():
    name = os.environ.get("POSTGRES_DB", "").strip()
    if not name:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    engine = os.environ.get("DJANGO_DB_ENGINE", "django.db.backends.postgresql").strip()
    if engine not in (
        "django.db.backends.postgresql",
        "django.db.backends.postgresql_psycopg2",
    ):
        engine = "django.db.backends.postgresql"
    return {
        "ENGINE": engine,
        "NAME": name,
        "USER": os.environ.get("POSTGRES_USER", "").strip(),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost").strip() or "localhost",
        "PORT": os.environ.get("POSTGRES_PORT", "5432").strip() or "5432",
        "OPTIONS": {
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": _env_int("POSTGRES_CONN_MAX_AGE", 0),
    }


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "secret-key"

DEBUG = _env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
    "questions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "application.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.sidebar_context.sidebar_context",
            ],
            "libraries": {
                "pagination_tags": "core.templatetags.pagination_tags",
            },
        },
    },
]

WSGI_APPLICATION = "application.wsgi.application"

DATABASES = {"default": _database_config()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"


def show_debug_toolbar(request):
    from django.conf import settings as dj_settings

    return dj_settings.DEBUG


if DEBUG:
    INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]
    INTERNAL_IPS = ["127.0.0.1", "::1"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": "application.settings.show_debug_toolbar",
    }
