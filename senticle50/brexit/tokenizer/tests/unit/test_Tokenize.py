from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class TokenizeTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.since = '2000-01-01'
        self.until = '2000-02-01'
        self.batch_size = '10'
        self.args = ['--since=' + self.since,
                '--until=' + self.until,
                '--overwrite',
                '--batch_size=' + self.batch_size]
        self.out = StringIO()


    @patch('tokenizer.management.commands.Tokenize.TokenService.tokenize_tweets')
    def test_handle__calls_day_classifier_service_correctly(self,
                                                            token_service):

        call_command('Tokenize', self.args[0], self.args[1], self.args[2], self.args[3],
                     stdout=self.out)

        token_service.assert_called_with(self.since, self.until, True,
                                         int(self.batch_size))

    @patch('tokenizer.management.commands.Tokenize.TokenService.tokenize_tweets')
    def test_handle__calls_day_classifier_service_with_default_optional_arguments(self,
                                                            token_service):

        call_command('Tokenize', self.args[0], self.args[1], stdout=self.out)

        token_service.assert_called_with(self.since, self.until, False,
                                         5000)
