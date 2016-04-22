"""Testing utilities"""
from django.contrib.auth import get_user_model

from buildservice.models import OAuthToken, Webhook


def create_user_token(repo=None, user=None):
    """
    Create a Django user and token. For that we have to
    mimic the registration of a webhook.
    """
    if not user:
        user_class = get_user_model()
        user = user_class.objects.create_user('uuu', password='ttt')
    token = OAuthToken.objects.create(user=user, value='the_token')
    if repo:
        Webhook.objects.create(user=user, repository=repo)
    return token
