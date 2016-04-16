from django.contrib.auth import get_user_model
from django.test import TestCase

from buildservice.errors import MissingToken
from buildservice.models import Repository
from buildservice.utils.testing import create_user_token


class RepositoryTestCase(TestCase):

    def setUp(self):
        self.repo = Repository.objects.create(name='john-doe/repo')

    def test_get_token_missing(self):
        self.assertRaises(MissingToken, self.repo.get_token)

    def test_get_token_ok(self):
        token = create_user_token(self.repo)
        self.assertEqual(self.repo.get_token(), token)

    def test_get_token_multiple(self):
        user = get_user_model().objects.create_user('aaa', password='ttt')
        token = create_user_token(self.repo, user)
        token2 = create_user_token(self.repo)
        self.assertIn(self.repo.get_token(), [token, token2])
