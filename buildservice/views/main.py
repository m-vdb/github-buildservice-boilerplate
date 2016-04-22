"""The main views accessible to humans"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_control

from buildservice.models import Repository, Build
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required
from buildservice.utils.views import group_repositories


@login_required
@oauth_token_required
def home(request):
    """
    This is the home. This list repositories
    that already use the service.
    """
    return render(request, "home.html")


@login_required
@oauth_token_required
def repository_detail(request, repository_name):
    """
    Display the builds within a repository.
    """
    repository = get_object_or_404(Repository, name=repository_name)
    builds = Build.objects.filter(repository=repository).order_by('-created_at')[:50]

    return render(request, "repository_detail.html", {
        "repository": repository,
        "builds": builds
    })


@login_required
@oauth_token_required
def build_detail(request, repository_name, build_number):
    """
    Displays a build progress.
    """
    build = get_object_or_404(Build, repository__name=repository_name, number=build_number)
    return render(request, "build.html", {'repository': build.repository, 'build': build})


@login_required
@oauth_token_required
def register_repositories(request):
    """
    When user is logged in and
    we have a token, this view lists the available
    repositories and makes it possible to activate
    or deactivate webhooks.
    """
    token = request.user.oauth_token.value
    hooks = request.user.webhook_set.filter(active=True)
    repos = github.get_user_repos(token)
    # needed for CSRF
    return render(request, "register_repositories.html", {
        "repositories": group_repositories(repos),
        "active_hooks": set(hook.repository.name for hook in hooks)
    })


@cache_control(no_cache=True)
def badge(request, repository_name, branch_name=None):
    """
    Return a svg that gives the build status of the repository.
    """
    svg_name = "svg/buildservice-%s.svg"
    status = "unknown"
    try:
        repository = Repository.objects.get(name=repository_name)
    except Repository.DoesNotExist:
        pass
    else:
        last_build = Build.objects.filter(
            repository=repository,
            branch=branch_name or repository.default_branch
        ).exclude(
            status='pending'
        ).order_by('-created_at').first()
        if last_build:
            status = last_build.status

    return render(
        request, svg_name % status,
        content_type="image/svg+xml"
    )
