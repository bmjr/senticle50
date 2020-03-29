from queue import Queue

from concurrency.Worker import Worker

__author__ = "Emilio Monti"
__copyright__ = "Copyright 2010"
__license__ = "MIT"
__url__ = "http://code.activestate.com/recipes/577187-python-thread-pool/"
__repository__ = "https://github.com/ActiveState/code/recipes/Python/577187_Python_Thread_Pool"


class ThreadPool:
    """Pool of threads consuming tasks from a queue

       Attributes:
           tasks: The tasks for which the pool must consume.
    """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
