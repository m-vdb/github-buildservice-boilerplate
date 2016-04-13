"""The Repository model"""
from django.db import models

from .oauth_token import OAuthToken
from buildservice.errors import MissingToken


class Repository(models.Model):
    """
    A database record containing a repository.
    """
    name = models.CharField(max_length=255, unique=True)
    default_branch = models.CharField(max_length=255, default='master')
    build_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_token(self):
        """
        Get a token for the repository. If none
        is found, a MissingToken exception is raised.
        """
        token = OAuthToken.objects.filter(user__webhook__repository=self).first()
        if not token:
            raise MissingToken('Cannot find token for repository %s' % self)

        return token
