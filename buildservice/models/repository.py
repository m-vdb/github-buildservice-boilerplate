"""The Repository model"""
from django.conf import settings
from django.db import models

from .oauth_token import OAuthToken
from buildservice.errors import MissingToken
from buildservice.utils import github


class Repository(models.Model):
    """
    A database record containing a repository.
    """
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='repositories',
        related_query_name='repository'
    )
    name = models.CharField(max_length=255, unique=True)
    default_branch = models.CharField(max_length=255, default='master')
    build_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the name of the repository.
        """
        return self.name

    @classmethod
    def add_user_to_known_repositories(cls, user):
        """
        Add a new user to known repositories. If one
        of his collaborators already added repositories,
        that way he can access them.
        """
        token = user.oauth_token.value
        repository_names = [repo.full_name for repo in github.get_user_repos(token)]
        repositories = list(cls.objects.filter(name__in=repository_names))
        user.repositories.add(*repositories)

    def get_token(self):
        """
        Get a token for the repository. If none
        is found, a MissingToken exception is raised.
        """
        token = OAuthToken.objects.filter(user__in=self.users.all()).first()  # pylint: disable=no-member
        if not token:
            raise MissingToken('Cannot find token for repository %s' % self)

        return token
