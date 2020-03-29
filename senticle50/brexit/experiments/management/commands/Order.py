import json
import os

from django.core.management.base import BaseCommand

from experiments.OrderOfWordsService import OrderOfWordsService


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'



    def handle(self, *args, **options):
        service = OrderOfWordsService(100)
        service.get_similar_tweets()
