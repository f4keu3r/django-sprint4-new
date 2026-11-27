from django.db import models
from django.db.models import Count, Q
from django.utils import timezone


def _available_q():
    return Q(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


class PostQuerySet(models.QuerySet):

    def available(self):
        """Посты, доступные для показа читателю."""
        return self.filter(_available_q())

    def available_or_author(self, user):
        """Доступные посты плюс все посты указанного автора."""
        if user.is_authenticated:
            return self.filter(_available_q() | Q(author=user))
        return self.available()

    def with_relations(self):
        """Подтягивает связанные author, category, location одним запросом."""
        return self.select_related('author', 'category', 'location')

    def with_comments_count(self):
        """Аннотирует число комментариев (одним запросом на выборку)."""
        return self.annotate(
            comment_count=Count('comments'),
        ).order_by('-pub_date')
