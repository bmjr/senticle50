#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db.models.query import Q
from tqdm import tqdm

from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from concurrency.Utils import Utils
from scraper.models import Tweet
from tokenizer.TokenizedTweetTransformer import TokenizedTweetTransformer
from utils.DatabaseManager import DatabaseManager


class TokenService:
    def __init__(self):
        self.repository_utils = DatabaseManager()

    def tokenize_tweets(self, since, until, overwrite_mode, batch_size):
        print("Getting tweets...")
        filter_criteria = Q(date__gte=since) & Q(
            date__lte=until)
        if not overwrite_mode:
            filter_criteria = filter_criteria & Q(tokenizedtweet=None)
        tweets = Tweet.objects.filter(filter_criteria).values_list('id',
                                                                   'text').distinct('id')
        print("Got tweets ...")

        worker_loop = Utils.get_worker_loop()
        pool = ThreadPool(3)
        synchronized_list = SynchronizedList()
        print("parsing tweets")
        batch_number = 1

        next_batch = list(tweets[:batch_size])
        while next_batch:
            print('\nTokenizing batch %d\n' % batch_number)
            no_of_tweets_to_tokenize = min(batch_size, len(next_batch))
            progress = tqdm(total=no_of_tweets_to_tokenize)
            progress.monitor_interval = 0
            for i in range(0, no_of_tweets_to_tokenize):
                pool.add_task(self.process_tweet, synchronized_list,
                              next_batch, i,
                              overwrite_mode, batch_size, progress,
                              worker_loop)

            pool.wait_completion()

            tweets = tweets[batch_size:]
            next_batch = list(tweets[:batch_size])
            batch_number += 1

        # Save any unsaved tokenized tweets
        self.repository_utils.save_items(synchronized_list.get_list(),
                                         'tokenizer',
                                         'TokenizedTweet', overwrite_mode)

        # Exit program
        worker_loop.call_soon_threadsafe(worker_loop.stop)

    def process_tweet(self, synchronized_list, tweets_to_tokenize, index,
                      overwrite_mode, batch_size, progress, worker_loop):

        (tweet_id, tweet_text) = tweets_to_tokenize[index]
        tokenized_tweet = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_id, tweet_text)

        if tokenized_tweet:
            synchronized_list.add(tokenized_tweet)

            synchronized_list.get_lock()
            if synchronized_list.get_size_thread_unsafe() >= batch_size:
                worker_loop.call_soon_threadsafe(
                    self.repository_utils.save_items,
                    synchronized_list.get_list(), 'tokenizer',
                    'TokenizedTweet', overwrite_mode)
                # Clear list now it has been saved
                synchronized_list.clear()
            synchronized_list.release_lock()

        progress.update(1)
