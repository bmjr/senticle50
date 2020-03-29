from django.test import TestCase

from scraper.managers.TweetManager import TweetManager
from scraper.models import *


class TestTweetManagerMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        Tweet.objects.create(id=1,
                             text="This is an example #tweet",
                             date='2016-10-10')
        Tweet.objects.create(id=2,
                             text="I love to #tweet it makes my #day #great",
                             date='2016-11-11')
        Tweet.objects.create(id=3,
                             text="#tweet #fun #great",
                             date='2016-12-12')

    def test_get_all_tweets_text(self):
        expected_output = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]
        actual_output = TweetManager.get_all_tweets_text()

        self.assertEqual(len(expected_output), len(actual_output))

        for expected_item, actual_item in zip(expected_output, actual_output):
            self.assertEqual(expected_item, actual_item)

    def get_all_pre_negotiation_tweets_id_text_tuples__all_tuples(self):
        expected_output = [
            (1, "This is an example #tweet"),
            (2, "I love to #tweet it makes my #day #great"),
            (3, "#tweet #fun #great")
        ]

        actual_output = \
            TweetManager.get_all_pre_negotiation_tweet_id_text_tuples()

        self.assertEqual(sorted(expected_output), sorted(actual_output))

    def get_all_pre_negotiation_tweets_id_text_tuples__check_date_matcher(
            self):
        expected_output = [
            (1, "This is an example #tweet"),
            (2, "I love to #tweet it makes my #day #great"),
            (3, "#tweet #fun #great")
        ]

        # Save Tweet greater than negotiation date
        Tweet.objects.create(id=4,
                             text="#tweet #fun #great",
                             date='2017-12-12')

        actual_output = \
            TweetManager.get_all_pre_negotiation_tweet_id_text_tuples()

        self.assertEqual(sorted(expected_output), sorted(actual_output))

    def test_get_page_three_pages(self):
        expected_output = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]

        all_tweets = TweetManager.get_all_tweets_text()

        for i in range(0, 3):
            actual_item = TweetManager.get_page(all_tweets, 1, i + 1)
            self.assertEqual(expected_output.__getitem__(i), actual_item[0])

    def test_get_page_one_page(self):
        expected_output = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]

        all_tweets = TweetManager.get_all_tweets_text()
        actual_output = TweetManager.get_page(all_tweets, 3, 1)

        self.assertEqual(len(expected_output), len(actual_output))

        for expected_item, actual_item in zip(expected_output, actual_output):
            self.assertEqual(expected_item, actual_item)

    def test_get_page_page_size_is_smaller_than_requested(self):
        expected_output = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]

        all_tweets = TweetManager.get_all_tweets_text()
        actual_output = TweetManager.get_page(all_tweets, 4, 1)

        self.assertEqual(len(expected_output), len(actual_output))
