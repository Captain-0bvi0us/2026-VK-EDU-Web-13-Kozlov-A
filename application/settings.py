import os
from pathlib import Path

from celery.schedules import crontab
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


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


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
    "django.contrib.postgres",
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

CSRF_TRUSTED_ORIGINS = _env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000",
)
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# -------------------- Redis / Celery / Celerybeat --------------------

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost").strip() or "localhost"
REDIS_PORT = _env_int("REDIS_PORT", 6379)
REDIS_CACHE_DB = _env_int("REDIS_CACHE_DB", 1)
REDIS_BROKER_DB = _env_int("REDIS_BROKER_DB", 2)
REDIS_BEAT_DB = _env_int("REDIS_BEAT_DB", 3)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 60 * 10,
    }
}

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"

CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_REDBEAT_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"

CELERY_TIMEZONE = os.environ.get("CELERY_TIMEZONE", TIME_ZONE) or TIME_ZONE
CELERY_TASK_TIME_LIMIT = 60 * 5
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 4
CELERY_TASK_ALWAYS_EAGER = _env_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    "recompute-popular-tags": {
        "task": "core.tasks.recompute_popular_tags",
        "schedule": crontab(minute="*/10"),
    },
    "recompute-best-members": {
        "task": "core.tasks.recompute_best_members",
        "schedule": crontab(minute="5-59/10"),
    },
}

# -------------------- Centrifugo (realtime) --------------------

CENTRIFUGO_API_URL = (
    os.environ.get("CENTRIFUGO_API_URL", "").strip()
    or "http://localhost:8001/api"
)
CENTRIFUGO_API_KEY = os.environ.get("CENTRIFUGO_API_KEY", "").strip()
CENTRIFUGO_HMAC_SECRET_KEY = os.environ.get("CENTRIFUGO_HMAC_SECRET_KEY", "").strip()
CENTRIFUGO_NAMESPACE = os.environ.get("CENTRIFUGO_NAMESPACE", "questions").strip() or "questions"
CENTRIFUGO_WS_URL = (
    os.environ.get("CENTRIFUGO_WS_URL", "").strip()
    or "ws://localhost:8001/connection/websocket"
)
CENTRIFUGO_TOKEN_TTL = _env_int("CENTRIFUGO_TOKEN_TTL", 60 * 60)

# -------------------- Email --------------------

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
).strip()
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost").strip() or "localhost"
EMAIL_PORT = _env_int("EMAIL_PORT", 1025)
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL", "").strip()
    or "CupOfQ <noreply@cupofq.local>"
)


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
