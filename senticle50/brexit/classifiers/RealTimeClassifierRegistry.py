from classifiers.Singleton import Singleton


class RealTimeClassifierRegistry(Singleton):

    def _init(self):
        self.classifiers = {}

    def get_registered_classifiers(self):
        return self.classifiers

    def get_registered_classifier_keys(self):
        sorted_keys = sorted(self.classifiers,
                             key=lambda key: self.classifiers[key][
                                 'order_of_application'])
        return sorted_keys

    def add(self, classification_name, classifier):
        if classification_name not in self.classifiers:
            self.classifiers[classification_name] = classifier

    def get(self, classification_name):
        if classification_name in self.classifiers:
            return self.classifiers[classification_name]

        raise ValueError('Classifier not found in classifier registry')
