from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from buildservice.models import Webhook
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required


@oauth_token_required
@login_required
def create(request):
    repos = set()
    for name, value in request.POST.iteritems():
        if name.startswith('repo_') and value == 'on':
            repos.add(name[5:])

    repos_with_hook = request.user.webhook_set.filter(active=True).values_list('repository', flat=True)
    new_repos = repos.difference(repos_with_hook)
    if new_repos:
        token = request.user.oauth_token
        hooks = []
        hook_url = request.build_absolute_uri(reverse('webhooks_pull_request'))
        for repo in new_repos:
            hook_id = github.create_webhook(token.value, repo, hook_url)
            hooks.append(Webhook(repository=repo, github_id=hook_id))

        request.user.webhook_set.add(*hooks)

    return redirect('home')


def pull_request(request):
    # TODO
    # - 'X-GitHub-Event' header contains the event type
    # - 'X-Hub-Signature' header to verify signature (cf. secret above)
    # - upon receiving a 'pull_request' event, we want to check for 2 actions: 'opened' and 'synchronize'
    return HttpResponse()
