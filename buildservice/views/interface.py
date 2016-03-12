from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required


@login_required
@oauth_token_required
def home(request):
    token = request.user.oauth_token
    # needed for CSRF
    return render(request, "home.html", {"repositories": github.get_user_repos(token.value)})
