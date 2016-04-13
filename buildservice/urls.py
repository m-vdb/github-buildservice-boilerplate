"""Url configuration file"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm

from buildservice.views import api, auth, main, oauth, webhooks


urlpatterns = [  # pylint: disable=invalid-name
    # UI
    url(r'^$', main.home, name='home'),
    url(
        r'^repositories/(?P<repository_name>[^/]+/[^/]+)$',
        main.repository_detail,
        name="repository_detail"
    ),
    url(
        r'^repositories/(?P<repository_name>[^/]+/[^/]+)/builds/(?P<build_number>\d+)$',
        main.build_detail,
        name='build_detail'
    ),
    url(r'^repositories/register$', main.register_repositories, name='register_repositories'),
    url(
        r'^badge/(?P<repo_name>[^\:]+/[^\:]+)(?:\:(?P<branch_name>.+))?\.svg$',
        main.badge,
        name='repository_badge'
    ),

    # auth
    url(r'^register/$', auth.RegisterView.as_view(
        template_name='registration/register.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name='auth_register'),
    url(r'^login/$', auth_views.login, name='auth_login'),
    url(r'^logout/$', auth_views.logout_then_login, name='auth_logout'),

    # OAuth
    url(r'^oauth/login$', oauth.login, name='oauth_login'),
    url(r'^oauth/callback$', oauth.callback, name='oauth_callback'),

    # Webhooks
    url(r'^webhooks$', webhooks.create, name='webhooks_create'),
    url(r'^webhooks/push$', webhooks.push, name='webhooks_push'),

    # API
    url(
        r'^api/repository/(?P<repository_name>[^/]+/[^/]+)/builds/(?P<build_number>\d+)/status$',
        api.update_build_status,
        name='api_build_status'
    ),
]
