from django.db import models

from scraper import models as scraper_models


class TokenizedTweet(models.Model):
    """ An object that represents a tweet that has been Tokenized (preprocessed)
        into a representation which is ready to vectorized and classified.


    The tokenized object contains the original id of the tweet and a
    transformed string from which the original text has been transformed
    into using a number of tokenization steps.
    """
    id = models.OneToOneField(scraper_models.Tweet, on_delete=models.CASCADE,
                              primary_key=True, blank=True, null=False)
    tokens = models.TextField(max_length=280, blank=True, null=False)

    class Meta:
        managed = True
        db_table = 'Tokenized_Tweet'
        verbose_name = 'Tokenized_Tweet'
