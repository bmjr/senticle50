from classifiers.Singleton import Singleton


class ClassifierRegistry(Singleton):
    """ A registry layer class used to register classifier class
        implementations which are available in the system.

        The classifier registry upon launch of the system is called to register
        all the available classifiers within the system so they are available
        to retrieve from just a configurable string.

        In it's essence this class is a static system wide (as inherited from
        a Singleton Implementation) dictionary from which classifiers .cls
        implementations are stored against their corresponding
        classifier string names.

        Attributes:
            classifiers = a Dictionary of available classifiers for which the
                          registry manipulates.
    """

    def _init(self):
        self.classifiers = {}

    def get_registered_classifiers(self):
        """
        Returns the registered classifier dictionary.
        :return classifiers: the registered classifier dictionary.
        """

        return self.classifiers

    def add(self, classifier_name, classifier):
        """
        Adds a given classifier to the classifier registry dictionary.

        Arguments:
        :param classifier_name: The key value to store the classifier against.
        :param model: The classifier class implementation to store as value.
        """

        if classifier_name not in self.classifiers:
            self.classifiers[classifier_name] = classifier

    def get(self, classifier_name):
        """
        Fetches a classifier class given a classifier name.
        :param classifier_name: The classifier name for which to query the
                                classifier registry dictionary for.
        :return:
               Class: The classifier class that was queried for.

               ValueError: An error to signify the classifier that was
                           requested to be fetched does not exist.
        """
        if classifier_name in self.classifiers:
            return self.classifiers[classifier_name]

        raise ValueError('Classifier not found in classifier registry')
