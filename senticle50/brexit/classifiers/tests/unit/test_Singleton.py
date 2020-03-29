from unittest import TestCase

from classifiers.Singleton import Singleton


class MockSingleton(Singleton):

    def _init(self):
        pass


class TestSingleton(TestCase):

    def test_singleton(self):
        singleton = MockSingleton()
        new_singleton = MockSingleton()

        self.assertEqual(singleton, new_singleton)
