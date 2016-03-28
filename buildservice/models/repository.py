"""The Repository model"""
from django.db import models


class Repository(models.Model):
    """
    A database record containing a repository.
    """
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
