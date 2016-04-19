from django.test import TestCase, override_settings
from mock import patch
from github3.repos.repo import Repository
from github3.repos.hook import Hook

from buildservice.errors import CannotCreateHook
from buildservice.utils import github


@override_settings(
    GITHUB_HOOK_SECRET='ssseeeeccccrrrreeeettt',
    GITHUB_USER_ID='user_id',
    GITHUB_USER_PASSWORD='user_password'
)
class GithubUtilsTestCase(TestCase):

    @override_settings(DEBUG=True, GITHUB_USER_ID='user', GITHUB_USER_PASSWORD='ppp')
    @patch('github3.login')
    def test_github_login_debug_user_id(self, gh_login):
        github._github_login('token')
        gh_login.assert_called_with('user', password='ppp')

    @override_settings(DEBUG=True, GITHUB_USER_ID='')
    @patch('github3.login')
    def test_github_login_debug_no_user_id(self, gh_login):
        github._github_login('token')
        gh_login.assert_called_with(token='token')

    @override_settings(DEBUG=False)
    @patch('github3.login')
    def test_github_login_normal(self, gh_login):
        github._github_login('token')
        gh_login.assert_called_with(token='token')

    @patch('github3.github.GitHub.iter_repos', return_value=[1, 2, 3])
    def test_get_user_repos(self, iter_repos):
        self.assertEqual(github.get_user_repos('token'), [1, 2, 3])
        iter_repos.assert_called_with()

    @patch('github3.github.GitHub.repository')
    def test_create_webhook_hook_error(self, get_repo):
        repo = Repository({})
        get_repo.return_value = repo
        with patch.object(repo, 'create_hook', return_value=None) as create_hook:
            self.assertRaises(
                CannotCreateHook,
                github.create_webhook, 'token',
                'm-vdb/awesome-name', 'https://hook.com'
            )
            get_repo.assert_called_with('m-vdb', 'awesome-name')
            create_hook.assert_called_with(
                'web',
                {
                    "url": 'https://hook.com', "content_type": "json",
                    "secret": 'ssseeeeccccrrrreeeettt',
                    "insecure_ssl": "0"
                },
                events=['push'],
                active=True
            )

    @patch('github3.github.GitHub.repository')
    def test_create_webhook_ok(self, get_repo):
        repo = Repository({})
        get_repo.return_value = repo
        with patch.object(repo, 'create_hook', return_value=Hook({'id': 1257})) as create_hook:
            hook_id = github.create_webhook(
                'token', 'm-vdb/awesome-name', 'https://hook.com'
            )
            get_repo.assert_called_with('m-vdb', 'awesome-name')
            create_hook.assert_called_with(
                'web',
                {
                    "url": 'https://hook.com', "content_type": "json",
                    "secret": 'ssseeeeccccrrrreeeettt',
                    "insecure_ssl": "0"
                },
                events=['push'],
                active=True
            )
            self.assertEqual(hook_id, 1257)

    @patch.object(Hook, 'delete')
    @patch('github3.github.GitHub.repository')
    def test_delete_webhook_unknown(self, get_repo, delete):
        repo = Repository({})
        get_repo.return_value = repo
        with patch.object(repo, 'hook', return_value=None) as get_hook:
            github.delete_webhook('token', 'm-vdb/awesome-name', 53127)
            get_repo.assert_called_with('m-vdb', 'awesome-name')
            get_hook.assert_called_with(53127)
            self.assertFalse(delete.called)

    @patch.object(Hook, 'delete')
    @patch('github3.github.GitHub.repository')
    def test_delete_webhook_ok(self, get_repo, delete):
        repo = Repository({})
        get_repo.return_value = repo
        with patch.object(repo, 'hook', return_value=Hook({'id': 53127})) as get_hook:
            github.delete_webhook('token', 'm-vdb/awesome-name', 53127)
            get_repo.assert_called_with('m-vdb', 'awesome-name')
            get_hook.assert_called_with(53127)
            delete.assert_called_with()

    @patch('github3.github.GitHub.repository')
    def test_create_status(self, get_repo):
        repo = Repository({})
        get_repo.return_value = repo
        with patch.object(repo, 'create_status') as create_status:
            github.create_status(
                'token', 'm-vdb/awesome-name', '128619826916abcdefed',
                'success', key1='value1', key2='value2'
            )
            get_repo.assert_called_with('m-vdb', 'awesome-name')
            create_status.assert_called_with(
                '128619826916abcdefed', 'success',
                context='ci/buildservice',
                key1='value1', key2='value2'
            )
