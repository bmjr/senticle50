from django.core.paginator import Paginator
from django.db import models
from django.db import transaction

from scraper.models import Tweet
from utils import StringUtils


class TweetManager(models.Manager):

    @staticmethod
    def get_all_tweets_text():
        return Tweet.objects.all().values_list('text', flat=True)

    @staticmethod
    def get_all_pre_negotiation_tweet_id_text_tuples():
        return Tweet.objects.all().values_list('id', 'text').filter(
            date__lte='2017-06-18')[:100000]

    @staticmethod
    def get_all_pre_negotiation_tweets():
        return Tweet.objects.all().values_list('text', flat=True).filter(
            date__lte='2017-06-18')

    @staticmethod
    @transaction.atomic
    def save_tweets(tweets):
        # Save all given tweets
        print(tweets[0].date)
        for tweet in tweets:
            tweet.save()

    @staticmethod
    def get_hashtag_count(tweets, count):
        return StringUtils.get_delimited_strings_count(tweets, count, '#')

    @staticmethod
    def get_page(query_set, page_size, page_number):
        paginator = Paginator(query_set, page_size)

        return paginator.page(page_number).object_list
