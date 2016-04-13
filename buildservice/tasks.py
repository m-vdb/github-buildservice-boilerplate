"""Asynchronous tasks"""
from django_rq import job

from buildservice.models import Build


@job
def execute_build(build_id):
    """
    Execute a given build.
    """
    build = Build.objects.get(pk=build_id)

    # when build complete...
    status = 'success'
    build.update_status(status)
