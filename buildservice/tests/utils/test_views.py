from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from github3.repos.repo import Repository as GithubRepository

from buildservice.models import Repository, Webhook
from buildservice.utils import views


class ViewsUtilsTestCase(TestCase):

    def test_group_repositories(self):
        u1r1 = GithubRepository({'name': 'u1/repo1', 'owner': {'login': 'u1'}})
        u1r2 = GithubRepository({'name': 'u1/repo2', 'owner': {'login': 'u1'}})
        o1r3 = GithubRepository({'name': 'org1/repo3', 'owner': {'login': 'org1'}})
        o1r4 = GithubRepository({'name': 'org1/repo4', 'owner': {'login': 'org1'}})
        o2r5 = GithubRepository({'name': 'org2/repo5', 'owner': {'login': 'org2'}})
        o3r6 = GithubRepository({'name': 'org3/repo6', 'owner': {'login': 'org3'}})
        repos = [u1r1, u1r2, o1r3, o1r4, o2r5, o3r6]
        sections = views.group_repositories(repos)
        self.assertEqual(sections, [
            ('org1', [o1r3, o1r4]),
            ('u1', [u1r1, u1r2]),
            ('Other', [o2r5, o3r6])
        ])

    def test_get_user_active_repositories_anonymous(self):
        self.assertEqual(views.get_user_active_repositories(AnonymousUser()), [])

    def test_get_user_active_repositories_ok(self):
        user = get_user_model().objects.create_user(username='yop', password='yyy')
        r1 = Repository.objects.create(name='user/r1')
        r2 = Repository.objects.create(name='user/r2')
        r3 = Repository.objects.create(name='user/r3')
        r1.users.add(user)
        r2.users.add(user)
        Webhook.objects.create(repository=r1)
        Webhook.objects.create(repository=r2, active=False)
        self.assertEqual(list(views.get_user_active_repositories(user)), [r1])
