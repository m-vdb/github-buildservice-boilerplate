# github-buildservice-boilerplate
A boilerplate for creating a build service using Github

## Before installing

Setup a new [Github application](https://github.com/settings/applications/new). It is required to perform
Oauth. Be careful to define your _Authorization callback URL_ as follow: `<domain>/oauth`.


## The app

The home view, contains a list of the user's Github projects. The using [OAuth strategy](https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#web-app-example-of-oauth-2-web-application-flow) relies on 2 views:
- `/oauth/login`: starting point of oauth, redirects to Github.
- `/oauth/callback`: oauth callback route, will store the access token in database.

Finally, the application relies on 2 other routes. The first is `/webhooks/create`, used after a submit on the homepage form to create a webhook. This route will have two effects: [create the webhook](https://developer.github.com/v3/repos/hooks/#create-a-hook) onto Github API and save a model representing it in database. The second route is `/webhook/pull_request`, [hit](https://developer.github.com/v3/repos/hooks/#receiving-webhooks) whenever a Pull Request is submitted on the user's repository. It'll [POST on Status API](https://developer.github.com/v3/repos/statuses/#create-a-status), first a `pending` status, then a `success`, `failure` or `error` status.


## Under the hood


TODO