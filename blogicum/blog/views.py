from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from core.pagination import paginate
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from .mixins import (
    PostAuthorRequiredMixin,
    CommentAuthorRequiredMixin,
    CommentQuerysetMixin
)


def index(request):
    post_list = (
        Post.objects
        .available()
        .with_relations()
        .with_comments_count()
    )
    page_obj = paginate(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.with_relations().available_or_author(request.user),
        pk=pk,
    )
    context = {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = (
        category.posts
        .available()
        .with_relations()
        .with_comments_count()
    )
    page_obj = paginate(request, post_list)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostAuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.object.pk})


class PostDeleteView(PostAuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def get_post(self):
        return get_object_or_404(
            Post.objects.available_or_author(self.request.user),
            pk=self.kwargs['post_id'],
        )

    def get(self, request, *args, **kwargs):
        return redirect('blog:post_detail', pk=self.kwargs['post_id'])

    def form_valid(self, form):
        form.instance.post = self.get_post()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        post = self.get_post()
        context = {
            'post': post,
            'comments': post.comments.all(),
            'form': form,
        }
        return render(self.request, 'blog/detail.html', context)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentUpdateView(CommentAuthorRequiredMixin,
                        CommentQuerysetMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentDeleteView(CommentAuthorRequiredMixin,
                        CommentQuerysetMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})
