#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import threading
from multiprocessing import Lock
from threading import Thread

import codecs
import django
import os
import re
from collections import Counter, OrderedDict
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# This should be the directory that contains the directory containing settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brexit.settings.production")

django.setup()

from scraper.managers.TweetManager import TweetManager

from queue import Queue

lock = threading.Lock()

#CONCURRENCY PATTERN SOURCED ONLINE
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


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


class TweetCounter(object):
    def __init__(self, query_set):
        self.query_set = query_set.iterator()
        self.lock = Lock()
        self.counter = Counter({})

    def add(self, counter):
        with self.lock:
            self.counter += counter

    def get_next_tweet(self):
        with self.lock:
            return next(self.query_set)

    def get_counter(self):
        return self.counter


def get_delimited_strings_count(tweetCounter, t):
    regex = '#' + "\w+"
    found = re.findall(regex, tweetCounter.get_next_tweet().upper())
    tweetCounter.add(Counter(found))
    t.update(1)


def run():
    pool = ThreadPool(3)
    tweetCounter = TweetCounter(
        TweetManager.get_all_pre_negotiation_tweets())
    size = TweetManager.get_all_pre_negotiation_tweets().count()
    t = tqdm(total=size)
    for i in range(0, size):
        pool.add_task(get_delimited_strings_count, tweetCounter, t)

    pool.wait_completion()

    outputFile = codecs.open("hashtag_count.csv", "w+", "utf-8")

    outputFile.write('hashtag;count')

    hashtags = OrderedDict(tweetCounter.get_counter().most_common())

    print(hashtags)
    print(hashtags.items())

    for hashtag in hashtags.items():
        outputFile.write(('\n%s;%s' % (hashtag[0], hashtag[1])))
        outputFile.flush()

    outputFile.close()

if __name__ == "__main__":
    run()
