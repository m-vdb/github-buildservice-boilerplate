"""OAuth views"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session

from buildservice.models import OAuthToken, Repository


@login_required
def login(request):
    """
    Step 1 of OAuth: redirect to provider.
    """
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, scope=settings.GITHUB_SCOPES)
    authorization_url, state = github.authorization_url(settings.GITHUB_AUTHORIZATION_BASE_URL)

    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required
def callback(request):
    """
    Step 2 of OAuth: fetch the token.
    """
    try:
        oauth_state = request.session['oauth_state']
    except KeyError:
        return HttpResponseBadRequest('Missing oauth state.')

    github = OAuth2Session(settings.GITHUB_CLIENT_ID, state=oauth_state)
    token = github.fetch_token(
        settings.GITHUB_TOKEN_URL,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri()
    )

    try:
        OAuthToken.objects.create(user=request.user, value=token['access_token'])
    except (KeyError, TypeError):
        return HttpResponseBadRequest('Cannot read access_token.')

    Repository.add_user_to_known_repositories(request.user)
    return redirect("home")
