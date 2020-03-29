from django.apps import apps

from classifiers.Classifier import Classifier
from classifiers.ClassifierDecorator import classifier


@classifier
class CombinationClassifier(Classifier):

    def __init__(self, model_to_load):
        pass

    def get_classification(self, classifications_to_combine):
        if len(classifications_to_combine) != 2:
            return None
        combined_classification = 0
        for classification in classifications_to_combine:
            combined_classification = combined_classification ^ int(
                classification)
        return combined_classification, 1

    def classify(self, id, model_parameters):
        classification_types = []
        for classification in model_parameters['classifications_to_combine']:
            classification_types.append(classification['classification_type'])

        classifications_to_combine = \
            apps.get_model('classifiers', 'ClassifiedTweet').objects.filter(
                tweet_id=id,
                classification_type_id__in=classification_types).values_list(
                'classification_value', flat=True)

        return self.get_classification(list(classifications_to_combine))

    def classify_batch(self, tweet_ids, model_parameters):
        classifications = []

        classification_types = []
        for classification in model_parameters['classifications_to_combine']:
            classification_types.append(classification['classification_type'])

        classifications_to_combine = \
            apps.get_model('classifiers', 'ClassifiedTweet').objects.filter(
                tweet_id_id__in=tweet_ids,
                classification_type_id__in=classification_types).values(
                'classification_value', 'tweet_id_id')

        classifications_to_combine_reduced = {}
        for classification in classifications_to_combine:
            key = classification['tweet_id_id']
            if key in classifications_to_combine_reduced:
                classifications_to_combine_reduced[key].append(
                    int(classification['classification_value']))
            else:
                classifications_to_combine_reduced[key] = [
                    int(classification['classification_value'])]

        for tweet_id in tweet_ids:
            if tweet_id not in classifications_to_combine_reduced:
                classifications.append(None)
            else:
                classifications_to_combine = \
                classifications_to_combine_reduced[tweet_id]
                classifications.append(
                    self.get_classification(classifications_to_combine))

        return classifications

    @staticmethod
    def get_classifier_name():
        return "CombinationClassifier"
