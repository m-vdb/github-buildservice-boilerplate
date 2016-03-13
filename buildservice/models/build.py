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
        return settings.GITHUB_USER_PROFILE_URL % self.pusher_name

    @property
    def url(self):
        return reverse('interface_build', (self.pk, ))
