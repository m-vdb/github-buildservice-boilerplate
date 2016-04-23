from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from buildservice.models import Webhook, Repository


@override_settings(BUILDSERVICE_BASE_URL='https://service.com')
class WebhookTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('zzz', password='ttt')
        self.repo = Repository.objects.create(name='john-doe/repo')
        self.repo.users.add(self.user)
        self.webhook = Webhook.objects.create(repository=self.repo)

    def test_get_push_url(self):
        push_url = reverse('webhooks_push')
        self.assertEqual(self.webhook.get_push_url(), 'https://service.com%s' % push_url)
