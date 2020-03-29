import math
import pickle
import random

import numpy as np
from django.core.management.base import BaseCommand
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, Dropout
from keras.layers.embeddings import Embedding
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.regularizers import l2

from classifiers.models import ClassifiedTweet
from scraper.models import Tweet
from tokenizer.models import TokenizedTweet


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'

    def handle(self, *args, **options):
        self.training_classifications = ClassifiedTweet.objects.all().filter(
            is_training_set=True).order_by('tweet_id__id')

        self.tweets = TokenizedTweet.objects.all().values_list('tokens',
                                                               flat=True)

        self.training_tokens = TokenizedTweet.objects.all().filter(
            id__id__in=self.training_classifications.values_list('tweet_id_id',
                                                                 flat=True)).order_by(
            'tweet_id_id')

        self.training_classifications = self.training_classifications.filter(
            tweet_id__id__in=self.training_tokens.values_list('id_id__id',
                                                              flat=True)).order_by(
            'tweet_id_id')

        self.new_model()

    def new_model(self):
        # print(len(self.training_classifications))
        # print(len(self.training_tokens))

        partition = 0.8

        tweets = list(
            Tweet.objects.filter(classifiedtweet__classification_type=5,
                                 classifiedtweet__is_training_set=1,
                                 classifiedtweet__isnull=False,
                                 tokenizedtweet__isnull=False) \
            .values('tokenizedtweet__tokens',
                    'classifiedtweet__classification_value'))

        leave_tokens = []
        remain_tokens = []

        tweets_length = len(tweets)
        print(tweets_length)
        for i in range(0, tweets_length):
            tweet = tweets[i]
            if tweet['classifiedtweet__classification_value'] == 0:
                leave_tokens.append((tweet['tokenizedtweet__tokens'], tweet[
                    'classifiedtweet__classification_value']))
            else:
                remain_tokens.append((tweet['tokenizedtweet__tokens'], tweet[
                    'classifiedtweet__classification_value']))
            print(i)

        # print(leave_tokens)
        # print(remain_tokens)

        random.shuffle(leave_tokens)
        random.shuffle(remain_tokens)

        # print(len(leave_tokens), len(remain_tokens))
        class_amount = min(len(leave_tokens), len(remain_tokens))
        print(class_amount)

        training_set = []

        for i in range(0, class_amount):
            training_set.append(leave_tokens[i])
            training_set.append(remain_tokens[i])
            print(i)

        print(len(training_set))
        print(training_set)

        x_samples = []
        y_samples = []
        for (x, y) in training_set:
            x_samples.append(x)
            y_samples.append(int(y))

        training_size = math.floor(partition * len(x_samples))

        train_y = y_samples[:training_size]
        test_y = y_samples[training_size:]

        tokenizer = Tokenizer(num_words=5000)

        tokenizer.fit_on_texts(x_samples)

        # Save the tokenizer
        with open('brexit_stance_tokenizer.pickle', 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        encoded_x = tokenizer.texts_to_sequences(x_samples)
        print(encoded_x[0])
        encoded_x = pad_sequences(encoded_x, maxlen=140, padding="post")

        train_x = encoded_x[:training_size]
        test_x = encoded_x[training_size:]

        print('Train_X_Length:%d, Train_Y_Length:%d' % (len(train_x), len(
            train_y)))

        print(train_x[0])
        # print(tokenizer.word_index[61])

        brexit_model = Sequential()
        # Word Embeddings
        # Load word embeddings
        print(len(train_x[0]))
        embedding_layer = Embedding(input_dim=len(tokenizer.word_index) + 1,
                                    input_length=len(train_x[0]),
                                    output_dim=100,
                                    trainable=True)
        embedding_layer.build((None,))
        brexit_model.add(embedding_layer)
        brexit_model.add(Conv1D(filters=128, kernel_size=5,
                                activation='relu'))
        brexit_model.add(MaxPooling1D(pool_size=5))
        brexit_model.add(Dropout(0.5))
        brexit_model.add(Conv1D(filters=128, kernel_size=5,
                                activation='relu',
                                kernel_regularizer=l2(0.01)))
        brexit_model.add(MaxPooling1D(pool_size=5))
        brexit_model.add(Flatten())
        brexit_model.add(Dense(128, activation='relu'))
        brexit_model.add(Dropout(0.5))
        brexit_model.add(Dense(2, activation='softmax'))
        brexit_model.compile(loss='sparse_categorical_crossentropy',
                             optimizer='adam', metrics=['accuracy'])
        print(brexit_model.summary())

        brexit_model.fit(train_x, np.asarray(list(train_y)),
                         validation_data=(
                             test_x, np.asarray(list(test_y))), epochs=30,
                         batch_size=128,
                         verbose=2,
                         callbacks=[
                             EarlyStopping(monitor='val_acc', min_delta=0.01,
                                           patience=3, verbose=1,
                                           mode='auto')])
        scores = brexit_model.evaluate(test_x, np.asarray(list(test_y)),
                                       verbose=0)
        print("Accuracy: %.2f%%" % (scores[1] * 100))

        correct_classifications = 0
        classifications_with_threshold = 0
        for i in range(0, len(test_x)):
            predict_probabailities = brexit_model.predict(
                np.asarray(test_x[i:i + 1]))
            if predict_probabailities[0][0] <= 0.4 or \
                    predict_probabailities[0][0] >= 0.6:
                predicted_index = np.argmax(predict_probabailities[0], axis=0)
                classifications_with_threshold += 1
                if predicted_index == test_y[i]:
                    correct_classifications += 1

        print('Threshold 0.6 %d/%d correct' % (
        correct_classifications, classifications_with_threshold))

        correct_classifications = 0
        classifications_with_threshold = 0
        for i in range(0, len(test_x)):
            predict_probabailities = brexit_model.predict(
                np.asarray(test_x[i:i + 1]))
            if predict_probabailities[0][0] <= 0.3 or \
                    predict_probabailities[0][0] >= 0.7:
                predicted_index = np.argmax(predict_probabailities[0], axis=0)
                classifications_with_threshold += 1
                if predicted_index == test_y[i]:
                    correct_classifications += 1

        print('Threshold 0.7 %d/%d correct' % (correct_classifications,
                                               classifications_with_threshold))

        np.set_printoptions(threshold=np.nan)
        print(brexit_model.predict(test_x))

        y_pred = brexit_model.predict_classes(test_x)

        from sklearn.metrics import classification_report
        print('\n Classification Report \n')
        pred_y = brexit_model.predict_classes(test_x)
        print(classification_report(test_y, pred_y))

        model_json = brexit_model.to_json()
        with open("brexit_stance_keras_model.json", "w") as json_file:
            json_file.write(model_json)
        brexit_model.save_weights("brexit_stance_keras_weights.h5")
        print("Model Saved")
