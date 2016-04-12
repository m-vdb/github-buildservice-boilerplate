"""Decorators for views"""
from functools import wraps
import hashlib
import hmac

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from buildservice.models import OAuthToken


def oauth_token_required(func):
    """
    A decorator to require that
    request.user.oauth_token exists.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        """
        Try to get token and redirect to oauth_login
        if not found.
        """
        try:
            _ = request.user.oauth_token
        except (AttributeError, OAuthToken.DoesNotExist):
            return redirect('oauth_login')

        return func(request, *args, **kwargs)

    return inner


def signature_required(func):
    """
    A decorator to require the
    X-Hub-Signature header to be valid.
    See https://developer.github.com/v3/repos/hooks/#webhook-headers.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        """
        Try to validate the signature and return a 401 if not valid.
        """
        signature = "sha1=%s" % hmac.new(
            settings.GITHUB_HOOK_SECRET.encode('utf-8'),
            request.body,
            hashlib.sha1
        ).hexdigest()
        if signature != request.META.get('HTTP_X_HUB_SIGNATURE'):
            return HttpResponse(status=401, content="Invalid signature.")

        return func(request, *args, **kwargs)

    return inner


def anonymous_user_required(func):
    """
    A decorator that require that a user is *not* logged in.
    If it's the case, it redirects the user to home.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        """
        Redirect the user to home if user is authentiated,
        else call `func` normally.
        """
        if request.user.is_authenticated():
            return redirect('home')
        return func(request, *args, **kwargs)

    return inner
