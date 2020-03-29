from classifiers.ClassifierRegistry import ClassifierRegistry


def classifier(cls):
    """ Decorator method used to add a decorated `Classifier` class
        to the ClassifierRegistry.

        The decorator method takes the classifier name and populates the classifier
        registry with the key of the classifier name and the class as it's
        corresponding value.

    :param cls: The class for which to add to the classifier registry.
    :return cls: The class for which to add to the classifier registry.
    """
    classifier_registry = ClassifierRegistry()
    classifier_registry.add(cls.get_classifier_name(), cls)
    return cls
