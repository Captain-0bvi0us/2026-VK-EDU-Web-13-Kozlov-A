from __future__ import annotations

import logging

from django.core.cache import cache

from . import cache_keys
from .tasks import _compute_best_members, _compute_popular_tags

logger = logging.getLogger(__name__)


_TAG_SIZES = ("lg", "md", "md", "sm", "sm", "accent", "warm", "sm")


def _decorate_tags(items: list[dict]) -> list[dict]:
    out = []
    for i, t in enumerate(items):
        size = _TAG_SIZES[i] if i < len(_TAG_SIZES) else "sm"
        out.append({**t, "size": size})
    return out


def get_popular_tags() -> list[dict]:
    try:
        cached = cache.get(cache_keys.POPULAR_TAGS)
    except Exception:  # noqa: BLE001
        cached = None
    if cached is not None:
        return _decorate_tags(cached)
    data = _compute_popular_tags()
    try:
        cache.set(cache_keys.POPULAR_TAGS, data, timeout=cache_keys.SIDEBAR_TIMEOUT)
    except Exception:  # noqa: BLE001
        logger.warning("popular_tags: не удалось записать кэш", exc_info=True)
    return _decorate_tags(data)


def get_best_members() -> list[dict]:
    try:
        cached = cache.get(cache_keys.BEST_MEMBERS)
    except Exception:  # noqa: BLE001
        cached = None
    if cached is not None:
        return cached
    data = _compute_best_members()
    try:
        cache.set(cache_keys.BEST_MEMBERS, data, timeout=cache_keys.SIDEBAR_TIMEOUT)
    except Exception:  # noqa: BLE001
        logger.warning("best_members: не удалось записать кэш", exc_info=True)
    return data


def sidebar_context(request):
    return {
        "popular_tags": get_popular_tags(),
        "best_members": get_best_members(),
    }
