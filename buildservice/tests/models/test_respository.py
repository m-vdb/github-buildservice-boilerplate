from django.contrib.auth import get_user_model
from django.test import TestCase
from github3.repos.repo import Repository as GithubRepository
from mock import patch

from buildservice.errors import MissingToken
from buildservice.models import Repository
from buildservice.utils.testing import create_user_token


class RepositoryTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('heho', password='ttt')
        self.repo = Repository.objects.create(name='john-doe/repo')
        self.repo.users.add(self.user)

    def test_get_token_missing(self):
        self.assertRaises(MissingToken, self.repo.get_token)

    def test_get_token_ok(self):
        token = create_user_token(self.user, self.repo)
        self.assertEqual(self.repo.get_token(), token)

    def test_get_token_multiple(self):
        user = get_user_model().objects.create_user('aaa', password='ttt')
        token = create_user_token(user)
        token2 = create_user_token(self.user)
        self.repo.users.add(user)
        self.assertIn(self.repo.get_token(), [token, token2])

    def test_str(self):
        self.assertEqual(str(self.repo), self.repo.name)

    @patch(
        'buildservice.utils.github.get_user_repos',
        return_value=[
            GithubRepository({'full_name': 'john-doe/repo'}),
            GithubRepository({'full_name': 'other/repo'}),
            GithubRepository({'full_name': 'unknown/repo'})
        ]
    )
    def test_add_user_to_known_repositories(self, get_user_repos):
        repo2 = Repository.objects.create(name='other/repo')
        user2 = get_user_model().objects.create_user('yoo', password='ttt')
        token = create_user_token(user2)

        Repository.add_user_to_known_repositories(user2)
        get_user_repos.assert_called_with(token.value)
        user_repos = list(user2.repositories.all())
        self.assertItemsEqual(user_repos, [self.repo, repo2])
