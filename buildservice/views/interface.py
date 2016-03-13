from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required


@login_required
@oauth_token_required
def home(request):
    token = request.user.oauth_token.value
    hooks = request.user.webhook_set.filter(active=True)
    # needed for CSRF
    return render(request, "home.html", {
        "repositories": github.get_user_repos(token),
        "active_hooks": set(hook.repository for hook in hooks)
    })


@login_required
def build(request, build_id):
    return render(request, "build.html")
