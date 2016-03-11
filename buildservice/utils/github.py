from django.conf import settings
from github3 import login


def get_user_repos(token):
    """
    Get all user repositories using a OAuth Token.
    """
    gh = _github_login(token)
    return gh.iter_repos()


def create_webhook(token, repo, url):
    """
    Create a webhook for the repo.
    """
    gh = _github_login(token)
    owner, repository = repo.split('/')
    repo = gh.repository(owner, repository)
    hook = repo.create_hook(
        settings.GITHUB_HOOK_NAME,
        {"url": url, "content_type": "json", "secret": settings.GITHUB_HOOK_SECRET, "insecure_ssl": "0"},
        events=settings.GITHUB_HOOK_EVENTS,
        active=True
    )
    return hook.id


def _github_login(token):
    """
    Connect to github, using token in prod and
    login/password in dev.
    """
    if settings.DEBUG and settings.GITHUB_USER_ID:
        return login(settings.GITHUB_USER_ID, password=settings.GITHUB_USER_PASSWORD)

    return login(token=token)
