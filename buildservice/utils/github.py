"""Github utils method"""
from django.conf import settings
import github3

from buildservice.errors import CannotCreateHook


def get_user_repos(token):
    """
    Get all user repositories using a OAuth Token.
    """
    client = _github_login(token)
    return client.iter_repos()


def create_webhook(token, repo, url):
    """
    Create a webhook for the repo.
    """
    client = _github_login(token)
    owner, repository = repo.split('/')
    repo = client.repository(owner, repository)
    hook = repo.create_hook(
        settings.GITHUB_HOOK_NAME,
        {
            "url": url, "content_type": "json",
            "secret": settings.GITHUB_HOOK_SECRET,
            "insecure_ssl": "0"
        },
        events=settings.GITHUB_HOOK_EVENTS,
        active=True
    )
    if not hook:
        raise CannotCreateHook("Cannot create hook for repo %s/%s" % (owner, repository))
    return hook.id


def delete_webhook(token, repo, hook_id):
    """
    Delete a webhook from a repo.
    """
    client = _github_login(token)
    owner, repository = repo.split('/')
    repo = client.repository(owner, repository)
    hook = repo.hook(hook_id)
    if hook:
        hook.delete()


def create_status(token, repo, sha, state, **kwargs):
    """
    Create a Status on the repo, for the given sha.
    """
    client = _github_login(token)
    owner, repository = repo.split('/')
    repo = client.repository(owner, repository)
    repo.create_status(
        sha, state,
        context=settings.BUILDSERVICE_STATUS_CONTEXT,
        **kwargs
    )


def _github_login(token):
    """
    Connect to github, using token in prod and
    login/password in dev.
    """
    if settings.DEBUG and settings.GITHUB_USER_ID:
        return github3.login(settings.GITHUB_USER_ID, password=settings.GITHUB_USER_PASSWORD)

    return github3.login(token=token)
