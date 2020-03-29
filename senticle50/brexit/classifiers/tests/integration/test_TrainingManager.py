from django.test import TestCase

from classifiers.entities.TrainingTweet import TrainingTweet
from classifiers.models import Tweet, ClassificationType, ClassifiedTweet
from tokenizer.models import TokenizedTweet


class TestTrainingManagerMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        self.good_tweet = Tweet.objects.create(id=1,
                                               text="tweet classified as good",
                                               date='2016-11-11')
        self.bad_tweet = Tweet.objects.create(id=2,
                                              text="tweet classified as bad",
                                              date='2016-12-12')
        self.non_training_tweet = Tweet.objects.create(id=3,
                                                       text="random tweet",
                                                       date='2016-08-12')
        self.classification_type = ClassificationType.objects.create(id=1,
                                                                     name='Polarity')

        self.classification_probability = 1

        self.classified_good_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.good_tweet,
            classification_type=self.classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=True
        )
        self.classified_bad_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.bad_tweet,
            classification_type=self.classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=True
        )
        self.classified_non_training_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.non_training_tweet,
            classification_type=self.classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.tokenized_good_tweet = TokenizedTweet.objects.create(
            id=self.good_tweet,
            tokens=self.good_tweet.text)

        self.tokenized_bad_tweet = TokenizedTweet.objects.create(
            id=self.bad_tweet,
            tokens=self.bad_tweet.text)

        self.training_good_tweet = TrainingTweet(self.good_tweet.id,
                                                 self.classified_good_tweet.classification_type,
                                                 self.classified_good_tweet.classification_value,
                                                 self.tokenized_good_tweet.tokens)

        self.training_bad_tweet = TrainingTweet(self.bad_tweet.id,
                                                self.classified_bad_tweet.classification_type,
                                                self.classified_bad_tweet.classification_value,
                                                self.tokenized_bad_tweet.tokens)

    def test_get_all_training_tweets(self):
        expected_output = [
            self.classified_good_tweet, self.classified_bad_tweet
        ]
        actual_output = ClassifiedTweet.training_manager.get_queryset()

        self.assertEqual(len(expected_output), len(actual_output))

        for expected_item, actual_item in zip(expected_output, actual_output):
            self.assertEqual(expected_item, actual_item)

    def test_get_all_tokenized_tweets(self):
        expected_output = [
            self.tokenized_good_tweet, self.tokenized_bad_tweet
        ]

        actual_output = ClassifiedTweet.training_manager.get_token_queryset()

        self.assertEqual(len(expected_output), len(actual_output))

        for expected_item, actual_item in zip(expected_output, actual_output):
            self.assertEqual(expected_item, actual_item)

    def test_get_training_set(self):
        expected_output = [
            self.training_good_tweet, self.training_bad_tweet
        ]
        actual_output = ClassifiedTweet.training_manager.get_training_set(
            self.classification_type)

        self.assertEqual(len(expected_output), len(actual_output))

        for expected_item, actual_item in zip(expected_output, actual_output):
            self.assertEqual(expected_item.id, actual_item.id)
            self.assertEqual(expected_item.classification_type,
                             actual_item.classification_type)
            self.assertEqual(expected_item.classification_value,
                             actual_item.classification_value)
            self.assertEqual([expected_item.tokens],
                             list(actual_item.tokens))
