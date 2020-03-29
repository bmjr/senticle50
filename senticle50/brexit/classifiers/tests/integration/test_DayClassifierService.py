from django.test import TestCase

from classifiers.DayClassifierService import DayClassifierService
from classifiers.models import Tweet, ClassificationType, ClassifiedTweet


class TestDayClassifierService(TestCase):
    # @Rollback
    # serialized_rollback = True

    @classmethod
    def setUpTestData(self):
        self.good_tweet = Tweet.objects.create(id=1,
                                               text="tweet classified as good",
                                               date='2016-12-12')
        self.bad_tweet = Tweet.objects.create(id=2,
                                              text="tweet classified as bad",
                                              date='2016-12-12')
        self.another_bad_tweet = Tweet.objects.create(id=3,
                                                      text="random tweet",
                                                      date='2016-12-12')
        self.classification_type = ClassificationType.objects.create(id=1,
                                                                     name='Polarity')

        self.classified_good_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.good_tweet,
            classification_type=self.classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_bad_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.bad_tweet,
            classification_type=self.classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_non_training_tweet = ClassifiedTweet.objects.create(
            tweet_id=self.another_bad_tweet,
            classification_type=self.classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )

    def test_classify_day_aggregates_tweets(self):
        pass
