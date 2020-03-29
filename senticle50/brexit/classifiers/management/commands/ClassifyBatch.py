import json
import os

from django.core.management.base import BaseCommand

from classifiers.BatchClassifierService import BatchClassifierService


class Command(BaseCommand):
    """ A method to add the required and optional arguments that the
        ClassifyBatch Command expects

    Args:
        :param parser: The parser for standard input
    """
    help = 'Classifies tweets in batches within a given date range'

    def add_arguments(self, parser):
        """ A method to add the required and optional arguments that the
            ClassifyBatch Command expects

        Args:
            :param parser: The parser for standard input
        """
        parser.add_argument(
            '--since', dest='since', required=True,
            help='the date to classify since',
        )

        parser.add_argument(
            '--until', dest='until', required=True,
            help='the date to classify until',
        )

        parser.add_argument(
            '--config', dest='config', required=True,
            help='the config to use when classifying',
        )

        parser.add_argument(
            '--overwrite', action='store_true', dest='overwrite',
            default=False,
            help='whether to overwrite existing tokenized tweets',
        )

        parser.add_argument(
            '--batch_size', dest='batch_size',
            default=5000, type=int,
            help='the batch size to carry out classifications in',
        )

    def handle(self, *args, **options):
        """ A method to handle the invocation of the ClassifyBatch command

        This method takes the parsed arguments both optional and required and
        calls the Batch Classifier Service to classify the tweets with the
        given parameters.

        Args:
            :param args: method arguments.
            :param options: the parsed options.
        """
        since = options['since']
        until = options['until']
        config = options['config']
        overwrite = options['overwrite']
        batch_size = options['batch_size']

        config = json.load(open(os.path.join('./classifiers/config/',
                                             config)))
        batch_classifier_service = BatchClassifierService(batch_size)

        batch_classifier_service.classify_tweets(since, until, config, overwrite)
