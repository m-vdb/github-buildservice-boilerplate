"""The Repository model"""
from django.db import models


class Repository(models.Model):
    """
    A database record containing a repository.
    """
    name = models.CharField(max_length=255, unique=True)
    default_branch = models.CharField(max_length=255, default='master')
    build_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
