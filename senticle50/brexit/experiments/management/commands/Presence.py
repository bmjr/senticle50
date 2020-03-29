from django.core.management.base import BaseCommand

from experiments.PresenceOfWordsService import PresenceOfWordsService


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'

    def handle(self, *args, **options):
        service = PresenceOfWordsService(25000)
        service.get_similar_tweets()
