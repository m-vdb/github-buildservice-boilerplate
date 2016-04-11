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
    user = request.user
    # duck-typing
    hooks = user.webhook_set.filter(active=True) if hasattr(user, 'webhook_set') else []
    return {
        "app_name": settings.BUILDSERVICE_APP_NAME,
        "user_repositories": sorted((hook.repository for hook in hooks), key=attrgetter('name'))
    }
