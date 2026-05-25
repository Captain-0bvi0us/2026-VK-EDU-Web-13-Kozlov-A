from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.filter
def elided_page_numbers(page, on_each_side: int = 2):
    if page is None:
        return []
    paginator = page.paginator
    out = []
    for x in paginator.get_elided_page_range(
        page.number,
        on_each_side=int(on_each_side),
        on_ends=1,
    ):
        out.append(None if x == Paginator.ELLIPSIS else x)
    return out
