"""Webhook views"""
import json

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from buildservice import tasks
from buildservice.models import Webhook, Build, OAuthToken, Repository
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required, signature_required


@login_required
@oauth_token_required
def create(request):
    """
    This view creates Webhook(s). Additionally,
    it handles webhook deactivation.
    """
    repos = set()
    for name, value in request.POST.iteritems():
        if name.startswith('repo_') and value == 'on':
            repos.add(name[5:])

    user = request.user
    token = user.oauth_token.value
    # compute the diff of repos
    repos_with_hook = set(
        user.webhook_set.filter(active=True).values_list('repository__name', flat=True)
    )
    new_repos = repos - repos_with_hook
    deactivated_repos = repos_with_hook - repos

    # create new hooks
    if new_repos:
        hook_url = Webhook.get_push_url()
        for repo in new_repos:
            repo, _ = Repository.objects.get_or_create(
                name=repo,
                defaults={
                    'default_branch': request.POST['default_branch_%s' % repo]
                }
            )
            hook_id = github.create_webhook(token, repo.name, hook_url)
            Webhook.objects.update_or_create(
                user=user, repository=repo,
                defaults={"github_id": hook_id, "active": True}
            )

    # deactivate some hooks
    if deactivated_repos:
        hooks = Webhook.objects.filter(repository__name__in=deactivated_repos)
        for hook in hooks:
            github.delete_webhook(token, hook.repository.name, hook.github_id)
        hooks.update(active=False, github_id=0)

    return redirect('interface_home')


@signature_required
@csrf_exempt
@require_POST
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

    if event == 'push':
        branch = payload['ref'].replace('refs/heads/', '')
        sha = payload['after']
        repo_name = payload['repository']['full_name']
        pusher = payload['pusher']['name']

        repository = get_object_or_404(Repository, name=repo_name)

        # atomically update the build count on the repo
        Repository.objects.filter(name=repo_name).update(build_count=F('build_count') + 1)
        repository.refresh_from_db()

        # try to find a token. If none, do nothing
        token = OAuthToken.objects.filter(user__webhook__repository=repository).first()
        if not token:
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
        tasks.execute_build.delay(build.pk)

    return HttpResponse()
