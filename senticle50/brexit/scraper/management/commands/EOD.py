from django.core.management.base import BaseCommand

from scraper.EndOfDayService import EndOfDayService


class Command(BaseCommand):
    """ A management command to formulate `End of Day` tweet numbers between
        a given date range.
    """
    help = 'formulates tweets end of day counts in a given date range'

    def add_arguments(self, parser):
        """ A method to add the required and optional arguments that the
            EOD Command expects

        Args:
            :param parser: The parser for standard input
        """
        parser.add_argument(
            '--since', dest='since', required=True,
            help='the date to formulate end of day tweets numbers since',
        )

        parser.add_argument(
            '--until', dest='until', required=True,
            help='the date to formulate end of day tweets numbers until',
        )

    def handle(self, *args, **options):
        """ A method to handle the invocation of the Tokenize command

        This method takes the parsed arguments both optional and required
        and calls the End Of Day Service to generate the days within the
        given parameters.

        Args:
            :param args: method arguments.
            :param options: the parsed options.
        """
        since = options['since']
        until = options['until']

        end_of_day_service = EndOfDayService()

        end_of_day_service.generate_days(since, until)
