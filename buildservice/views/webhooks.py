from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect

from buildservice.models import Webhook
from buildservice.utils import github
from buildservice.utils.decorators import oauth_token_required


@login_required
@oauth_token_required
def create(request):
    repos = set()
    for name, value in request.POST.iteritems():
        if name.startswith('repo_') and value == 'on':
            repos.add(name[5:])

    token = request.user.oauth_token.value
    # compute the diff of repos
    repos_with_hook = set(request.user.webhook_set.filter(active=True).values_list('repository', flat=True))
    new_repos = repos - repos_with_hook
    deactivated_repos = repos_with_hook - repos

    # create new hooks
    if new_repos:
        hook_url = request.build_absolute_uri(reverse('webhooks_pull_request'))
        for repo in new_repos:
            hook_id = github.create_webhook(token, repo, hook_url)
            Webhook.objects.update_or_create(
                user=request.user, repository=repo,
                defaults={"github_id": hook_id, "active": True}
            )

    # deactivate some hooks
    if deactivated_repos:
        hooks = Webhook.objects.filter(repository__in=deactivated_repos)
        for hook in hooks:
            github.delete_webhook(token, hook.repository, hook.github_id)
        hooks.update(active=False, github_id=0)

    return redirect('interface_home')


def pull_request(request):
    # TODO
    # - 'X-GitHub-Event' header contains the event type
    # - 'X-Hub-Signature' header to verify signature (cf. secret above)
    # - upon receiving a 'pull_request' event, we want to check for 2 actions: 'opened' and 'synchronize'
    return HttpResponse()
