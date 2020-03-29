from django.apps import apps
from django.test import TestCase

from classifiers.CombinationClassifier import CombinationClassifier


class TestCombinationClassifierMethods(TestCase):
    """
        Tests to ensure the XOR logic of Combination classifier works correctly.

        The below tests follow the corresponding table:

        INPUT	|   OUTPUT
        A	B	|   A XOR B
        0	0	|   0
        0	1	|   1
        1	0	|   1
        1	1	|   0
    """

    @classmethod
    def setUpTestData(self):
        self.good_blue_tweet = apps.get_model('scraper',
                                              'Tweet').objects.create(
            id=1,
            text="tweet classified as good and about the colour blue",
            date='2016-12-12')

        self.good_non_blue_tweet = apps.get_model('scraper',
                                                  'Tweet').objects.create(
            id=2,
            text="tweet classified as good and not about the colour blue",
            date='2016-12-12')

        self.bad_blue_tweet = apps.get_model('scraper',
                                             'Tweet').objects.create(
            id=3,
            text="tweet classified as bad and about the colour blue",
            date='2016-12-12')

        self.bad_non_blue_tweet = apps.get_model('scraper',
                                                 'Tweet').objects.create(
            id=4,
            text="tweet classified as bad and not about the colour blue",
            date='2016-12-12')

        self.one_classification_tweet = apps.get_model('scraper',
                                                       'Tweet').objects.create(
            id=5,
            text="tweet by one of the combination classification types",
            date='2016-12-12')

        self.non_classified_tweet = apps.get_model('scraper',
                                                   'Tweet').objects.create(
            id=6,
            text="tweet that is not classified",
            date='2016-12-12')

        self.sentiment_classification_type = apps.get_model('classifiers',
                                                            'ClassificationType').objects.create(
            id=1,
            name='Polarity')

        self.color_classification_type = apps.get_model('classifiers',
                                                        'ClassificationType').objects.create(
            id=2,
            name='Color')

        self.classified_good__one_classification_tweet = apps.get_model(
            'classifiers',
            'ClassifiedTweet').objects.create(
            tweet_id=self.one_classification_tweet,
            classification_type=self.sentiment_classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )

        self.classified_good__blue_tweet = apps.get_model('classifiers',
                                                          'ClassifiedTweet').objects.create(
            tweet_id=self.good_blue_tweet,
            classification_type=self.sentiment_classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_good__non_blue_tweet = apps.get_model('classifiers',
                                                              'ClassifiedTweet').objects.create(
            tweet_id=self.good_non_blue_tweet,
            classification_type=self.sentiment_classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_bad__blue_tweet = apps.get_model('classifiers',
                                                         'ClassifiedTweet').objects.create(
            tweet_id=self.bad_blue_tweet,
            classification_type=self.sentiment_classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_bad__non_blue_tweet = apps.get_model('classifiers',
                                                             'ClassifiedTweet').objects.create(
            tweet_id=self.bad_non_blue_tweet,
            classification_type=self.sentiment_classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_blue__good_blue_tweet = apps.get_model('classifiers',
                                                               'ClassifiedTweet').objects.create(
            tweet_id=self.good_blue_tweet,
            classification_type=self.color_classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_non_blue__good_non_blue_tweet = apps.get_model(
            'classifiers',
            'ClassifiedTweet').objects.create(
            tweet_id=self.good_non_blue_tweet,
            classification_type=self.color_classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_blue__bad_blue_tweet_ = apps.get_model(
            'classifiers',
            'ClassifiedTweet').objects.create(
            tweet_id=self.bad_blue_tweet,
            classification_type=self.color_classification_type,
            classification_value=0,
            classification_probability=1,
            is_training_set=False
        )
        self.classified_non_blue__bad_non_blue_tweet_ = apps.get_model(
            'classifiers',
            'ClassifiedTweet').objects.create(
            tweet_id=self.bad_non_blue_tweet,
            classification_type=self.color_classification_type,
            classification_value=1,
            classification_probability=1,
            is_training_set=False
        )

        self.tweet_ids = [1, 2, 3, 4, 5, 6]

        self.combination_classifier = CombinationClassifier(None)

        self.config = {
            "classifications_to_combine": [
                {
                    "name": "Sentiment",
                    "classification_type": self.sentiment_classification_type.id
                },
                {
                    "name": "Color",
                    "classification_type": self.color_classification_type.id
                }
            ]
        }

    def test_classify_outputs_classification_value_one_for_zero_one_input(
            self):
        expected_classification = (1, 1)
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[0], self.config)
        self.assertEqual(expected_classification, actual_classification)

    def test_classify_outputs_classification_value_zero_for_one_one_input(
            self):
        expected_classification = (0, 1)
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[1], self.config)
        self.assertEqual(expected_classification, actual_classification)

    def test_classify_outputs_classification_value_zero_for_zero_zero_input(
            self):
        expected_classification = (0, 1)
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[2], self.config)
        self.assertEqual(expected_classification, actual_classification)

    def test_classify_outputs_classification_value_one_for_one_zero_input(
            self):
        expected_classification = (1, 1)
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[3], self.config)
        self.assertEqual(expected_classification, actual_classification)

    def test_classify_outputs_none_for_tweet_which_is_partly_classified(
            self):
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[4], self.config)
        self.assertIsNone(actual_classification)

    def test_classify_outputs_none_for_tweet_which_is_not_classified(
            self):
        actual_classification = self.combination_classifier.classify(
            self.tweet_ids[5], self.config)
        self.assertIsNone(actual_classification)

    def test_classify_batch_classifies_each_tweet_correctly(
            self):
        expected_classifications = [(1,1), (0,1), (0,1), (1,1), None, None]
        actual_classifications = self.combination_classifier.classify_batch(
            self.tweet_ids, self.config)
        self.assertEqual(expected_classifications, actual_classifications)
