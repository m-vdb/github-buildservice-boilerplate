from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings
from mock import patch

from buildservice.models import OAuthToken


@override_settings(GITHUB_CLIENT_SECRET='the_secret')
class OAuthViewsTestCase(TestCase):

    login_url = reverse('oauth_login')
    callback_url = reverse('oauth_callback')

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user('user', password='pwd')

    def test_get_login_anonymous(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('auth_login') + '?next=' + self.login_url)

    @patch(
        'requests_oauthlib.OAuth2Session.authorization_url',
        return_value=('https://github.com', 'the_state')
    )
    def test_get_login_ok(self, authorization_url):
        self.assertTrue(self.client.login(username='user', password='pwd'))
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 302)
        authorization_url.assert_called_with(settings.GITHUB_AUTHORIZATION_BASE_URL)
        self.assertEqual(resp.url, 'https://github.com')
        self.assertEqual(resp.wsgi_request.session['oauth_state'], 'the_state')

    def test_callback_anonymous(self):
        resp = self.client.get(self.callback_url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('auth_login') + '?next=' + self.callback_url)

    def test_callback_token_missing_oauth_state(self):
        self.assertTrue(self.client.login(username='user', password='pwd'))
        resp = self.client.get(self.callback_url)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Missing oauth state.')

    @patch('requests_oauthlib.OAuth2Session.fetch_token', return_value='token')
    def test_callback_token_malformatted(self, fetch_token):
        self.assertTrue(self.client.login(username='user', password='pwd'))
        session = self.client.session
        session['oauth_state'] = 'the_state'
        session.save()
        resp = self.client.get(self.callback_url)
        fetch_token.assert_called_with(
            settings.GITHUB_TOKEN_URL,
            client_secret='the_secret',
            authorization_response=resp.wsgi_request.build_absolute_uri()
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Cannot read access_token.')

    @patch('requests_oauthlib.OAuth2Session.fetch_token', return_value={})
    def test_callback_token_malformatted_bis(self, fetch_token):
        self.assertTrue(self.client.login(username='user', password='pwd'))
        session = self.client.session
        session['oauth_state'] = 'the_state'
        session.save()
        resp = self.client.get(self.callback_url)
        fetch_token.assert_called_with(
            settings.GITHUB_TOKEN_URL,
            client_secret='the_secret',
            authorization_response=resp.wsgi_request.build_absolute_uri()
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Cannot read access_token.')

    @patch('requests_oauthlib.OAuth2Session.fetch_token', return_value={'access_token': 'abc'})
    def test_callback_ok(self, fetch_token):
        self.assertTrue(self.client.login(username='user', password='pwd'))
        session = self.client.session
        session['oauth_state'] = 'the_state'
        session.save()
        resp = self.client.get(self.callback_url)
        fetch_token.assert_called_with(
            settings.GITHUB_TOKEN_URL,
            client_secret='the_secret',
            authorization_response=resp.wsgi_request.build_absolute_uri()
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')
        token = OAuthToken.objects.get(user=self.user)
        self.assertEqual(token.value, 'abc')
