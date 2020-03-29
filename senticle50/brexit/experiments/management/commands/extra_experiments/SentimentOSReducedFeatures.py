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
from imblearn.over_sampling import RandomOverSampler, SMOTE

from scraper.models import Tweet


class Command(BaseCommand):
    help = 'Classifies tweets in given date range'

    def handle(self, *args, **options):
        # self.training_classifications = ClassifiedTweet.objects.all().filter(
        #     is_training_set=True).order_by('id__id')
        #
        # self.tweets = TokenizedTweet.objects.all().values_list('tokens',
        #                                                        flat=True)
        #
        # self.training_tokens = TokenizedTweet.objects.all().filter(
        #     id__id__in=self.training_classifications.values_list('id__id',
        #                                                          flat=True)).order_by(
        #     'id__id')
        #
        # self.training_classifications = self.training_classifications.filter(
        #     Q(id__id__in=self.training_tokens.values_list('id__id', flat=True))
        #     & Q(classification_type_id=5)).order_by(
        #     'id__id')

        self.new_model()

    def new_model(self):
        # print(len(self.training_classifications))
        # print(len(self.training_tokens))

        partition = 0.8

        tweets = list(
            Tweet.objects.filter(classifiedtweet__classification_type=6,
                                 classifiedtweet__is_training_set=1,
                                 classifiedtweet__isnull=False,
                                 tokenizedtweet__isnull=False) \
                .values('tokenizedtweet__tokens',
                        'classifiedtweet__classification_value'))

        x_samples = []

        positive_tokens = []
        negative_tokens = []

        tweets_length = len(tweets)
        print(tweets_length)
        for i in range(0, tweets_length):
            tweet = tweets[i]
            if tweet['classifiedtweet__classification_value'] == 0:
                positive_tokens.append((tweet['tokenizedtweet__tokens'], tweet[
                    'classifiedtweet__classification_value']))
            else:
                negative_tokens.append((tweet['tokenizedtweet__tokens'], tweet[
                    'classifiedtweet__classification_value']))

        # print(positive_tokens)
        # print(negative_tokens)

        random.shuffle(positive_tokens)
        random.shuffle(negative_tokens)

        positive_token_length = len(positive_tokens)
        negative_token_length = len(negative_tokens)
        print(positive_token_length, negative_token_length)
        # Get min class number
        class_amount = min(positive_token_length, negative_token_length)
        print(class_amount)

        validation_size = class_amount - math.floor(partition * class_amount)

        validation_set = []

        for i in range(0, validation_size):
            validation_set.append(positive_tokens[(positive_token_length-1) - i])
            validation_set.append(negative_tokens[(negative_token_length-1) - i])

        validation_x = []
        validation_y = []

        for (x, y) in validation_set:
            x_samples.append(x)
            validation_x.append(x)
            validation_y.append(int(y))

        training_set = []

        training_set.extend(
            positive_tokens[:positive_token_length - validation_size])
        training_set.extend(
            negative_tokens[:negative_token_length - validation_size])

        print(len(training_set))

        train_x = []
        train_y = []
        for (x, y) in training_set:
            x_samples.append(x)
            train_x.append(x)
            train_y.append(int(y))

        # print('%d Tokenized Tweets' % len(self.tweets))
        # sentences = []
        # for tweet in self.tweets:
        #     sentences.append(tweet.split())
        # # sentences = [['first', 'sentence'], ['second', 'sentence']]
        # model = gensim.models.Word2Vec(min_count=5, window=5, max_vocab_size=5000)
        # model.build_vocab(sentences, keep_raw_vocab=True)
        # model.train(sentences, total_examples=model.corpus_count,
        #             epochs=model.iter)
        # model.wv.save_word2vec_format('word_embeddings' + '.model.txt',
        #                               binary=False)

        tokenizer = Tokenizer(num_words=5000)

        tokenizer.fit_on_texts(x_samples)

        # Save the tokenizer
        with open('os_reduced_features_sentiment_tokenizer.pickle',
                  'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        train_x = tokenizer.texts_to_sequences(train_x)
        print(train_x[0])
        train_x = pad_sequences(train_x, maxlen=140, padding="post")

        print(len(train_x), len(train_y))
        train_x, train_y = SMOTE(random_state=0, ratio='minority').fit_sample(train_x, train_y)
        print(len(train_x), len(train_y))

        validation_x = tokenizer.texts_to_sequences(validation_x)
        print(validation_x[0])
        validation_x = pad_sequences(validation_x, maxlen=140, padding="post")

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
                                activation='relu',
                                kernel_regularizer=l2(0.01)))
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
                             validation_x, np.asarray(list(validation_y))),
                         epochs=30,
                         batch_size=128,
                         verbose=2,
                         callbacks=[
                             EarlyStopping(monitor='val_acc', min_delta=0.01,
                                           patience=20, verbose=1,
                                           mode='auto')])
        scores = brexit_model.evaluate(validation_x,
                                       np.asarray(list(validation_y)),
                                       verbose=0)
        print("Accuracy: %.2f%%" % (scores[1] * 100))

        correct_classifications = 0
        classifications_with_threshold = 0
        for i in range(0, len(validation_x)):
            predict_probabailities = brexit_model.predict(
                np.asarray(validation_x[i:i + 1]))
            if predict_probabailities[0][0] <= 0.4 or \
                    predict_probabailities[0][0] >= 0.6:
                predicted_index = np.argmax(predict_probabailities[0], axis=0)
                classifications_with_threshold += 1
                if predicted_index == validation_y[i]:
                    correct_classifications += 1

        print('Threshold 0.6 %d/%d correct' % (
            correct_classifications, classifications_with_threshold))

        correct_classifications = 0
        classifications_with_threshold = 0
        for i in range(0, len(validation_x)):
            predict_probabailities = brexit_model.predict(
                np.asarray(validation_x[i:i + 1]))
            if predict_probabailities[0][0] <= 0.3 or \
                    predict_probabailities[0][0] >= 0.7:
                predicted_index = np.argmax(predict_probabailities[0], axis=0)
                classifications_with_threshold += 1
                if predicted_index == validation_y[i]:
                    correct_classifications += 1

        print('Threshold 0.7 %d/%d correct' % (correct_classifications,
                                               classifications_with_threshold))

        np.set_printoptions(threshold=np.nan)
        print(brexit_model.predict(validation_x))

        y_pred = brexit_model.predict_classes(validation_x)

        from sklearn.metrics import classification_report
        print('\n Classification Report \n')
        pred_y = brexit_model.predict_classes(validation_x)
        print(classification_report(validation_y, pred_y))

        model_json = brexit_model.to_json()
        with open("os_reduced_features_sentiment_keras_model.json",
                  "w") as json_file:
            json_file.write(model_json)
        brexit_model.save_weights(
            "os_reduced_features_sentiment_keras_weights.h5")
        print("Model Saved")
