import pickle

from django.db.models.query import Q
from keras.preprocessing.sequence import pad_sequences

from classifiers.ClassifiedTweetTransformer import ClassifiedTweetTransformer
from classifiers.models import ClassifiedTweet
from scraper.models import Tweet
from utils.DatabaseManager import DatabaseManager


class OrderOfWordsService:
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

    def get_similar_tweets(self):
        # Load Tokenizer
        tokenizer_file = open('xlreduced_features_brexit_stance_tokenizer.pickle', 'rb')
        tokenizer = pickle.load(tokenizer_file)
        print("Getting tweets...")
        tweets = ClassifiedTweet.objects.all() \
            .values_list('tweet_id_id', 'tweet_id_id__text').distinct('tweet_id_id')
        print('Got tweets')

        next_batch = list(tweets[:self.batch_size])
        identical_tweets = {}

        while next_batch:
            tweet_texts = []
            tweet_ids = []

            for i in range(0, len(next_batch)):
                (tweet_id, text) = next_batch[i]
                tweet_texts.append(text)
                tweet_ids.append(tweet_id)

            sequences = tokenizer.texts_to_sequences(tweet_texts)
            one_hot_encoded_text_vectors = pad_sequences(sequences, maxlen=140,
                                                         padding="post")

            for i in range(0, len(one_hot_encoded_text_vectors)):
                key = hash(str(one_hot_encoded_text_vectors[i]))
                if key not in identical_tweets:
                    identical_tweets[key] = [int(tweet_ids[i])]
                else:
                    identical_tweets[key].append(int(tweet_ids[i]))

            print('\n IDENTICAL TWEETS')
            for key in identical_tweets:
                if len(identical_tweets[key]) > 1:
                    print(identical_tweets[key])
            print('\n')

            tweets = tweets[self.batch_size:]

            next_batch = tweets[:self.batch_size]
            #print(identical_tweets)