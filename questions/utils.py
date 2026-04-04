from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(objects_list, request, per_page=10):
    """Возвращает объект Page для шаблона пагинатора."""
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get("page", 1)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
