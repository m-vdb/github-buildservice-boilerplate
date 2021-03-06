"""The OAuthToken model"""
from django.conf import settings
from django.db import models


class OAuthToken(models.Model):
    """
    A database record containing a user's access token.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='oauth_token'
    )
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
