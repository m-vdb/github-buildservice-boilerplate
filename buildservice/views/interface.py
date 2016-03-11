from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect


# TODO: setup django.contrib.auth
@login_required
def home(request):
    # TODO:
    # if not authorized, redirect to oauth_login
    # else, list user repos
    return render_to_response("home.html")
