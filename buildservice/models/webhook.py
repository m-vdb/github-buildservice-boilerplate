"""The Webhook model"""
from django.conf import settings
from django.core.urlresolvers import reverse
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
    repository = models.ForeignKey('Repository')
    github_id = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_push_url(cls):
        """
        Return the push url, useful when creating the webhook on Github.
        """
        return "%s%s" % (settings.BUILDSERVICE_BASE_URL, reverse('webhooks_push'))
