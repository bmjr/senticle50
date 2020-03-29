from django.test import TestCase

from scraper.DayTransformer import DayTransformer
from scraper.models import Day
from datetime import datetime


class TestDayTransformerMethods(TestCase):

    @classmethod
    def setUpTestData(self):
        self.model_name = 'test_model'
        self.date = '2017-01-01'

        self.existing_day = Day(date=self.date, tweet_number=1)
        self.existing_day.save()

    def test_get_new_day_returns_new_day(self):
        expected_output = Day(date='2017-01-02', tweet_number=10)

        actual_output = DayTransformer.get_new_day('2017-01-02', 2)

        self.assertIsNotNone(actual_output)
        self.assertEqual(actual_output, expected_output)

    def test_get_new_day_returns_updated_day(self):
        expected_output = Day(date=self.date, tweet_number=2)

        actual_output = DayTransformer.get_new_day(self.date, 2)

        self.assertIsNotNone(actual_output)
        self.assertEqual(actual_output, expected_output)

    def test_get_new_day_returns_none_for_identical_existing_day(self):
        actual_output = DayTransformer.get_new_day(self.date, 1)

        self.assertIsNone(actual_output)

    def test_get_day_returns_existing_day(self):
        expected_output = self.existing_day

        actual_output = DayTransformer.get_day(self.date)

        self.assertEqual(expected_output.date, actual_output.date.strftime('%Y-%m-%d'))
        self.assertEqual(expected_output.tweet_number, actual_output.tweet_number)


    def test_get_day_returns_new_day(self):
        non_existent_day = '2000-01-01'
        expected_output = Day(date=non_existent_day, tweet_number=0)

        actual_output = DayTransformer.get_day(non_existent_day)

        self.assertEqual(expected_output.date, actual_output.date)
        self.assertEqual(expected_output.tweet_number, actual_output.tweet_number)