# github-buildservice-boilerplate
A boilerplate for creating a build service using Github

## Before installing

Setup a new [Github application](https://github.com/settings/applications/new). It is required to perform
Oauth. Be careful to define your _Authorization callback URL_ as follow: `<domain>/oauth`.


## TODO

### Working with Github

- create a [webhook on github](https://developer.github.com/v3/repos/hooks/#create-a-hook):
  - name: `"web"`
  - config: `{"url": "...", "content_type": "json", "secret": "...", "insecure_ssl": "0"}`
  - events: `[pull_request"]`

- configure our server properly to [receive webhooks](https://developer.github.com/v3/repos/hooks/#receiving-webhooks)
  - `X-GitHub-Event` header contains the event type
  - `X-Hub-Signature` header to verify signature (cf. secret above)
  - upon receiving a `pull_request` event, we want to check for 2 actions: `opened` and `synchronize` (see [payload example](https://developer.github.com/v3/activity/events/types/#webhook-payload-example-13))

- [POST on Status API](https://developer.github.com/v3/repos/statuses/#create-a-status):
  - should post when starting to do something
  - should post when finished to do something

### The server

It should be a simple webserver:
- one view (simple Django form) to create the webhook
- [implement OAUTH](https://developer.github.com/v3/oauth/#web-application-flow) (using [this](https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#web-app-example-of-oauth-2-web-application-flow))
- one route that will receive the webhook
- [one Redis-powered async task runner](https://github.com/nvie/rq)
  - before launching a task, POST a `"pending"` status on the Status API
  - at the end of the task, POST either a `"success"`, `"failure"` or `"error"` status
