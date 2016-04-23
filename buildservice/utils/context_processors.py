"""
This module contains context processors for
Django templates. See Django's documentation
for more information.
"""
from operator import attrgetter

from django.conf import settings

from .views import get_user_active_repositories


def base(request):  # pylint: disable=unused-argument
    """
    A base context processor that return
    app-wide settings.
    """
    return {
        "app_name": settings.BUILDSERVICE_APP_NAME,
        "user_repositories": sorted(
            get_user_active_repositories(request.user),
            key=attrgetter('name')
        )
    }
