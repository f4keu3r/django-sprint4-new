from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.pagination import paginate
from .forms import RegistrationForm, ProfileEditForm


User = get_user_model()
POSTS_PER_PAGE = 10


class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)

    posts = profile.posts
    if request.user != profile:
        posts = posts.available()
    posts = posts.with_relations().with_comments_count()

    page_obj = paginate(request, posts)

    return render(request, 'blog/profile.html', {
        'profile': profile,
        'page_obj': page_obj,
    })


@login_required
def profile_edit(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form})
