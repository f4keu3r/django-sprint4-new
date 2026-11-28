from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from .models import Post


class PostAuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.get_object().pk)


class CommentAuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id')
        if post_id is None:
            raise Http404('Не указан идентификатор публикации.')
        return redirect('blog:post_detail', pk=post_id)


class CommentQuerysetMixin:

    def get_queryset(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id'),
        ).comments.all()
