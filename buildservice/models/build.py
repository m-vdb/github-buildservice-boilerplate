from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse


class Build(models.Model):
    """
    A database record containing a repository build.
    """
    repository = models.CharField(max_length=255)
    sha = models.CharField(max_length=40)
    pull_request_id = models.IntegerField(default=0)
    pull_request_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def pull_request_url(self):
        return settings.GITHUB_PULL_REQUEST_BASE_URL % {
            'repository': self.repository,
            'number': pull_request_number
        }

    @property
    def url(self):
        return reverse('interface_build', (self.pk, ))
