from django.core.management.base import BaseCommand

from scraper.realtime.TweetStreamer import get_tweets


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_tweets()
