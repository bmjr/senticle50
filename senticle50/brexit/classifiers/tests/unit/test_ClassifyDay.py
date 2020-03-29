import json
from io import StringIO
from unittest.mock import patch, mock_open

from django.core.management import call_command
from django.test import TestCase


class ClassifyDayTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.since = '2000-01-01'
        self.until = '2000-02-01'

    @patch('classifiers.management.commands.ClassifyDay.DayClassifierService.classify_days')
    def test_handle__calls_day_classifier_service_correctly(self, classifier_service):
        out = StringIO()
        args = ['--since=' + self.since,
                '--until=' + self.until]
        call_command('ClassifyDay', args[0], args[1], stdout=out)

        classifier_service.assert_called_with(self.since, self.until)
