from django.conf import settings
from django.db import models


class Webhook(models.Model):
    """
    A database record containing a user's webhook to
    a repository. There can be several hooks per user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    repository = models.CharField(max_length=255)
    github_id = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
