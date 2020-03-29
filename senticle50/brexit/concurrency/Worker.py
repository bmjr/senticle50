from threading import Thread

__author__ = "Emilio Monti"
__copyright__ = "Copyright 2010"
__license__ = "MIT"
__url__ = "http://code.activestate.com/recipes/577187-python-thread-pool/"
__repository__ = "https://github.com/ActiveState/code/recipes/Python/577187_Python_Thread_Pool"


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            self.tasks.task_done()
