from django.utils.http import url_has_allowed_host_and_scheme


def get_safe_redirect_url(request, url: str | None, *, fallback: str) -> str:
    if not url:
        return fallback
    allowed = {request.get_host()}
    if url_has_allowed_host_and_scheme(
        url,
        allowed_hosts=allowed,
        require_https=request.is_secure(),
    ):
        return url
    return fallback


def get_safe_logout_redirect(request, fallback: str) -> str:
    return get_safe_redirect_url(request, request.META.get("HTTP_REFERER"), fallback=fallback)
