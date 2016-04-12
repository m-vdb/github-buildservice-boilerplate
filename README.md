# github-buildservice-boilerplate

[![Circle CI](https://circleci.com/gh/m-vdb/github-buildservice-boilerplate.svg?style=shield&circle-token=005fe273ea45c0f445bddbf53f2f90594dcfce91)](https://circleci.com/gh/m-vdb/github-buildservice-boilerplate)
[![Buildservice](https://buildservice.maxvdb.com/badge/m-vdb/github-buildservice-boilerplate.svg)](https://buildservice.maxvdb.com/repositories/m-vdb/github-buildservice-boilerplate)

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
  - an internal endpoint that accepts build status changes - *useful in case an other service runs builds*
- an asynchronous task system based on [django-rq](https://github.com/ui/django-rq) - *useful in case this service runs builds*

## What this project doesn't cover

This project isn't a full build service. It doesn't tackle containerization of the builds. You can use this service as the center part of a full service; it will receive calls from Github and may communicate with your other micro-services.

This project doesn't either cover the UI part in full - no fancy front-end framework here, just plain [Django views](https://docs.djangoproject.com/en/1.9/topics/http/views/).

## Installation and setup

You first need to setup a new [Github application](https://github.com/settings/applications/new). All the tokens will be granted for this application. Be careful to define your _Authorization callback URL_ as follow: `https://<domain>/oauth/callback`. You'l need HTTPS.

## Settings

TODO

## Useful links & inspiration

- [CircleCI](https://circleci.com/)
- [Shields.io](http://shields.io/)
- [Django](https://docs.djangoproject.com/en/1.9/)
- [Dokku](http://dokku.viewdocs.io/dokku/)
