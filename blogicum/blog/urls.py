from django.urls import include, path

from users.views import profile_edit, profile_view
from .views import (
    index,
    post_detail,
    category_posts,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView,
)

app_name = 'blog'

POSTS_PREFIX = 'posts/'

post_urls = [
    path(
        'create/',
        PostCreateView.as_view(),
        name='create_post',
    ),
    path(
        '<int:post_id>/edit/',
        PostUpdateView.as_view(),
        name='edit_post',
    ),
    path(
        '<int:post_id>/delete/',
        PostDeleteView.as_view(),
        name='delete_post',
    ),
    path(
        '<int:post_id>/comment/',
        CommentCreateView.as_view(),
        name='add_comment',
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        CommentUpdateView.as_view(),
        name='edit_comment',
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment',
    ),
]

urlpatterns = [
    path(
        '',
        index,
        name='index',
    ),
    path(
        'category/<slug:category_slug>/',
        category_posts,
        name='category_posts'
    ),

    path(
        'profile/edit/',
        profile_edit,
        name='edit_profile',
    ),
    path(
        'profile/<str:username>/',
        profile_view,
        name='profile',
    ),
    path(
        POSTS_PREFIX, include(post_urls),
    ),
    path(
        'posts/<int:pk>/',
        post_detail,
        name='post_detail',
    ),
]
