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


urlpatterns = [
    # UI
    url(r'^$', interface.home, name='interface_home'),
    url(r'^login/$', auth_views.login, name='auth_login'),
    # OAuth
    url(r'^oauth/login$', oauth.login, name='oauth_login'),
    url(r'^oauth/callback$', oauth.callback, name='oauth_callback'),
    # Webhooks
    url(r'^webhooks/create$', webhooks.create, name='webhooks_create'),
    url(r'^webhooks/pull-request$', webhooks.pull_request, name='webhooks_pull_request'),
]
