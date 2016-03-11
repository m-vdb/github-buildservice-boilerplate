from django.conf import settings
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session


def login(request):
    github = OAuth2Session(settings.GITHUB_CLIENT_ID)
    authorization_url, state = github.authorization_url(settings.GITHUB_AUTHORIZATION_BASE_URL)

    request.session['oauth_state'] = state
    return redirect(authorization_url)


def callback(request):
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, request.session['oauth_state'])
    token = github.fetch_token(
        settings.GITHUB_TOKEN_URL,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri()  # TODO: code, redirect_uri?
    )

    return redirect("interface_home")
