from django.core.management.base import BaseCommand

from tokenizer.TokenService import TokenService


class Command(BaseCommand):
    """ A management command to Tokenize Tweets between a given date range

    """

    help = 'Tokenize tweets in a given date range'

    def add_arguments(self, parser):
        """ A method to add the required and optional arguments that the
            Tokenize Command expects

        Args:
            :param parser: The parser for standard input
        """
        parser.add_argument(
            '--since', dest='since', required=True,
            help='the date tokenize since',
        )

        parser.add_argument(
            '--until', dest='until', required=True,
            help='the date tokenize until',
        )

        parser.add_argument(
            '--overwrite', action='store_true', dest='overwrite',
            default=False,
            help='Whether to overwrite existing tokenized tweets',
        )

        parser.add_argument(
            '--batch_size', dest='batch_size',
            default=5000, type=int,
            help='Batch size to tokenize tweets in',
        )

    def handle(self, *args, **options):
        """ A method to handle the invocation of the Tokenize command

        This method takes the parsed arguments both optional and required and
        calls the Token Service to tokenize the tweets with the
        given parameters.

        Args:
            :param args: method arguments.
            :param options: the parsed options.
        """
        since = options['since']
        until = options['until']
        overwrite = options['overwrite']
        batch_size = options['batch_size']

        tokenizer = TokenService()

        tokenizer.tokenize_tweets(since, until, overwrite, batch_size)
