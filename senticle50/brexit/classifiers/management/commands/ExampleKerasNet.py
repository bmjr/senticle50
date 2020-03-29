import gensim
import numpy as np
from django.core.management.base import BaseCommand
from keras import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.layers.embeddings import Embedding
from keras.preprocessing.text import Tokenizer
import math

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
                                                        flat=True)).order_by(
            'id__id')

        self.new_model()

    def new_model(self):
        print(len(self.training_classifications))
        print(len(self.training_tokens))

        partition = 0.8
        X = self.training_tokens.values_list(
            'tokens', flat=True)

        Y = self.training_classifications.values_list(
            'classification_value', flat=True)

        leave_tokens = []
        remain_tokens = []

        for i in range(0, len(X)):
            if Y[i] == 0:
                leave_tokens.append((X[i], Y[i]))
            else:
                remain_tokens.append((X[i], Y[i]))

        #print(leave_tokens)
        #print(remain_tokens)

        print(len(leave_tokens), len(remain_tokens))
        class_amount = min(len(leave_tokens), len(remain_tokens))
        print(class_amount)

        training_set = []

        for i in range(0, class_amount):
            training_set.append(leave_tokens[i])
            training_set.append(remain_tokens[i])
            print(i)

        print(len(training_set))

        x_samples = []
        y_samples = []
        for (x,y) in training_set:
            x_samples.append(x)
            y_samples.append(y)

        training_size = math.floor(partition*len(x_samples))

        train_y = y_samples[:training_size]
        test_y = y_samples[training_size:]

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

        tokenizer = Tokenizer(num_words=1000)

        tokenizer.fit_on_texts(self.tweets)

        encoded_x = tokenizer.sequences_to_matrix(
            tokenizer.texts_to_sequences(x_samples), mode='binary')

        train_x = encoded_x[:training_size]
        test_x = encoded_x[training_size:]

        print('Train_X_Length:%d, Train_Y_Length:%d' % (len(train_x), len(
            train_y)))

        print(self.tweets[0])

        brexit_model = Sequential()
        # Word Embeddings
        # Load word embeddings
        print(len(train_x[0]))
        embedding_layer = Embedding(input_dim=len(train_x[0]),
                                    input_length=len(train_x[0]),
                                    output_dim=52,
                                    weights=[model.wv.syn0],
                                    trainable=True)
        embedding_layer.build((None,))
        brexit_model.add(embedding_layer)
        brexit_model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
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

        model_json = brexit_model.to_json()
        with open("lstm_multi_model.json", "w") as json_file:
            json_file.write(model_json)
        brexit_model.save_weights("lstm_multi_model.h5")
        print("Model Saved")
