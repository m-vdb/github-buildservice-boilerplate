"""OAuth views"""
from django.conf import settings
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session

from buildservice.models import OAuthToken
from buildservice.errors import MalformattedToken


def login(request):
    """
    Step 1 of OAuth: redirect to provider.
    """
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, scope=settings.GITHUB_SCOPES)
    authorization_url, state = github.authorization_url(settings.GITHUB_AUTHORIZATION_BASE_URL)

    request.session['oauth_state'] = state
    return redirect(authorization_url)


def callback(request):
    """
    Step 2 of OAuth: fetch the token.
    """
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, state=request.session['oauth_state'])
    token = github.fetch_token(
        settings.GITHUB_TOKEN_URL,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri()
    )

    try:
        OAuthToken.objects.create(user=request.user, value=token['access_token'])
    except KeyError:
        raise MalformattedToken('Cannot read access_token.')

    return redirect("home")
