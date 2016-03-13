"""The Build model"""
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse


class Build(models.Model):
    """
    A database record containing a repository build.
    """
    repository = models.CharField(max_length=255)
    sha = models.CharField(max_length=40)
    pusher_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return "%s%s" % (settings.BUILDSERVICE_BASE_URL, reverse('interface_build', args=[self.pk]))
