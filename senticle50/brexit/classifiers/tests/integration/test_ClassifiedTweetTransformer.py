from django.test import TestCase

from classifiers.ClassifiedTweetTransformer import ClassifiedTweetTransformer
from classifiers.models import ClassificationType
from classifiers.models import ClassifiedTweet
from scraper.models import Tweet


class TestClassifiedTweetTransformerMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        self.model_name = 'test_model'
        self.classification_type = ClassificationType(19, 'Example_Type')
        self.model = 're'

        self.classification_value = 5
        self.classification_probability = 1
        self.classification = (
        self.classification_value, self.classification_probability)
        self.is_training = True

        self.config = {
            'model_name': self.model_name,
            'model': self.model,
            'classification_type': self.classification_type,
            'is_training': self.is_training
        }

        self.tweet = Tweet(id=10, text='Some example text')

        self.classification_type.save()
        self.overwrite_mode = False
        self.tweet.save()

    def test_ClassifiedTweetTransformer_transforms_tweet(self):
        expected_output = ClassifiedTweet(tweet_id=self.tweet,
                                          classification_type=self.classification_type,
                                          classification_value=self.classification_value,
                                          classification_probability=self.classification_probability,
                                          is_training_set=self.is_training)

        actual_output = ClassifiedTweetTransformer.get_classified_tweet(
            self.tweet.id,
            self.classification_type,
            self.classification,
            self.is_training,
            self.overwrite_mode
        )

        self.assertEqual(expected_output.tweet_id, actual_output.tweet_id)
        self.assertEqual(expected_output.classification_type,
                         actual_output.classification_type)
        self.assertEqual(expected_output.classification_value,
                         actual_output.classification_value)
        self.assertEqual(expected_output.classification_probability,
                         actual_output.classification_probability)
        self.assertEqual(expected_output.is_training_set,
                         actual_output.is_training_set)

    def test_ClassifiedTweetTransformer_updates_existing_classified_tweet_when_new_classification_detected(
            self):
        existing_classified_tweet = ClassifiedTweet(tweet_id=self.tweet,
                                                    classification_type=self.classification_type,
                                                    classification_value=self.classification_value,
                                                    classification_probability=self.classification_probability,
                                                    is_training_set=self.is_training)
        existing_classified_tweet.save()

        new_classification_value = self.classification_value - 1

        expected_output = ClassifiedTweet(tweet_id=self.tweet,
                                          classification_type=self.classification_type,
                                          classification_value=new_classification_value,
                                          classification_probability=self.classification_probability,
                                          is_training_set=self.is_training)

        actual_output = ClassifiedTweetTransformer.get_classified_tweet(
            self.tweet.id,
            self.classification_type,
            (new_classification_value, self.classification_probability),
            self.is_training,
            self.overwrite_mode
        )

        self.assertEqual(expected_output.tweet_id, actual_output.tweet_id)
        self.assertEqual(expected_output.classification_type,
                         actual_output.classification_type)
        self.assertEqual(expected_output.classification_value,
                         actual_output.classification_value)
        self.assertEqual(expected_output.classification_probability,
                         actual_output.classification_probability)
        self.assertEqual(expected_output.is_training_set,
                         actual_output.is_training_set)

    def test_ClassifiedTweetTransformer_returns_none_when_classified_tweet_exists_when_overwriting(
            self):
        existing_classified_tweet = ClassifiedTweet(tweet_id=self.tweet,
                                                    classification_type=self.classification_type,
                                                    classification_value=self.classification_value,
                                                    classification_probability=self.classification_probability,
                                                    is_training_set=self.is_training)
        existing_classified_tweet.save()

        expected_output = None

        actual_output = ClassifiedTweetTransformer.get_classified_tweet(
            self.tweet.id,
            self.classification_type,
            self.classification,
            self.is_training,
            True
        )

        self.assertEqual(expected_output, actual_output)
