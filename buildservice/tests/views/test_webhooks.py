import hashlib
import hmac
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings
from mock import patch

from buildservice.models import Repository, Build
from buildservice.utils.testing import create_user_token


class CreateWebhooksTestCase(TestCase):
    pass


@override_settings(GITHUB_HOOK_SECRET='ssssecret')
class PushWebhooksTestCase(TestCase):

    url = reverse('webhooks_push')
    payload = {
        'ref': 'refs/heads/branch-name',
        'after': '1234567890abcdef1234567890abcdef12345678',
        'repository': {
            'full_name': 'user/great-repo'
        },
        'pusher': {
            'name': 'big-user'
        }
    }

    def setUp(self):
        self.client = Client()

    def test_get(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    def test_post_no_signature(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 401)

    def test_post_bad_signature(self):
        signature = "sha1=%s" % hmac.new('ssssecret', 'toto', hashlib.sha1).hexdigest()
        resp = self.client.post(self.url, HTTP_X_HUB_SIGNATURE=signature)
        self.assertEqual(resp.status_code, 401)

    def test_post_no_github_event(self):
        signature = "sha1=%s" % hmac.new('ssssecret', '{}', hashlib.sha1).hexdigest()
        resp = self.client.post(
            self.url, data='{}',
            HTTP_X_HUB_SIGNATURE=signature,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)

    def do_proper_post(self, data='', event='push'):
        if data:
            data = json.dumps(data)
        signature = "sha1=%s" % hmac.new('ssssecret', data, hashlib.sha1).hexdigest()
        return self.client.post(
            self.url,
            data=data,
            HTTP_X_HUB_SIGNATURE=signature,
            HTTP_X_GITHUB_EVENT=event,
            content_type="application/json"
        )

    def test_post_no_json(self):
        resp = self.do_proper_post()
        self.assertEqual(resp.status_code, 200)

    @patch('buildservice.tasks.run_build.delay')
    @patch('buildservice.utils.github.create_status')
    def test_post_other_event(self, create_status, run_build):
        resp = self.do_proper_post(event='pull')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(create_status.called)
        self.assertFalse(run_build.called)

    def test_post_unknown_repo(self):
        resp = self.do_proper_post(data=self.payload)
        self.assertEqual(resp.status_code, 404)

    @patch('buildservice.tasks.run_build.delay')
    @patch('buildservice.utils.github.create_status')
    def test_post_missing_token(self, create_status, run_build):
        repo = Repository.objects.create(name='user/great-repo')
        resp = self.do_proper_post(data=self.payload)
        self.assertEqual(resp.status_code, 200)
        repo.refresh_from_db()
        self.assertEqual(repo.build_count, 1)
        self.assertFalse(create_status.called)
        self.assertFalse(run_build.called)

    @patch('buildservice.tasks.run_build.delay')
    @patch('buildservice.utils.github.create_status')
    def test_post_ok(self, create_status, run_build):
        repo = Repository.objects.create(name='user/great-repo')
        token = create_user_token(repo)
        resp = self.do_proper_post(data=self.payload)
        self.assertEqual(resp.status_code, 200)
        repo.refresh_from_db()
        self.assertEqual(repo.build_count, 1)
        build = Build.objects.get(repository=repo, number=1)
        self.assertEqual(build.sha, '1234567890abcdef1234567890abcdef12345678')
        self.assertEqual(build.pusher_name, 'big-user')
        self.assertEqual(build.branch, 'branch-name')
        create_status.assert_called_with(
            token.value, repo.name, build.sha,
            state='pending', target_url=build.url
        )
        run_build.assert_called_with(build.pk)
