from django.core.paginator import Paginator


POSTS_PER_PAGE = 10


def paginate(request, queryset):
    """Общая пагинация: отдаёт page_obj по POSTS_PER_PAGE."""
    return Paginator(
        queryset, POSTS_PER_PAGE
    ).get_page(
        request.GET.get('page')
    )
