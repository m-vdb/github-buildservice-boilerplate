from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from buildservice.models import OAuthToken
from buildservice.utils import github


@login_required
def home(request):
    try:
        token = request.user.oauth_token
    except OAuthToken.DoesNotExist:
        return redirect('oauth_login')

    # needed for CSRF
    return render(request, "home.html", {"repositories": github.get_user_repos(token.value)})
