from django.core.paginator import Paginator


POSTS_PER_PAGE = 10


def paginate(request, queryset):
    """Общая пагинация: отдаёт page_obj по POSTS_BY_PAGE."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))
