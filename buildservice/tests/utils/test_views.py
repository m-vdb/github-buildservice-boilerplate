from django.test import TestCase
from github3.repos.repo import Repository

from buildservice.utils import views


class ViewsUtilsTestCase(TestCase):

    def test_group_repositories(self):
        u1r1 = Repository({'name': 'u1/repo1', 'owner': {'login': 'u1'}})
        u1r2 = Repository({'name': 'u1/repo2', 'owner': {'login': 'u1'}})
        o1r3 = Repository({'name': 'org1/repo3', 'owner': {'login': 'org1'}})
        o1r4 = Repository({'name': 'org1/repo4', 'owner': {'login': 'org1'}})
        o2r5 = Repository({'name': 'org2/repo5', 'owner': {'login': 'org2'}})
        o3r6 = Repository({'name': 'org3/repo6', 'owner': {'login': 'org3'}})
        repos = [u1r1, u1r2, o1r3, o1r4, o2r5, o3r6]
        sections = views.group_repositories(repos)
        self.assertEqual(sections, [
            ('org1', [o1r3, o1r4]),
            ('u1', [u1r1, u1r2]),
            ('Other', [o2r5, o3r6])
        ])
