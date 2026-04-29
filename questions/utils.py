from django.core.paginator import EmptyPage, Paginator
from django.http import Http404


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    raw = request.GET.get("page", 1)
    try:
        page_number = int(raw)
    except (TypeError, ValueError):
        return paginator.page(1)
    try:
        return paginator.page(page_number)
    except EmptyPage:
        raise Http404("Страницы с таким номером не существует.")
