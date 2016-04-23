"""Testing utilities"""
from buildservice.models import OAuthToken, Webhook


def create_user_token(user, repo=None):
    """
    Create a Django user and token. For that we have to
    mimic the registration of a webhook.
    """
    token = OAuthToken.objects.create(user=user, value='the_token')
    if repo:
        Webhook.objects.create(repository=repo)
    return token
