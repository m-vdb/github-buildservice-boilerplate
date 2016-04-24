import hashlib
import hmac
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, override_settings

from buildservice.models import Repository
from buildservice.utils import decorators
from buildservice.utils.testing import create_user_token


def view(request):
    return HttpResponse(str(request))


view_token = decorators.oauth_token_required(view)
view_signature = decorators.signature_required(view)
view_anonymous = decorators.anonymous_user_required(view)
view_json = decorators.require_json(view)
view_api_key = decorators.require_api_key(view)


@override_settings(GITHUB_HOOK_SECRET='ssssecret', BUILDSERVICE_API_KEY='Key')
class DecoratorsTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='vvv', password='ttt')

    def test_oauth_token_required_anonymous(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = view_token(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('oauth_login'))

    def test_oauth_token_required_no_token(self):
        req = HttpRequest()
        req.user = self.user
        resp = view_token(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('oauth_login'))

    def test_oauth_token_required_ok(self):
        req = HttpRequest()
        req.user = self.user
        repo = Repository.objects.create(name='some/repo')
        repo.users.add(self.user)
        create_user_token(self.user, repo)
        resp = view_token(req)
        self.assertEqual(resp.status_code, 200)

    def test_signature_required_missing(self):
        req = HttpRequest()
        req._body = 'hello'
        resp = view_signature(req)
        self.assertEqual(resp.status_code, 401)

    def test_signature_required_wrong(self):
        req = HttpRequest()
        req._body = 'hello'
        req.META['HTTP_X_HUB_SIGNATURE'] = 'ihowqepqwhe'
        resp = view_signature(req)
        self.assertEqual(resp.status_code, 401)

    def test_signature_required_ok(self):
        signature = "sha1=%s" % hmac.new('ssssecret', 'hello body', hashlib.sha1).hexdigest()
        req = HttpRequest()
        req._body = 'hello body'
        req.META['HTTP_X_HUB_SIGNATURE'] = signature
        resp = view_signature(req)
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_user_required_authenticated(self):
        req = HttpRequest()
        req.user = self.user
        resp = view_anonymous(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')

    def test_anonymous_user_required_ok(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = view_anonymous(req)
        self.assertEqual(resp.status_code, 200)

    def test_require_json_no_json(self):
        req = HttpRequest()
        req._body = 'yo'
        resp = view_json(req)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content), {'error': 'JSON body required.'})

    def test_require_json_strange_body(self):
        req = HttpRequest()
        req._body = {'youhou'}
        resp = view_json(req)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content), {'error': 'JSON body required.'})

    def test_require_json_empty(self):
        req = HttpRequest()
        req._body = ''
        resp = view_json(req)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(req.json, {})

    def test_require_json_ok(self):
        req = HttpRequest()
        req._body = '{"key": "value"}'
        resp = view_json(req)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(req.json, {"key": "value"})

    def test_require_api_key_missing(self):
        req = HttpRequest()
        resp = view_api_key(req)
        self.assertEqual(resp.status_code, 401)

    def test_require_api_key_wrong(self):
        req = HttpRequest()
        req.GET['api_key'] = 'oula'
        resp = view_api_key(req)
        self.assertEqual(resp.status_code, 401)

    def test_require_api_key_ok(self):
        req = HttpRequest()
        req.GET['api_key'] = 'Key'
        resp = view_api_key(req)
        self.assertEqual(resp.status_code, 200)
