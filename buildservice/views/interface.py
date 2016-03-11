from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect

from buildservice.models import OAuthToken


@login_required
def home(request):
    try:
        token = request.user.oauth_token
    except OAuthToken.DoesNotExist:
        return redirect('oauth_login')

    # TODO: list user repos
    return render_to_response("home.html")
