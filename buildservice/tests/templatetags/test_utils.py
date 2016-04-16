from django.test import TestCase

from buildservice.models import Build
from buildservice.templatetags import utils


class UtilsTemplateTagsTestCase(TestCase):

    def setUp(self):
        self.build = Build()

    def test_build_icon_success(self):
        self.build.status = 'success'
        self.assertEqual(utils.build_icon(self.build), 'done')

    def test_build_icon_pending(self):
        self.assertEqual(utils.build_icon(self.build), 'alarm')

    def test_build_icon_errored(self):
        self.build.status = 'errored'
        self.assertEqual(utils.build_icon(self.build), 'clear')

    def test_build_icon_failure(self):
        self.build.status = 'failure'
        self.assertEqual(utils.build_icon(self.build), 'clear')

    def test_build_icon_color_success(self):
        self.build.status = 'success'
        self.assertEqual(utils.build_icon_color(self.build), 'success')

    def test_build_icon_color_pending(self):
        self.assertEqual(utils.build_icon_color(self.build), 'warning')

    def test_build_icon_color_errored(self):
        self.build.status = 'errored'
        self.assertEqual(utils.build_icon_color(self.build), 'danger')

    def test_build_icon_color_failure(self):
        self.build.status = 'failure'
        self.assertEqual(utils.build_icon_color(self.build), 'danger')
