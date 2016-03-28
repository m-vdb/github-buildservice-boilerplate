"""
This module contains context processors for
Django templates. See Django's documentation
for more information.
"""
from django.conf import settings


def base(request):  # pylint: disable=unused-argument
    """
    A base context processor that return
    app-wide settings.
    """
    return {
        "app_name": settings.BUILDSERVICE_APP_NAME,
    }
