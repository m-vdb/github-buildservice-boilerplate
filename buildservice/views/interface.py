"""The views accessible to humans"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from buildservice.models import Repository, Build
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required


@login_required
@oauth_token_required
def home(request):
    """
    This is the home. WHen user is logged in and
    we have a token, this view lists the available
    repositories and makes it possible to activate
    or deactivate webhooks.
    """
    token = request.user.oauth_token.value
    hooks = request.user.webhook_set.filter(active=True)
    # needed for CSRF
    return render(request, "home.html", {
        "repositories": github.get_user_repos(token),
        "active_hooks": set(hook.repository.name for hook in hooks)
    })


@login_required
def build(request, build_id):
    """
    Displays a build progress.
    """
    return render(request, "build.html", {'build_id': build_id})


def badge(request, repo_name, branch_name=None):
    """
    Return a svg that gives the build status of the repository.
    """
    svg_name = "svg/buildservice-%s.svg"
    status = "unknown"
    try:
        repository = Repository.objects.get(name=repo_name)
    except Repository.DoesNotExist:
        pass
    else:
        build = Build.objects.filter(
            repository=repository,
            branch=branch_name or repository.default_branch
        ).exclude(
            status='pending'
        ).order_by('-created_at').first()
        if build:
            status = build.status

    return render(
        request, svg_name % status,
        content_type="image/svg+xml"
    )
