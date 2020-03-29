from multiprocessing import Lock
from collections import Counter


class TweetCounter(object):
    def __init__(self, query_set):
        self.query_set = query_set
        self.lock = Lock()
        self.counter = Counter({})

    def add(self, counter):
        with self.lock:
            self.counter += counter

    def get_next_tweet(self):
        with self.lock:
            return next(self.query_set)