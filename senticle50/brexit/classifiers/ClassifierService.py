from django.db.models import F
from django.db.models.query import Q
from tqdm import tqdm

from classifiers.ClassifiedTweetTransformer import ClassifiedTweetTransformer
from classifiers.ClassifierRegistry import ClassifierRegistry
from classifiers.models import ClassificationType
from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from concurrency.Utils import Utils
from scraper.models import Tweet
from tokenizer.models import TokenizedTweet
from utils.DatabaseManager import DatabaseManager


class ClassifierService:

    @staticmethod
    def process_tweet_classification(classified_tweet_counter, model, tweets,
                                     index, classification_type, config,
                                     progress, worker_loop):
        classification_value = model.classify(tweets[index].text, config)
        if classification_value is not None:
            classified_tweet = ClassifiedTweetTransformer.get_classified_tweet(
                tweets[index].tweet_id, classification_type,
                classification_value, config)
            if classified_tweet is not None:
                classified_tweet_counter.add(classified_tweet)

            classified_tweet_counter.get_lock()
            if classified_tweet_counter.get_size_thread_unsafe() >= 500:
                worker_loop.call_soon_threadsafe(
                    DatabaseManager.update_items,
                    classified_tweet_counter.get_list())
                # Clear list now it has been saved
                classified_tweet_counter.clear()
            classified_tweet_counter.release_lock()

        progress.update(1)

    def classify_tweets(self, since, until, config):
        print("Getting tweets...")
        tweets = None
        if config['tweet_type'] == 'unprocessed':
            tweets = Tweet.objects.filter(Q(date__gte=since) & Q(
                date__lte=until)).annotate(tweet_id=F('id'))
        else:
            tweets = TokenizedTweet.objects.filter(Q(id__date__gte=since) & Q(
                id__date__lte=until)).annotate(tweet_id=F('id__id')) \
                .annotate(text=F('tokens'))

        classification_type = ClassificationType.objects.get(
            id=config[
                'classification_type'])
        print("Got tweets ...")

        worker_loop = Utils.get_worker_loop()
        pool = ThreadPool(3)
        classified_tweet_counter = SynchronizedList()

        model = ClassifierRegistry().get(config['model_name'])
        model = model(config['model'])
        print("parsing tweets")

        size = tweets.count()
        progress = tqdm(total=size)
        for i in range(0, size):
            pool.add_task(self.process_tweet_classification,
                          classified_tweet_counter, model, tweets, i,
                          classification_type, config, progress,
                          worker_loop)

        pool.wait_completion()

        print(classified_tweet_counter.get_list(), flush=True)

        # Save any unsaved tokenized tweets
        DatabaseManager.update_items(
            classified_tweet_counter.get_list())

        # Exit program
        worker_loop.call_soon_threadsafe(worker_loop.stop)
