class Singleton(object):
    """ A class implementation of a Singleton object.

    Any object which inherits from Singleton will only ever have one
    instantiation exist at runtime.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Method which handles the instantiation of a Singleton object where
        one does not already exist or the returning of the object that already
        exists.

        Returns:
            :return cls_instance: The instance of the Singleton class.
        """
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance._init()
        return cls._instance

    def __call__(self, *args, **kw):
        """
        Method which handles the calling of a Singleton class to always return
        the Singleton class.

        Returns:
        :return instance: The existing instance fo the Singleton class.
        """
        return self._instance
