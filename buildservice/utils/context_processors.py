"""
This module contains context processors for
Django templates. See Django's documentation
for more information.
"""
from operator import attrgetter

from django.conf import settings


def base(request):  # pylint: disable=unused-argument
    """
    A base context processor that return
    app-wide settings.
    """
    hooks = request.user.webhook_set.filter(active=True)
    return {
        "app_name": settings.BUILDSERVICE_APP_NAME,
        "user_repositories": sorted((hook.repository for hook in hooks), key=attrgetter('name'))
    }
