"""The Build model"""
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse


class Build(models.Model):
    """
    A database record containing a repository build.
    """
    STATUSES = (
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('errored', 'Errored'),
        ('pending', 'Pending'),
    )
    repository = models.ForeignKey('Repository', on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    branch = models.CharField(max_length=255)
    sha = models.CharField(max_length=40)
    pusher_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):  # pylint: disable=too-few-public-methods
        """Model options"""
        unique_together = (
            ('repository', 'number'),
        )

    @property
    def pusher_profile_url(self):
        """
        Return the pusher profile URL on Github.
        """
        return settings.GITHUB_USER_PROFILE_URL % self.pusher_name

    @property
    def url(self):
        """
        Return the build url, useful to create statuses.
        """
        return "%s%s" % (
            settings.BUILDSERVICE_BASE_URL,
            reverse('build_detail', args=[self.repository.name, self.number])
        )

    @property
    def is_success(self):
        """
        Return True if the build is successful.
        """
        return self.status == 'success'

    @property
    def is_pending(self):
        """
        Return True if the build is pending.
        """
        return self.status == 'pending'

    @property
    def short_sha(self):
        """
        Return the 7 first chars of the Build's sha.
        """
        return self.sha[:7]  # pylint: disable=unsubscriptable-object
