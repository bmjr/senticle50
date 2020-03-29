
class Classification(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @name.setter
    def name(self, name):
        self._name = name

    @value.setter
    def value(self, value):
        self._value = value

