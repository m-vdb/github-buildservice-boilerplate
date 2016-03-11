from functools import wraps

from django.shortcuts import redirect

from buildservice.models import OAuthToken


def oauth_token_required(func):
    """
    A decorator to require that
    request.user.oauth_token exists.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        try:
            _ = request.user.oauth_token
        except (AttributeError, OAuthToken.DoesNotExist):
            return redirect('oauth_login')

        return func(request, *args, **kwargs)

    return inner
