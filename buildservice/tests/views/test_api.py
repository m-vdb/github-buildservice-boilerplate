from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings
from mock import patch

from buildservice.models import Build, Repository, OAuthToken, Webhook


@override_settings(BUILDSERVICE_API_KEY='the_key')
class UpdateBuildStatusTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.dummy_url = reverse('api_build_status', args=('unknown/repo', '42'))
        self.repo = Repository.objects.create(name='my/repo')
        self.build = Build.objects.create(
            repository=self.repo, branch='master',
            sha='0000', pusher_name='mvdb'
        )
        self.url = reverse('api_build_status', args=('my/repo', self.build.number))

    def test_get(self):
        resp = self.client.get(self.dummy_url)
        self.assertEqual(resp.status_code, 405)

    def test_post_not_json(self):
        resp = self.client.post(
            self.dummy_url, data='hello',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_missing_status(self):
        resp = self.client.post(
            self.dummy_url + '?api_key=the_key', data='{"key": "value"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'error': 'Missing status field.'})

    def test_post_json_not_dict(self):
        resp = self.client.post(
            self.dummy_url + '?api_key=the_key', data='[1, 2, 3]',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'error': 'Missing status field.'})

    def test_post_no_api_key(self):
        resp = self.client.post(
            self.dummy_url, data='{"status": "success"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 401)

    def test_post_unknown_build(self):
        resp = self.client.post(
            self.dummy_url + '?api_key=the_key', data='{"status": "success"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 404)

    def test_post_missing_token(self):
        resp = self.client.post(
            self.url + '?api_key=the_key', data='{"status": "something"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'error': 'No token.'})

    def setup_user(self):
        user_class = get_user_model()
        user = user_class.objects.create_user('uuu', password='ttt')
        OAuthToken.objects.create(user=user, value='the_token')
        Webhook.objects.create(user=user, repository=self.repo)

    def test_post_bad_status(self):
        self.setup_user()
        resp = self.client.post(
            self.url + '?api_key=the_key', data='{"status": "something"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'error': 'Invalid status.'})

    @patch('buildservice.utils.github.create_status')
    def test_post_ok(self, create_status):
        self.setup_user()
        resp = self.client.post(
            self.url + '?api_key=the_key', data='{"status": "success"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.build.refresh_from_db()
        self.assertTrue(self.build.is_success)
        create_status.assert_called_with(
            'the_token', 'my/repo', self.build.sha,
            state='success', target_url=self.build.url
        )
