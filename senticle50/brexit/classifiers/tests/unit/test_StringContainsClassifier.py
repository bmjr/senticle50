from unittest import TestCase

from classifiers.StringContainsClassifier import StringContainsClassifier


class TestStringContainsClassifierMethods(TestCase):

    @classmethod
    def setUpClass(self):
        self.multiple_label_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': ['A', 'B', 'C']
                        }, {'classification_value': 1,
                            'strings_to_match': ['D', 'E', 'F']
                            }]
        }

        self.single_label_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': ['A', 'B', 'C']
                        }]
        }

    def test_string_contains_classifier_classifies_correctly_with_one_label(
            self):
        expected_classification = (0, 1)
        text = "This String has an A in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, self.single_label_model_parameters)
        self.assertEqual(expected_classification,
                         actual_classification_value)

    def test_string_contains_classifier_classifies_correctly_with_more_than_one_label(
            self):
        expected_classification_value = (1, 1)
        text = "String with F in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, self.multiple_label_model_parameters)
        self.assertEqual(expected_classification_value,
                         actual_classification_value)

    def test_string_contains_classifier_classifies_correctly_with_one_string_to_match(
            self):
        expected_classification_value = (0, 1)

        one_string_to_match_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': ['C']
                        }]
        }
        text = "This String has a C in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, one_string_to_match_model_parameters)
        self.assertEqual(expected_classification_value,
                         actual_classification_value)

    def test_string_contains_classifier_classifies_correctly_with_multiple_strings_to_match(
            self):
        expected_classification_value = (0, 1)

        multiple_strings_to_match_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': ['A', 'B', 'C']
                        }]
        }
        text = "String with C in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, multiple_strings_to_match_model_parameters)
        self.assertEqual(expected_classification_value,
                         actual_classification_value)

    def test_string_contains_classifier_classifies_correctly_with_punctuation_strings_to_match(
            self):
        expected_classification_value = (0, 1)

        multiple_strings_to_match_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': [':)', ':(', ':D']
                        }]
        }
        text = "String with :) in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, multiple_strings_to_match_model_parameters)
        self.assertEqual(expected_classification_value,
                         actual_classification_value)

    def test_string_contains_classifier_classifies_none_correctly_with_punctuation_strings_to_match(
            self):
        expected_classification_value = None

        multiple_strings_to_match_model_parameters = {
            'labels': [{'classification_value': 0,
                        'strings_to_match': [':)', ':(', ':D']
                        }]
        }
        text = "String with :\) in it"
        actual_classification_value = \
            StringContainsClassifier('re') \
                .classify(text, multiple_strings_to_match_model_parameters)
        self.assertEqual(expected_classification_value,
                         actual_classification_value)

