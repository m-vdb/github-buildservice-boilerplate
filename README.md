# github-buildservice-boilerplate

[![Circle CI](https://circleci.com/gh/m-vdb/github-buildservice-boilerplate.svg?style=shield&circle-token=005fe273ea45c0f445bddbf53f2f90594dcfce91)](https://circleci.com/gh/m-vdb/github-buildservice-boilerplate)
[![Buildservice](https://buildservice.maxvdb.com/badge/m-vdb/github-buildservice-boilerplate.svg)](https://buildservice.maxvdb.com/repositories/m-vdb/github-buildservice-boilerplate)
[![Coverage Status](https://coveralls.io/repos/github/m-vdb/github-buildservice-boilerplate/badge.svg?branch=master)](https://coveralls.io/github/m-vdb/github-buildservice-boilerplate?branch=master)

A boilerplate for creating a build service using Github.
*Demo is available at https://buildservice.maxvdb.com/.*


## Features

This web app makes it possible for users to register their Github repositories and perform builds on each
code push. The definition of "build" is up to you. Here is the skeleton:

- a basic web application with the following views:
  - home view: lists your available repositories
  - repository view: lists the latest builds of your repository
  - build view: shows the build detail
  - register repository view: allows you to register one or several views
- a badge view: a simple endpoint to retrieve the SVG badge of a repository, like [this one](https://buildservice.maxvdb.com/badge/m-vdb/github-buildservice-boilerplate.svg)
- a simple web API:
  - a webhook that receives calls from Github
  - an internal endpoint that accepts build status changes - *useful in case an other service runs the builds*
- an asynchronous task system based on [django-rq](https://github.com/ui/django-rq) - *useful in case this service runs the builds*

## Project Scope

This project isn't a full build service. It doesn't tackle:
- containerization
- build restart
- per-branch views

You can use this boilerplate to create the central node of a more complex architecture.

This project doesn't either provide a full UI - no fancy front-end framework here, just plain [Django views](https://docs.djangoproject.com/en/1.9/topics/http/views/).

## Installation and setup

You first need to create a [Github application](https://github.com/settings/applications/new). The app will ask for user permissions (on behalf of the Github application) and save tokens in database for later use. Be careful to define your _Authorization callback URL_ as follow: `https://<domain>/oauth/callback`. You'll need HTTPS.

## Settings

- `DEBUG`: set to `True` to enable Django debug
- `DATABASE_URL`: your main database URI, e.g. `postgres://<user>:<passsword>@<host>:5432/<database>`
- `REDIS_URL`: your broker URI, useful fo asynchronous tasks (used by _django-rq_), e.g. `127.0.0.1:6379`
- `SECRET_KEY`: required by Django for cryptographic signing
- `GITHUB_CLIENT_ID`: your Github application id
- `GITHUB_CLIENT_SECRET`: your Github application id
- `GITHUB_HOOK_SECRET`: a hook secret, useful for webhook authentication
- `BUILDSERVICE_BASE_URL`: the URL of your website, example: `https://buildservice.maxvdb.com`
- `BUILDSERVICE_APP_NAME`: the name of your website

While debugging locally, you might want to use `GITHUB_USER_ID` and `GITHUB_USER_PASSWORD` instead of the
`GITHUB_CLIENT_*` credentials.

## Useful links & inspiration

- [CircleCI](https://circleci.com/)
- [Shields.io](http://shields.io/)
- [Django](https://docs.djangoproject.com/en/1.9/)
- [Dokku](http://dokku.viewdocs.io/dokku/)
- [Bootstrap](http://getbootstrap.com/)
- [Google Material Icons](https://design.google.com/icons/)


## Troubleshooting

### My repository badge doesn't update

Github _aggressively_ caches content. Make sure to have ETags enabled on your webserver.
If you're using [nginx](https://www.nginx.com/), ETags are ignored if the content is gzipped. Don't forget to remove the SVG mimetype from the `gzip_types` directive.
