from datetime import datetime

from django.test import TestCase

from scraper.models import Tweet
from tokenizer.models import TokenizedTweet
from scraper.tasks import recieve_tweet
from unittest.mock import patch


class TestTasksMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        self.tweet_id = '111'
        self.tweet_username = 'example user'
        self.tweet_text = 'example text'
        self.tweet_date = 'Wed Mar 07 16:32:22 +0000 2018'
        self.tweet_retweets = '10'
        self.tweet_favourites = '99'

    @patch('scraper.tasks.redis')
    def test_receive_tweet_saves_tweet(self, redis):
        self.assertIsNone(
            self.get_tweet(self.tweet_id, self.tweet_username, self.tweet_text,
                           self.tweet_date,
                           self.tweet_retweets, self.tweet_favourites))

        expected_result = Tweet(id=int(self.tweet_id),
                                username=self.tweet_username,
                                text=self.tweet_text,
                                date=datetime.strptime(self.tweet_date,
                                                       '%a %b %d %H:%M:%S %z %Y').strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                retweets=int(self.tweet_retweets),
                                favorites=int(self.tweet_favourites))

        recieve_tweet(self.tweet_id, self.tweet_username, self.tweet_text,
             self.tweet_date,
             self.tweet_retweets, self.tweet_favourites)

        actual_result = self.get_tweet(self.tweet_id, self.tweet_username,
                                       self.tweet_text,
                                       self.tweet_date,
                                       self.tweet_retweets,
                                       self.tweet_favourites)

        self.assertIsNotNone(actual_result)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result.username, actual_result.username)
        self.assertEqual(expected_result.text, actual_result.text)
        self.assertEqual(expected_result.retweets, actual_result.retweets)
        self.assertEqual(expected_result.favorites, actual_result.favorites)

    @patch('scraper.tasks.redis')
    def test_receive_tweet_saves_tokenized_tweet(self, redis):
        self.assertIsNone(self.get_tokenized_tweet(self.tweet_id))

        expected_result = TokenizedTweet(id_id=int(self.tweet_id),
                                tokens='exampl text')

        recieve_tweet(self.tweet_id, self.tweet_username, self.tweet_text,
             self.tweet_date,
             self.tweet_retweets, self.tweet_favourites)

        actual_result = self.get_tokenized_tweet(self.tweet_id)

        self.assertIsNotNone(actual_result)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result.tokens, actual_result.tokens)

    def get_tweet(self, tweet_id, tweet_username, tweet_text, tweet_date,
                  tweet_retweets, tweet_favourites):
        try:
            return Tweet.objects.get(id=tweet_id, username=tweet_username,
                                     text=tweet_text,
                                     date=datetime.strptime(tweet_date,
                                                            '%a %b %d %H:%M:%S %z %Y').strftime(
                                         '%Y-%m-%d %H:%M:%S'),
                                     retweets=tweet_retweets,
                                     favorites=tweet_favourites)

        except Tweet.DoesNotExist:
            return None

    def get_tokenized_tweet(self, tweet_id):
        try:
            return TokenizedTweet.objects.get(id_id=tweet_id)

        except TokenizedTweet.DoesNotExist:
            return None

