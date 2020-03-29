import pickle
from multiprocessing import Lock

import numpy as np
from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences
from decimal import Decimal

from classifiers.Classifier import Classifier
from classifiers.ClassifierDecorator import classifier
import redis



@classifier
class KerasClassifier(Classifier):

    def __init__(self, model_to_load):
        # Load Model
        json_file = open(model_to_load['model_json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        self.model.load_weights(model_to_load['model_weights_json'])

        # Load Tokenizer
        tokenizer_file = open(model_to_load['tokenizer_pickle'], 'rb')
        self.tokenizer = pickle.load(tokenizer_file)
        self.lock = Lock()

    def classify(self, text, model_parameters):
        sequences = self.tokenizer.texts_to_sequences([text])
        one_hot_encoded_text_vector = pad_sequences(sequences, maxlen=140,
                                                     padding="post")

        one_hot_encoded_text_vector = np.asarray(one_hot_encoded_text_vector)
        classification = None
        with self.lock:
            classification = self.model.predict(x=one_hot_encoded_text_vector,
                                   batch_size=1)
            predicted_classification = int(np.argmax(
                classification, axis=0))
            prediction_probability = Decimal(
                round(float(classification[predicted_classification]), 10))

        return (predicted_classification, prediction_probability)

    def classify_batch(self, texts, model_parameters):
        sequences = self.tokenizer.texts_to_sequences(texts)
        one_hot_encoded_text_vectors = pad_sequences(sequences, maxlen=140,
                                                     padding="post")

        classifications = []
        with self.lock:
            batch_classification_probabailities = \
                self.model.predict(x=one_hot_encoded_text_vectors,
                                   batch_size=32)

            for classification_probability in batch_classification_probabailities:
                predicted_classification = int(np.argmax(
                    classification_probability, axis=0))
                prediction_probability = Decimal(round(float(classification_probability[
                    predicted_classification]), 10))

                classifications.append(
                    (predicted_classification, prediction_probability))

        return classifications

    @staticmethod
    def get_classifier_name():
        return "KerasClassifier"
