from classifiers.Classifier import Classifier
from classifiers.ClassifierDecorator import classifier


@classifier
class StringEndClassifier(Classifier):

    def __init__(self, model_to_load):
        self.model = __import__(model_to_load)

    def classify(self, text, model_parameters):
        classified_label = []
        for label in model_parameters['labels']:
            for string in label['strings_to_match']:
                if self.model.search(r"" + self.model.escape(string.lower()) + "$",
                                     string=text.lower()):
                    classified_label.append(
                        label['classification_value'])

        if len(classified_label) != 1:
            # TODO: Poss raise warning here?
            return None

        return classified_label[0], 1

    def classify_batch(self, texts, model_parameters):
        classifications = []

        for text in texts:
            classified_label = []
            for label in model_parameters['labels']:
                for string in label['strings_to_match']:
                    if self.model.search(r"" + self.model.escape(string.lower()) + "$",
                            string=text.lower()):
                        classified_label.append(label['classification_value'])

            if len(classified_label) != 1:
                # TODO: Poss raise warning here?
                classifications.append(None)
            else:
                classifications.append((classified_label[0], 1))

        return classifications

    @staticmethod
    def get_classifier_name():
        return "StringEndClassifier"
