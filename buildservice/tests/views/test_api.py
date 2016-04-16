from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings
from mock import patch

from buildservice.models import Build, Repository
from buildservice.utils.testing import create_user_token


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

    def test_post_bad_status(self):
        create_user_token(self.repo)
        resp = self.client.post(
            self.url + '?api_key=the_key', data='{"status": "something"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'error': 'Invalid status.'})

    @patch('buildservice.utils.github.create_status')
    def test_post_ok(self, create_status):
        token = create_user_token(self.repo)
        resp = self.client.post(
            self.url + '?api_key=the_key', data='{"status": "success"}',
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.build.refresh_from_db()
        self.assertTrue(self.build.is_success)
        create_status.assert_called_with(
            token.value, 'my/repo', self.build.sha,
            state='success', target_url=self.build.url
        )
