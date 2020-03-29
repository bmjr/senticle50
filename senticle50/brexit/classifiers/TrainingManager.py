from django.db import models

from classifiers.entities.TrainingTweet import TrainingTweet
from tokenizer.models import TokenizedTweet


class TrainingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_training_set=True)

    @staticmethod
    def get_token_queryset():
        return TokenizedTweet.objects.all()

    def get_training_set(self, classification_type):
        training_set = []
        training_tweets = self.get_queryset().filter(
            classification_type=classification_type)

        for tweet in training_tweets:
            tokens = self.get_token_queryset().filter(
                id=tweet.id).values_list('tokens', flat=True)
            training_set.append(TrainingTweet(
                id=tweet.tweet_id_id,
                classification_type=tweet.classification_type,
                classification_value=tweet.classification_value,
                tokens=tokens
            ))

        return training_set
