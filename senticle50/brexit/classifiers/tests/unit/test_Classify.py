import json
from io import StringIO
from unittest.mock import patch, mock_open

from django.core.management import call_command
from django.test import TestCase


class ClassifyTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.since = '2000-01-01'
        self.until = '2000-02-01'
        self.config_name = "example-config"
        self.config = {'config': self.config_name}

    @patch('classifiers.management.commands.Classify.ClassifierService.classify_tweets')
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps({'config': 'example-config'}))
    def test_classify_calls_classifier_service_correctly(self, mock_file,
                                                         classifier_service):
        out = StringIO()
        args = ['--since=' + self.since,
                '--until=' + self.until,
                '--config=' + self.config_name]
        # mock_file.read_data = self.mock_config
        call_command('Classify', args[0], args[1], args[2], stdout=out)

        mock_file.assert_called_with(
            './classifiers/config/' + self.config_name)
        classifier_service.assert_called_with(self.since, self.until,
                                              self.config)
