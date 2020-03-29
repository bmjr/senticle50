from unittest import TestCase
from unittest.mock import patch

from classifiers.ClassifierDecorator import classifier


class MockModel(object):
    def get_classifier_name(self):
        return "MockClassifier"


class TestClassifierDecoratorMethods(TestCase):

    @patch('classifiers.ClassifierDecorator.ClassifierRegistry')
    def test_classifier_decorator_registers_model(self, classifier_registry):
        mock_classifier = MockModel()

        classifier(mock_classifier)

        classifier_registry.return_value.add.assert_called_with(
            mock_classifier.get_classifier_name(),
            mock_classifier)
