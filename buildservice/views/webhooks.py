"""Webhook views"""
import json

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from buildservice import tasks
from buildservice.errors import MissingToken
from buildservice.models import Webhook, Build, Repository
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required, signature_required


@login_required
@oauth_token_required
def add_webhook(request, repository_name):
    """
    Add a new webhook to a repository.
    """
    done = lambda: redirect('repository_detail', repository_name=repository_name)

    hook = Webhook.objects.filter(repository__name=repository_name).first()
    if hook and hook.active:
        return done()

    user = request.user
    token = user.oauth_token.value
    hook_url = Webhook.get_push_url()

    # get or create repo
    defaults = {}
    if request.GET.get('default_branch'):
        defaults['default_branch'] = request.GET.get('default_branch')
    repo, _ = Repository.objects.get_or_create(
        name=repository_name, defaults=defaults
    )
    repo.users.add(user)
    hook_id = github.create_webhook(token, repo.name, hook_url)
    # update or create Webhook, will work if we disabled and re-enabled
    Webhook.objects.update_or_create(
        repository=repo,
        defaults={"github_id": hook_id, "active": True}
    )

    return done()


@login_required
@oauth_token_required
def remove_webhook(request, repository_name):
    """
    Remove webhook from a repository.
    """
    done = lambda: redirect('home')

    hook = Webhook.objects.filter(repository__name=repository_name).first()
    if not hook:
        return done()

    token = request.user.oauth_token.value
    github.delete_webhook(token, repository_name, hook.github_id)
    hook.active = False
    hook.github_id = 0
    hook.save()

    return done()


@require_POST
@signature_required
@csrf_exempt
def push(request):
    """
    The Push webhook. It's directly hit by
    Github when commits are pushed.
    """
    try:
        event = request.META['HTTP_X_GITHUB_EVENT']
        payload = json.loads(request.body)
    except (KeyError, ValueError, TypeError):
        return HttpResponse()  # we don't care about errors

    if event == 'push' and not payload.get('deleted'):
        branch = payload['ref'].replace('refs/heads/', '')
        sha = payload['after']
        repo_name = payload['repository']['full_name']
        pusher = payload['pusher']['name']

        repository = get_object_or_404(Repository, name=repo_name)

        # atomically update the build count on the repo
        Repository.objects.filter(name=repo_name).update(build_count=F('build_count') + 1)
        repository.refresh_from_db()

        # try to find a token. If none, do nothing
        try:
            token = repository.get_token()
        except MissingToken:
            return HttpResponse()
        token = token.value

        build = Build(
            repository=repository, sha=sha, number=repository.build_count,
            pusher_name=pusher, branch=branch
        )
        build.save()
        github.create_status(
            token, repository.name, sha,
            state='pending', target_url=build.url
        )
        # launch build asynchronously
        tasks.run_build.delay(build.pk)

    return HttpResponse()
