from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class EODTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.since = '2000-01-01'
        self.until = '2000-02-01'

    @patch('scraper.management.commands.EOD.EndOfDayService.generate_days')
    def test_handle__calls_day_classifier_service_correctly(self, eod_service):
        out = StringIO()
        args = ['--since=' + self.since,
                '--until=' + self.until]
        call_command('EOD', args[0], args[1], stdout=out)

        eod_service.assert_called_with(self.since, self.until)
