import gensim
import numpy as np
from django.core.management.base import BaseCommand
from keras import Sequential
from keras.layers import Dense, Flatten, Dropout, Convolution1D, LSTM
from keras.layers.embeddings import Embedding
from keras.models import model_from_json
from keras.preprocessing.text import Tokenizer

from classifiers.models import ClassifiedTweet
from tokenizer.models import TokenizedTweet


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'

    def handle(self, *args, **options):

        self.training_classifications = ClassifiedTweet.objects.all().filter(
            is_training_set=True).order_by('id__id')

        self.tweets = TokenizedTweet.objects.all().values_list('tokens',
                                                               flat=True)

        self.training_tokens = TokenizedTweet.objects.all().filter(
            id__id__in=self.training_classifications.values_list('id__id',
                                                                 flat=True)).order_by(
            'id__id')

        self.training_classifications = self.training_classifications.filter(
            id__id__in=self.training_tokens.values_list('id__id',
                                                        flat=True)).order_by('id__id')

        self.new_model()

    def predict_model(self):
        print(len(self.training_classifications))
        print(len(self.training_tokens))

        partition = len(self.training_tokens) - 500
        X = self.training_tokens.values_list(
            'tokens', flat=True)

        train_y = self.training_classifications.values_list(
            'classification_value', flat=True)[:partition]
        test_y = self.training_classifications.values_list(
            'classification_value', flat=True)[partition:]

        # print(len(train_x), len(test_x))
        # print(len(train_y), len(test_y))

        # print(train_x[0], train_y[0])

        # for i in range(0, len(training_classifications)):
        #     print(training_classifications[i])
        #     print(training_tokens[i])

        print('%d Tokenized Tweets' % len(self.tweets))
        sentences = []
        for tweet in self.tweets:
            sentences.append(tweet.split())
        # sentences = [['first', 'sentence'], ['second', 'sentence']]
        model = gensim.models.Word2Vec(min_count=100, window=5)
        model.build_vocab(sentences, keep_raw_vocab=True)
        model.train(sentences, total_examples=model.corpus_count,
                    epochs=model.iter)
        model.wv.save_word2vec_format('word_embeddings' + '.model.txt',
                                      binary=False)

        tokenizer = Tokenizer()

        tokenizer.fit_on_texts(self.tweets)

        # indexed_tweets = tokenizer.texts_to_sequences(tweets)

        # one_hot_encoded_tweets = tokenizer.sequences_to_matrix(
        #    indexed_tweets, mode='binary')

        encoded_x = tokenizer.sequences_to_matrix(
            tokenizer.texts_to_sequences(X), mode='binary')

        # print(indexed_tweets[0])
        # print(one_hot_encoded_tweets[0])
        print(self.tweets[0])
        # print(OrderedDict(
        #    sorted(tokenizer.word_index.items(), key=lambda t: t[1])))

        # load json and create model
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model.h5")
        print("Loaded model from disk")

        test_sample = encoded_x[0]
        print(test_sample)
        print(test_sample.shape)
        test_sample = [test_sample]
        print(test_sample)
        test_sample = np.asarray(test_sample)
        print(test_sample.shape)

        print(loaded_model.predict_proba(test_sample))

    def new_model(self):
        print(len(self.training_classifications))
        print(len(self.training_tokens))

        partition = len(self.training_tokens) - 500
        X = self.training_tokens.values_list(
            'tokens', flat=True)

        train_y = self.training_classifications.values_list(
            'classification_value', flat=True)[:partition]
        test_y = self.training_classifications.values_list(
            'classification_value', flat=True)[partition:]

        # print(len(train_x), len(test_x))
        # print(len(train_y), len(test_y))

        # print(train_x[0], train_y[0])

        # for i in range(0, len(training_classifications)):
        #     print(training_classifications[i])
        #     print(training_tokens[i])

        print('%d Tokenized Tweets' % len(self.tweets))
        sentences = []
        for tweet in self.tweets:
            sentences.append(tweet.split())
        # sentences = [['first', 'sentence'], ['second', 'sentence']]
        model = gensim.models.Word2Vec(min_count=5, window=5)
        model.build_vocab(sentences, keep_raw_vocab=True)
        model.train(sentences, total_examples=model.corpus_count,
                    epochs=model.iter)
        model.wv.save_word2vec_format('word_embeddings' + '.model.txt',
                                      binary=False)
        #
        # model = gensim.models.Word2Vec.load('word_embeddings.model.txt')


        tokenizer = Tokenizer()

        tokenizer.fit_on_texts(self.tweets)

        # indexed_tweets = tokenizer.texts_to_sequences(tweets)

        # one_hot_encoded_tweets = tokenizer.sequences_to_matrix(
        #    indexed_tweets, mode='binary')

        encoded_x = tokenizer.sequences_to_matrix(
            tokenizer.texts_to_sequences(X), mode='binary')

        train_x = encoded_x[:partition]
        test_x = encoded_x[partition:]

        print('Train_X_Length:%d, Train_Y_Length:%d' % (len(train_x), len(
            train_y)))

        # print(indexed_tweets[0])
        # print(one_hot_encoded_tweets[0])
        print(self.tweets[0])
        # print(OrderedDict(
        #    sorted(tokenizer.word_index.items(), key=lambda t: t[1])))

        brexit_model = Sequential()
        # Word Embeddings
        # Load word embeddings
        #print(len(model.wv.syn0))
        print(len(train_x[0]))
        embedding_layer = Embedding(input_dim=len(train_x[0]),
                                    input_length=len(train_x[0]),
                                    output_dim=52,
                                    weights=[model.wv.syn0],
                                    trainable=True)
        #weights=[model.wv.syn0],
        embedding_layer.build((None,))
        # embedding_layer.set_weights([model.wv.syn0])
        brexit_model.add(embedding_layer)
        # brexit_model.add(Flatten(input_shape=(None, 256)))
        # brexit_model.add(LSTM(32, return_sequences=True))
        # brexit_model.add(
        #     Dense(
        #         units=16,
        #         activation='relu'
        #     )
        # )
        # brexit_model.add(Dropout(0.5))
        # brexit_model.add(Flatten(input_shape=(None, 256)))
        # brexit_model.add(Dense(1, activation='relu'))
        print('here')
        brexit_model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
        print('after')
        #brexit_model.add(Convolution1D(32, 2, border_mode='same'))
        #brexit_model.add(Convolution1D(16, 2, border_mode='same'))
        #brexit_model.add(Convolution1D(8, 2, border_mode='same'))
        #brexit_model.add(Flatten())
        brexit_model.add(Dropout(0.5))
        brexit_model.add(Dense(64, activation='sigmoid'))
        brexit_model.add(Dropout(0.2))
        brexit_model.add(Dense(1, activation='sigmoid'))

        brexit_model.compile(loss='binary_crossentropy',
                             optimizer='adam', metrics=['accuracy'])
        print(brexit_model.summary())

        brexit_model.fit(train_x, np.asarray(list(train_y)),
                         validation_data=(
                             test_x, np.asarray(list(test_y))), epochs=3,
                         batch_size=128,
                         verbose=2)
        scores = brexit_model.evaluate(test_x, np.asarray(list(test_y)),
                                       verbose=0)
        print("Accuracy: %.2f%%" % (scores[1] * 100))

        # serialize model to JSON
        model_json = brexit_model.to_json()
        with open("lstm_multi_model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        brexit_model.save_weights("lstm_multi_model.h5")
        print("Saved model to disk")

        # for tweet in test_x:
        #    print(tweet)
        #    print(tweet, brexit_model.predict_proba(tweet,
        #batch_size = 128))

        # brexit_model.predict_proba(test_x[0])
        #
        # # model.save_weights('word_embeddings_model')
        # # print('Vocab Size: %d' % len(model.wv.vocab))
        # # print('Remain/Leave Similarity: %d' % model.similarity('remain',
        # #                                                       'leave'))
        # # print('Labour/Tori Similarity: %d' % model.similarity('labour',
        # #                                                      'tori'))

        # print(model.similar_by_word('good', 10))  # Get two most similar
        # words to 'hack'

        # print(model.similar_by_word('brexit', 10))  # Get two most similar
        # words to 'hack'
        # print(model.similar_by_word('labour', 10))  # Get two most similar

        # print(model.similar_by_word('tori', 10))  # Get two most similar

        # print(model.raw_vocab.keys())
        #
        # # integer encode
        # label_encoder = LabelEncoder()
        # integer_encoded = label_encoder.fit_transform(
        #     array(list(model.raw_vocab.keys())))
        # print(len(list(model.raw_vocab.keys())))
        # print(integer_encoded)
        #
        # # binary encode
        # onehot_encoder = OneHotEncoder(sparse=False)
        # integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        # onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        # print(onehot_encoded)
        #
        # # invert first example
        # # transformed = label_encoder.transform(['banana'])
        # # print(transformed)
        # # inverted = label_encoder.inverse_transform(transformed)
        # # print(inverted)
        #
        # max_tweet_word_length = max([len(sentence) for sentence in sentences])
        # print(max_tweet_word_length)
        #
        # # Transform Sentences into encoded One Hot Vectors.
        # ohe = []
        # for sentence in sentences:
        #     sentence_transformed = label_encoder.transform(sentence)
        #     sentence_encoded = onehot_encoder.transform(
        #         sentence_transformed.reshape(1, -1))
        #     print(sentence_encoded)
        #     ohe.append(sentence_encoded)
        # np.set_printoptions(threshold=np.inf)
        # one_hot_encoded_vectors = np.asarray(ohe)
        #
        # print(one_hot_encoded_vectors[2])
        # tweet_matrices = sequence.pad_sequences(one_hot_encoded_vectors,
        #                                         maxlen=max_tweet_word_length,
        #                                         dtype='int32',
        #                                         padding='post', value=0)
        # print(tweet_matrices[2])
        #
        # brexit_model = Sequential()
        # brexit_model.add(Dense(max_tweet_word_length))

        # One Hot Encode Sentences
        # sentences_encoded = onehot_encoder.transform(ohe)
        # print(sentences_encoded)

        # max_ohc_enc_length = min([len(encoded) for encoded in onehot_encoded])
        # np.set_printoptions(threshold=np.inf)
        # print(onehot_encoded[1])
        # print(onehot_encoded[1].dot(onehot_encoder.active_features_).astype(int))
        # print(label_encoder.inverse_transform(onehot_encoded[1].dot(
        #     onehot_encoder.active_features_).astype(int)))

        # transformed_sentence = label_encoder.transform(sentences[0])
        # print(transformed_sentence)
        # print(label_encoder.inverse_transform(transformed_sentence))
        #
        # onehot_encoded = onehot_encoder.transform(
        #     transformed_sentence.reshape(-1, 1))
        # print(onehot_encoded)
        # print(onehot_encoded)
        # inverse_ohc = onehot_encoded.dot(onehot_encoder.active_features_).astype(int)
        # print(inverse_ohc)
        # print(label_encoder.inverse_transform(inverse_ohc))

        # tweet_matrices = sequence.pad_sequences(tweet_matrices, maxlen=280,
        #                                       dtype='int32',
        #                                       padding='post', value=0)

        # print('Vocab: %s' % model.wv.vocab)
