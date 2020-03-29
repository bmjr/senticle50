import json
import os

from django.core.management.base import BaseCommand

from classifiers.ClassifierService import ClassifierService


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        since = options['since']
        until = options['until']
        config = options['config']

        config = json.load(open(os.path.join('./classifiers/config/',
                                             config)))
        classifier_service = ClassifierService()

        classifier_service.classify_tweets(since, until, config)
