from django.test import TestCase

from classifiers.ClassifierRegistry import ClassifierRegistry


class TestClassifierRegistryMethods(TestCase):

    def test_model_registry_registers_all_classifiers(self):
        expected_output = ['StringEndClassifier', 'StringContainsClassifier', 'KerasClassifier', 'CombinationClassifier']
        registered_classifiers = \
            ClassifierRegistry().get_registered_classifiers()

        self.assertEqual(len(expected_output),
                         len(registered_classifiers.keys()))

        for i in range(0, len(expected_output)):
            classifier_is_registered = expected_output[
                                           i] in registered_classifiers
            self.assertTrue(classifier_is_registered)
