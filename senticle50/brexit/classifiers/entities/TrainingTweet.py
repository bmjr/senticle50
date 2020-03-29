class TrainingTweet(object):
    def __init__(self, id, classification_type, classification_value, tokens):
        self._id = id
        self._classification_type = classification_type
        self._classification_value = classification_value
        self._tokens = tokens

    @property
    def id(self):
        return self._id

    @property
    def classification_type(self):
        return self._classification_type

    @property
    def classification_value(self):
        return self._classification_value

    @property
    def tokens(self):
        return self._tokens

    @id.setter
    def id(self, id):
        self._id = id

    @classification_type.setter
    def classification_type(self, classification_type):
        self._classification_type = classification_type
