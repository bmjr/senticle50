from django.core.management.base import BaseCommand

from classifiers.DayClassifierService import DayClassifierService


class Command(BaseCommand):
    """ A management command to formulate Classified Day's between
        a given date range.
    """
    help = 'Classifies days within given date range'

    def add_arguments(self, parser):
        """ A method to add the required and optional arguments that the
            ClassifyDay Command expects

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

    def handle(self, *args, **options):
        """ A method to handle the invocation of the ClassifyDay command

        This method takes the parsed arguments both optional and required and
        calls the Day Classifier Service to formulate the classified days with
        the given parameters.

        Args:
            :param args: method arguments.
            :param options: the parsed options.
        """
        since = options['since']
        until = options['until']

        day_classifier_service = DayClassifierService()

        day_classifier_service.classify_days(since, until)
