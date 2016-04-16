from django.test import TestCase
from mock import patch

from buildservice import tasks
from buildservice.models import Build, Repository


class TasksTestCase(TestCase):

    def test_run_build_unknown_build(self):
        self.assertRaises(Build.DoesNotExist, tasks.run_build, -42)

    @patch.object(Build, 'update_status')
    def test_run_build_ok(self, update_status):  # pylint: disable=no-self-use
        repo = Repository.objects.create(name='john-doe/repo')
        build = Build.objects.create(
            repository=repo,
            pusher_name='john-doe',
            branch='other',
            sha='1234567890abcdef',
            number=125
        )
        tasks.run_build(build.pk)
        update_status.assert_called_with('success')
