from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment


POSTS_PER_PAGE = 10


def _paginate(request, queryset):
    """Общая пагинация: отдаёт page_obj по POSTS_BY_PAGE."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = (
        Post.objects
        .available()
        .with_relations()
        .with_comments_count()
        .order_by('-pub_date')
    )
    page_obj = _paginate(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.with_relations(),
        pk=pk,
    )
    is_available = (
        post.is_published
        and post.category is not None
        and post.category.is_published
        and post.pub_date <= timezone.now()
    )
    if not is_available and request.user != post.author:
        raise Http404
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
        .order_by('-pub_date')
    )
    page_obj = _paginate(request, post_list)
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


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', pk=post.pk)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', pk=post.pk)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect('blog:post_detail', pk=self.post_object.pk)

    def form_valid(self, form):
        form.instance.post = self.post_object
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        context = {
            'post': self.post_object,
            'comments': self.post_object.comments.all(),
            'form': form,
        }
        return render(self.request, 'blog/detail.html', context)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']})
