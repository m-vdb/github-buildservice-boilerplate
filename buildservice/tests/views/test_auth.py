from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client


class RegisterViewTestCase(TestCase):

    url = reverse('auth_register')

    def setUp(self):
        self.client = Client()
        get_user_model().objects.create_user('aaa', password='ttt')

    def test_get_already_authenticated(self):
        self.assertTrue(self.client.login(username='aaa', password='ttt'))
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')

    def test_get_ok(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post_already_authenticated(self):
        self.assertTrue(self.client.login(username='aaa', password='ttt'))
        resp = self.client.post(self.url, {'username': 'bbb', 'password1': 'p', 'password2': 'p'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')
        self.assertIsNone(get_user_model().objects.filter(username='bbb').first())

    def test_post_ok(self):
        resp = self.client.post(self.url, {
            'username': 'ccc',
            'password1': 'the is a password',
            'password2': 'the is a password'
        })
        self.assertEqual(resp.status_code, 302)
        new_user = get_user_model().objects.filter(username='ccc').first()
        self.assertIsNotNone(new_user)
        # logged in
        self.assertEqual(resp.wsgi_request.user, new_user)
