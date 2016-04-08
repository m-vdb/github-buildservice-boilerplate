"""buildservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from buildservice.views import interface, oauth, webhooks


urlpatterns = [  # pylint: disable=invalid-name
    # UI
    url(r'^$', interface.home, name='interface_home'),
    url(
        r'^repositories/(?P<repository_name>[^/]+/[^/]+)$',
        interface.repository_builds,
        name="repository_builds"
    ),
    url(
        r'^repositories/(?P<repository_name>[^/]+/[^/]+)/builds/(?P<build_number>\d+)$',
        interface.build_detail,
        name='interface_build'
    ),
    url(r'^repositories/register$', interface.register_repositories, name='register_repositories'),
    url(r'^login/$', auth_views.login, name='auth_login'),
    url(
        r'^badge/(?P<repo_name>[^\:]+/[^\:]+)(?:\:(?P<branch_name>.+))?\.svg$',
        interface.badge,
        name='interface_badge'
    ),
    # OAuth
    url(r'^oauth/login$', oauth.login, name='oauth_login'),
    url(r'^oauth/callback$', oauth.callback, name='oauth_callback'),
    # Webhooks
    url(r'^webhooks$', webhooks.create, name='webhooks_create'),
    url(r'^webhooks/push$', webhooks.push, name='webhooks_push'),
]
