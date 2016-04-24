import hashlib
import hmac
import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings
from mock import patch

from buildservice.models import Repository, Build, Webhook
from buildservice.utils.testing import create_user_token


class AddWebhooksTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user('user', password='pwd')
        self.repo = Repository.objects.create(name='user/repo-mega-duper')
        self.repo.users.add(self.user)
        self.url = reverse('webhooks_add', args=(self.repo.name, ))
        self.redirect_url = reverse('repository_detail', args=(self.repo.name, ))

    def test_login_required(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('auth_login') + '?next=' + self.url)

    def test_token_required(self):
        self.client.login(username='user', password='pwd')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('oauth_login'))

    @patch('buildservice.utils.github.create_webhook')
    def test_get_hook_active(self, create_webhook):
        Webhook.objects.create(repository=self.repo, github_id=8082)
        self.client.login(username='user', password='pwd')
        create_user_token(self.user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, self.redirect_url)
        self.assertFalse(create_webhook.called)

    @patch('buildservice.utils.github.create_webhook', return_value=26192)
    def test_get_hook_inactive(self, create_webhook):
        hook = Webhook.objects.create(repository=self.repo, active=False)
        self.client.login(username='user', password='pwd')
        token = create_user_token(self.user)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, self.redirect_url)
        create_webhook.assert_called_with(token.value, self.repo.name, Webhook.get_push_url())
        hook.refresh_from_db()
        self.assertTrue(hook.active)
        self.assertEqual(hook.github_id, 26192)

    @patch('buildservice.utils.github.create_webhook', return_value=26192)
    def check_hook_creation(self, branch, create_webhook=None):
        url = self.url
        if branch != 'master':
            url += '?default_branch=' + branch

        self.repo.delete()
        self.client.login(username='user', password='pwd')
        token = create_user_token(self.user)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, self.redirect_url)
        create_webhook.assert_called_with(token.value, self.repo.name, Webhook.get_push_url())
        repo = Repository.objects.get(name='user/repo-mega-duper')
        self.assertEqual(repo.default_branch, branch)
        hook = Webhook.objects.get(repository=repo)
        self.assertTrue(hook.active)
        self.assertEqual(hook.github_id, 26192)

    def test_get_hook_no_repo(self):
        self.check_hook_creation('master')

    def test_get_hook_no_repo_default_branch(self):
        self.check_hook_creation('some-branch')


class RemoveWebhooksTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user('user', password='pwd')
        self.repo = Repository.objects.create(name='user/repo-mega-duper')
        self.repo.users.add(self.user)
        self.url = reverse('webhooks_remove', args=(self.repo.name, ))
        self.redirect_url = reverse('home')

    def test_login_required(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('auth_login') + '?next=' + self.url)

    def test_token_required(self):
        self.client.login(username='user', password='pwd')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('oauth_login'))

    def test_get_no_hook(self):
        self.client.login(username='user', password='pwd')
        create_user_token(self.user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, self.redirect_url)

    @patch('buildservice.utils.github.delete_webhook')
    def test_get_ok(self, delete_webhook):
        hook = Webhook.objects.create(repository=self.repo, github_id=127686)
        self.client.login(username='user', password='pwd')
        token = create_user_token(self.user)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, self.redirect_url)
        delete_webhook.assert_called_with(token.value, self.repo.name, hook.github_id)
        hook.refresh_from_db()
        self.assertFalse(hook.active)
        self.assertEqual(hook.github_id, 0)


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

    @patch('buildservice.tasks.run_build.delay')
    @patch('buildservice.utils.github.create_status')
    def test_post_deleted(self, create_status, run_build):
        resp = self.do_proper_post(data={'deleted': True})
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
        user = get_user_model().objects.create_user('user', password='pwd')
        repo.users.add(user)
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
        user = get_user_model().objects.create_user('user', password='pwd')
        repo.users.add(user)
        token = create_user_token(user, repo)
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
