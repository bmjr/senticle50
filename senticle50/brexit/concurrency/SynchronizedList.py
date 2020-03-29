from multiprocessing import Lock


class SynchronizedList(object):
    """ A wrapper class for a list that ensures thread safe manipulation of the
        contained list.

        Attributes:
            list: The list for which this class is a wrapper around.
            lock: The lock for which to hold when manipulating the list in a
                  thread safe operation.
            size: The size of the list at any given time.
    """
    def __init__(self):
        self.list = []
        self.lock = Lock()
        self.size = 0

    def add(self, item):
        """
        A method to add an item to the list using the blocking lock.

        Args:
            :param item: The item to add to the list
        """
        with self.lock:
            self.list.append(item)
            self.size += 1

    def get_size_thread_safe(self):
        """
        A method to retrieve the size of the list using the blocking lock.

        Returns:
            :return: The size of the list.
        """
        with self.lock:
            return self.size

    def get_size_thread_unsafe(self):
        """
        A method to retrieve the size of the list without using
        the blocking lock.

        Returns:
            :return: The size of the list.
        """
        return self.size

    def get_list(self):
        """
        A method to retrieve the list

        :return: The list.
        """
        return self.list

    def clear(self):
        """
        A method to handle the clearing of the list.
        """
        self.list = []
        self.size = 0

    def get_lock(self):
        """
        A method to acquire the blocking lock of this class.
        """
        self.lock.acquire()

    def release_lock(self):
        """
        A method to release the blocking lock of this class.
        """
        self.lock.release()
