import datetime

from django.test import TestCase

from classifiers.ClassifiedDayTransformer import ClassifiedDayTransformer
from classifiers.models import ClassificationType
from classifiers.models import ClassifiedDay


class TestClassifiedDayTransformerMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        self.model_name = 'test_model'
        self.classification_type = ClassificationType(19, 'Example_Type')
        self.model = 're'
        self.classification_value = 5
        self.amount_classified = 100

        self.date = datetime.date(2018, 2, 12)
        '2012/12/12'

        self.classification_type.save()

    def test_get_classified_day__transforms_day(self):
        expected_output = ClassifiedDay(date=self.date,
                                        classification_type=self.classification_type,
                                        classification_value=self.classification_value,
                                        amount_classified=self.amount_classified)

        actual_output = ClassifiedDayTransformer.get_classified_day(
            self.date,
            self.classification_type.id,
            self.classification_value,
            self.amount_classified)

        self.assertEqual(expected_output.date, actual_output.date)
        self.assertEqual(expected_output.classification_type,
                         actual_output.classification_type)
        self.assertEqual(expected_output.classification_value,
                         actual_output.classification_value)
        self.assertEqual(expected_output.amount_classified,
                         actual_output.amount_classified)

    def test_get_classified_day__updates_existing_classified_tweet_when_new_classified_amount_detected(
            self):
        existing_classified_day = ClassifiedDay(date=self.date,
                                                classification_type=self.classification_type,
                                                classification_value=self.classification_value,
                                                amount_classified=self.amount_classified)
        existing_classified_day.save()

        new_classified_amount = self.amount_classified + 1

        expected_output = ClassifiedDay(date=self.date,
                                        classification_type=self.classification_type,
                                        classification_value=self.classification_value,
                                        amount_classified=new_classified_amount)

        actual_output = ClassifiedDayTransformer.get_classified_day(
            self.date,
            self.classification_type.id,
            self.classification_value,
            new_classified_amount)

        self.assertEqual(expected_output.date, actual_output.date)
        self.assertEqual(expected_output.classification_type,
                         actual_output.classification_type)
        self.assertEqual(expected_output.classification_value,
                         actual_output.classification_value)
        self.assertEqual(expected_output.amount_classified,
                         actual_output.amount_classified)

    def test_get_classified_day__returns_none_when_classified_day_alreayd_exists(
            self):
        existing_classified_tweet = ClassifiedDay(date=self.date,
                                                  classification_type=self.classification_type,
                                                  classification_value=self.classification_value,
                                                  amount_classified=self.amount_classified)
        existing_classified_tweet.save()

        expected_output = None

        actual_output = ClassifiedDayTransformer.get_classified_day(
            self.date,
            self.classification_type.id,
            self.classification_value,
            self.amount_classified)

        self.assertEqual(expected_output, actual_output)
