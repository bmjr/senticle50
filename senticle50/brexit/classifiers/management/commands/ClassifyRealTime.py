from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from classifiers.BatchClassifierService import BatchClassifierService
from classifiers.DayClassifierService import DayClassifierService
from classifiers.RealTimeClassifierRegistry import RealTimeClassifierRegistry


class Command(BaseCommand):
    """ A method to add the required and optional arguments that the
        ClassifyRealTime Command expects

    Args:
        :param parser: The parser for standard input
    """
    help = 'Classifies tweets in batches within a given date range'

    def add_arguments(self, parser):
        """ A method to add the optional argument that the
            ClassifyRealTime Command expects

        Args:
            :param parser: The parser for standard input
        """
        parser.add_argument(
            '--batch_size', dest='batch_size',
            default=5000, type=int,
            help='the batch size to carry out classifications in',
        )

    def handle(self, *args, **options):
        """ A method to handle the invocation of the ClassifyRealTime command

        This method takes the parsed argument of batch_size calls the
        Batch Classifier Service to classify the tweets against all registered
        real time classifiers and updates the classified day stats.

        Args:
            :param args: method arguments.
            :param options: the parsed options.
        """
        batch_size = options['batch_size']
        batch_classifier_service = BatchClassifierService(batch_size)
        real_time_classifier_registry = RealTimeClassifierRegistry()

        since = (datetime.now() + relativedelta(days=-1)).strftime('%Y-%m-%d')
        until = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')

        for classifier in real_time_classifier_registry.get_registered_classifier_keys():
            config = real_time_classifier_registry.get(classifier)
            batch_classifier_service.classify_tweets(since, until, config,
                                                     False)

        # Update Classified Day Objects
        DayClassifierService().classify_days(since, until)
