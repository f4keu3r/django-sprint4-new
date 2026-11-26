from django.db import models
from django.db.models import Count
from django.utils import timezone


class PostQuerySet(models.QuerySet):

    def available(self):
        """Посты, доступные для показа читателю."""
        return self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    def with_relations(self):
        """Подтягивает связанные author, category, location одним запросом."""
        return self.select_related('author', 'category', 'location')

    def with_comments_count(self):
        """Аннотирует число комментариев (одним запросом на выборку)."""
        return self.annotate(comment_count=Count('comments'))
