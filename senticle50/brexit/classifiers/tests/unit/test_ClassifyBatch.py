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
        self.config_name = 'example-config'
        self.config = {'config': self.config_name}
        self.batch_size = '10000'
        self.overwrite_mode = True
        self.args = ['--since=' + self.since,
                     '--until=' + self.until,
                     '--config=' + self.config_name,
                     '--overwrite',
                     '--batch_size=' + self.batch_size]

    @patch(
        'classifiers.management.commands.ClassifyBatch.BatchClassifierService')
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps({'config': 'example-config'}))
    def test_classifybatch_instantiates_batch_classifier_service_correctly(
            self,
            mock_file,
            batch_classifier_service):
        out = StringIO()

        # mock_file.read_data = self.mock_config
        call_command('ClassifyBatch', self.args[0], self.args[1], self.args[2],
                     self.args[3], self.args[4], stdout=out)

        mock_file.assert_called_with(
            './classifiers/config/' + self.config_name)

        assert batch_classifier_service.call_count == 1
        batch_classifier_service.assert_called_with(int(self.batch_size))

    @patch(
        'classifiers.management.commands.ClassifyBatch.BatchClassifierService.classify_tweets')
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps({'config': 'example-config'}))
    def test_classifybatch_calls_batch_classifier_service_with_optional_arguments(
            self,
            mock_file,
            batch_classifier_service):
        out = StringIO()

        call_command('ClassifyBatch', self.args[0], self.args[1], self.args[2],
                     self.args[3], stdout=out)

        mock_file.assert_called_with(
            './classifiers/config/' + self.config_name)
        batch_classifier_service.assert_called_with(self.since, self.until,
                                                    self.config, self.overwrite_mode)

    @patch(
        'classifiers.management.commands.ClassifyBatch.BatchClassifierService.classify_tweets')
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps({'config': 'example-config'}))
    def test_classifybatch_calls_batch_classifier_service_with_default_optional_arguments(
            self,
            mock_file,
            batch_classifier_service):
        out = StringIO()

        call_command('ClassifyBatch', self.args[0], self.args[1], self.args[2],
                     stdout=out)

        mock_file.assert_called_with(
            './classifiers/config/' + self.config_name)
        batch_classifier_service.assert_called_with(self.since, self.until,
                                                    self.config, False)
