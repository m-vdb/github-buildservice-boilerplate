from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from mock import patch

from buildservice.models import Repository, Build
from buildservice.utils.testing import create_user_token


class MainViewsTestCase(TestCase):

    view_urls = [
        reverse('home'),
        reverse('repository_detail', args=('user/repo-super-duper', )),
        reverse('build_detail', args=('user/repo-super-duper', '1')),
        reverse('register_repositories')
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user('user', password='pwd')
        self.repo = Repository.objects.create(name='user/repo-super-duper')
        Build.objects.create(
            repository=self.repo,
            branch='the-branch',
            sha='abcdef1234567890',
            pusher_name='doe'
        )

    def test_login_required(self):
        for url in self.view_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.url, reverse('auth_login') + '?next=' + url)

    def test_token_required(self):
        self.client.login(username='user', password='pwd')
        for url in self.view_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.url, reverse('oauth_login'))

    def test_get_home(self):
        self.client.login(username='user', password='pwd')
        create_user_token(self.repo, self.user)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_get_repository_detail(self):
        self.client.login(username='user', password='pwd')
        create_user_token(self.repo, self.user)
        resp = self.client.get(reverse('repository_detail', args=('user/repo-super-duper', )))
        self.assertEqual(resp.status_code, 200)

    def test_get_build_detail(self):
        self.client.login(username='user', password='pwd')
        create_user_token(self.repo, self.user)
        resp = self.client.get(reverse('build_detail', args=('user/repo-super-duper', '1')))
        self.assertEqual(resp.status_code, 200)

    @patch('buildservice.utils.github.get_user_repos')
    def test_get_register_repositories(self, get_user_repos):
        self.client.login(username='user', password='pwd')
        token = create_user_token(self.repo, self.user)
        resp = self.client.get(reverse('register_repositories'))
        self.assertEqual(resp.status_code, 200)
        get_user_repos.assert_called_with(token.value)
