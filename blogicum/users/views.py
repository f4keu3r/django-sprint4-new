from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegistrationForm, ProfileEditForm


POSTS_PER_PAGE = 10


class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        posts = (
            profile.posts
            .with_relations()
            .with_comments_count()
        )
    else:
        posts = (
            profile.posts
            .available()
            .with_relations()
            .with_comments_count()
        )

    posts = posts.order_by('-pub_date')
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': profile,
        'page_obj': page_obj,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})
