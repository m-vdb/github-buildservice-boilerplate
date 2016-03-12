from django.conf import settings
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session

from buildservice.models import OAuthToken


def login(request):
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, scope=settings.GITHUB_SCOPES)
    authorization_url, state = github.authorization_url(settings.GITHUB_AUTHORIZATION_BASE_URL)

    request.session['oauth_state'] = state
    return redirect(authorization_url)


def callback(request):
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, state=request.session['oauth_state'])
    token = github.fetch_token(
        settings.GITHUB_TOKEN_URL,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri()
    )

    OAuthToken.objects.create(user=request.user, value=token)
    return redirect("interface_home")
