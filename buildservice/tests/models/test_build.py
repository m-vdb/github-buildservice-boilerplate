from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from mock import patch

from buildservice.errors import MissingToken, InvalidStatus
from buildservice.models import Build, Repository
from buildservice.utils.testing import create_user_token


@override_settings(BUILDSERVICE_BASE_URL='https://service.com')
class BuildTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('user', password='pwd')
        self.repo = Repository.objects.create(name='john-doe/repo')
        self.repo.users.add(self.user)
        self.build = Build.objects.create(
            repository=self.repo,
            pusher_name='john-doe',
            branch='master',
            sha='1234567890abcdef',
            number=125
        )

    def test_pusher_profile_url(self):
        self.assertEqual(self.build.pusher_profile_url, 'https://github.com/john-doe')

    def test_url(self):
        build_detail = reverse('build_detail', args=[self.repo.name, self.build.number])
        self.assertEqual(self.build.url, 'https://service.com%s' % build_detail)

    def test_is_success_yes(self):
        self.build.status = 'success'
        self.assertTrue(self.build.is_success)

    def test_is_success_no(self):
        self.assertFalse(self.build.is_success)

    def test_is_pending_yes(self):
        self.assertTrue(self.build.is_pending)

    def test_is_pending_no(self):
        self.build.status = 'errored'
        self.assertFalse(self.build.is_pending)

    def test_short_sha(self):
        self.assertEqual(self.build.short_sha, '1234567')

    def test_update_status_no_token(self):
        self.assertRaises(MissingToken, self.build.update_status, 'something')

    def test_update_status_bad_status(self):
        create_user_token(self.repo, self.user)
        self.assertRaises(InvalidStatus, self.build.update_status, 'something')
        self.build.refresh_from_db()
        self.assertEqual(self.build.status, 'pending')

    @patch('buildservice.utils.github.create_status')
    def test_update_status_ok(self, create_status):
        token = create_user_token(self.repo, self.user)
        self.build.update_status('success')
        self.build.refresh_from_db()
        self.assertEqual(self.build.status, 'success')
        create_status.assert_called_with(
            token.value, 'john-doe/repo', self.build.sha,
            state='success', target_url=self.build.url
        )
