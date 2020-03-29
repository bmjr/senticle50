from django.db.models.query import Q
from tqdm import tqdm

from classifiers.ClassifiedTweetTransformer import ClassifiedTweetTransformer
from classifiers.ClassifierRegistry import ClassifierRegistry
from classifiers.models import ClassificationType
from classifiers.models import ClassifiedTweet
from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from concurrency.Utils import Utils
from scraper.models import Tweet
from tokenizer.models import TokenizedTweet
from utils.DatabaseManager import DatabaseManager


class BatchClassifierService:
    """ A Service Layer Class to handle the Classification of Tweets in a
        grouped manner to maximise efficiency.

        The batch process implemented by this class utilises the lazy evaluation
        of Django Queryset's to handle 'Fast' classification batches.

        Each batch of tweets is classified against a configured classifier and
        the classification result is persisted to the database.

        Attributes:
            repository_utils: A database manager class for handling
                              saving classified tweets.
    """

    def __init__(self, batch_size):
        self.repository_utils = DatabaseManager()
        self.batch_size = batch_size

    def process_tweet_classification(self, classified_tweet_counter,
                                     tweet_id, classification_type,
                                     classification, config,
                                     overwrite_mode, worker_loop,
                                     progress):
        if classification:
            classified_tweet = ClassifiedTweetTransformer.get_classified_tweet(
                tweet_id, classification_type, classification,
                config['is_training'], overwrite_mode)
            if classified_tweet is not None:
                classified_tweet_counter.add(classified_tweet)

            classified_tweet_counter.get_lock()
            if classified_tweet_counter.get_size_thread_unsafe() >= self.batch_size:
                if overwrite_mode:
                    worker_loop.call_soon_threadsafe(
                        self.repository_utils.save_items,
                        classified_tweet_counter.get_list(), 'classifiers',
                        'ClassifiedTweet', overwrite_mode)
                else:
                    self.repository_utils.save_items(
                        classified_tweet_counter.get_list(), 'classifiers',
                        'ClassifiedTweet', overwrite_mode)

                # Clear list now it has been saved
                classified_tweet_counter.clear()

            classified_tweet_counter.release_lock()

        progress.update(1)

    def classify_tweets(self, since, until, config, overwrite_mode):
        print("Getting tweets...")
        tweets = None

        classification_type = ClassificationType.objects.get(
            id=config['classification_type'])
        is_training = config['is_training']

        if config['tweet_type'] == 'unprocessed':
            values_list = ['id', 'text']
            tweets = self.get_tweets(classification_type, is_training,
                                     overwrite_mode, since, until, values_list)
        elif config['tweet_type'] == 'id_only':
            values_list = ('id', 'id')
            tweets = self.get_tweets(classification_type, is_training,
                                     overwrite_mode, since, until, values_list)
        else:
            tweets = TokenizedTweet.objects.all()
            filter_criteria = Q(id__date__gte=since) & Q(
                id__date__lte=until)

            if not overwrite_mode:
                tweets = tweets.extra(where=[
                    '''NOT EXISTS(SELECT 1 FROM "{classified_tweet}" where 
                    classification_type_id = {classification_type_id} and 
                    tweet_id_id = "{tokenized_tweet}".id_id)'''.format(
                        classified_tweet=ClassifiedTweet._meta.db_table,
                        tokenized_tweet=TokenizedTweet._meta.db_table,
                        classification_type_id=str(classification_type.id))])

            if config['is_training']:
                tweets = TokenizedTweet.objects.all().filter(
                    filter_criteria).values_list('id_id', 'tokens').exclude(
                    id__text__istartswith='RT ').distinct('id_id')
            else:
                tweets = tweets.filter(
                    filter_criteria).values_list('id_id', 'tokens').distinct('id_id')

        print("Got tweets ...")
        print(tweets.count())
        worker_loop = Utils.get_worker_loop()
        pool = ThreadPool(3)
        synchronized_list = SynchronizedList()

        # Retrieve Classifier for given config
        classifier = ClassifierRegistry().get(config['classifier_name'])
        classifier = classifier(config['model'])

        next_batch = list(tweets[:self.batch_size])
        batch_number = 1
        while next_batch:
            attributes_to_classify = []
            tweet_ids = []

            for i in range(0, len(next_batch)):
                (tweet_id, attribute) = next_batch[i]
                attributes_to_classify.append(attribute)
                tweet_ids.append(tweet_id)

            batch_classifications = classifier.classify_batch(
                attributes_to_classify,
                config)

            progress = tqdm(total=len(batch_classifications))
            progress.write('Classifying Batch %d' % batch_number)
            for i in range(0, len(next_batch)):
                pool.add_task(self.process_tweet_classification,
                              synchronized_list, tweet_ids[i],
                              classification_type, batch_classifications[i],
                              config, overwrite_mode, worker_loop,
                              progress)

            pool.wait_completion()

            # Only set offset when overwriting existing tweets as non-overwrite
            # query is dynamic i.e. returns less results each batch.
            tweets = tweets[self.batch_size:]

            next_batch = tweets[:self.batch_size]
            batch_number += 1

        # Save any unsaved classified tweets
        self.repository_utils.save_items(synchronized_list.get_list(),
                                         'classifiers',
                                         'ClassifiedTweet', overwrite_mode)

        worker_loop.call_soon_threadsafe(worker_loop.stop)

    def get_tweets(self, classification_type, is_training, overwrite_mode,
                   since, until, value_list):
        tweets = Tweet.objects.all()
        filter_criteria = Q(date__gte=since) & Q(
            date__lte=until)
        if not overwrite_mode:
            tweets = tweets.extra(where=[
                '''NOT EXISTS(SELECT 1 FROM "{classified_tweet}" where 
                classification_type_id = {classification_type_id} AND "{tweet}".id ="{classified_tweet}".tweet_id_id)'''.format(
                    classified_tweet=ClassifiedTweet._meta.db_table,
                    tweet=Tweet._meta.db_table,
                    classification_type_id=str(classification_type.id))])
        if is_training:
            tweets = tweets.filter(
                filter_criteria).values_list(
                value_list).exclude(text__istartswith='RT ')
        else:
            attribute_1, attribute_2 = value_list
            tweets = tweets.filter(filter_criteria) \
                .values_list(attribute_1, attribute_2).distinct('id')
        return tweets
