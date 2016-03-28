"""Asynchronous tasks"""
from django_rq import job

from buildservice.errors import MissingToken
from buildservice.models import Build, OAuthToken
from buildservice.utils import github


@job
def execute_build(build_id):
    """
    Execute a given build.
    """
    build = Build.objects.get(pk=build_id)
    token = OAuthToken.objects.filter(user__webhook__repository=build.repository).first()
    if not token:
        raise MissingToken('Cannot find token for build %s' % build_id)

    # TODO: do stuff

    status = 'success'
    build.status = status
    build.save()
    github.create_status(
        token.value, build.repository, build.sha,
        state=status, target_url=build.url
    )
