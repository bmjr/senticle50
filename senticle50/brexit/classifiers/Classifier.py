from abc import ABC, abstractmethod


class Classifier(ABC):
    """ An abstract base class representation of Classifier

    Each classifier within the system is derived from this class and has
    to override the below abstract methods.
    """

    @abstractmethod
    def __init__(self, model_to_load):
        """
        An abstract method to enforce classifiers to implement an init
        method with the correct parameters.

        :param model_to_load: The model to load into the
                              classifier for classification.
        """
        pass

    @abstractmethod
    def classify(self, text, model_parameters):
        """
        An abstract method to enforce classifiers to implement a classify
        method which should classify a text against a classifiers model
        (received on instantiation) and or model_parameters.

        :param tweet: The tweet text.
        :param model_parameters: Configurable model parameters
                                 to classify against.
        """
        pass

    @abstractmethod
    def classify_batch(self, texts, model_parameters):
        """
        An abstract method to enforce classifiers to implement a classify batch
        method which should classify texts against a classifiers model
        (received on instantiation) and or model_parameters.

        :param tweet: The tweet text.
        :param model_parameters: Configurable model parameters
                                 to classify against.
        """
        pass

    @abstractmethod
    def get_classifier_name(self):
        """
        An abstract method to enforce classifiers to implement a
        get_classifier_name which should return a unique identifiable string
        for each classifier.
        """
        pass
