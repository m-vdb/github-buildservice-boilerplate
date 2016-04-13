"""The API views."""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from buildservice.errors import MissingToken
from buildservice.models import Build
from buildservice.utils.decorators import require_json


@require_json
@require_POST
def update_build_status(request, repository_name, build_number):
    """
    Update a build status. Useful when another
    separate micro-service runs the builds.
    """
    try:
        status = request.json['status']
    except (TypeError, KeyError):
        return JsonResponse({'error': 'missing status field.'}, status=400)

    build = get_object_or_404(Build, repository__name=repository_name, number=build_number)
    try:
        build.update_status(status)
    except MissingToken:
        return JsonResponse({'error': 'no token'}, status=400)

    return JsonResponse({})
