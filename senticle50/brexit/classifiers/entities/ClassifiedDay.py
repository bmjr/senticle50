class ClassifiedDay(object):
    def __init__(self, date, classifications):
        self._date = date

        if classifications is None:
            self._classifications = []
        else:
            self._classifications = classifications

    @property
    def date(self):
        return self._date

    @property
    def classifications(self):
        return self._classifications

    @classifications.setter
    def classifications(self, value):
        self._classifications = value

    @date.setter
    def date(self, value):
        self._date = value
