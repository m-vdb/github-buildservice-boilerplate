from django.conf import settings
from github3 import login


def get_user_repos(token):
    """
    Get all user repositories using a OAuth Token.
    """
    if settings.DEBUG and settings.GITHUB_USER_ID:
        gh = login(settings.GITHUB_USER_ID, password=settings.GITHUB_USER_PASSWORD)
    else:
        gh = login(token)
    return gh.iter_repos()
