from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect


@login_required
def create(request):
    # TODO:
    # create the webhooks + mark them as created in DB
    # { "name: "web",
    #   "config: {"url": "...", "content_type": "json", "secret": "...", "insecure_ssl": "0"},
    #   "events: [pull_request"]}
    return redirect('home')


def pull_request(request):
    # TODO
    # - 'X-GitHub-Event' header contains the event type
    # - 'X-Hub-Signature' header to verify signature (cf. secret above)
    # - upon receiving a 'pull_request' event, we want to check for 2 actions: 'opened' and 'synchronize'
    return HttpResponse()
