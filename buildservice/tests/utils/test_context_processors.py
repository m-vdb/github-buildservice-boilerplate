from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase, override_settings

from buildservice.models import Repository, Webhook
from buildservice.utils import context_processors


@override_settings(BUILDSERVICE_APP_NAME='the_service')
class ContextProcessorsTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('ccc', password='ttt')
        self.repo1 = Repository.objects.create(name='zzzdummy/repo1')
        self.repo2 = Repository.objects.create(name='other/repo2')
        Webhook.objects.create(user=self.user, repository=self.repo1)
        Webhook.objects.create(user=self.user, repository=self.repo2)

    def test_base(self):
        req = HttpRequest()
        req.user = self.user
        self.assertEqual(context_processors.base(req), {
            'app_name': 'the_service',
            'user_repositories': [self.repo2, self.repo1]  # sorted
        })
