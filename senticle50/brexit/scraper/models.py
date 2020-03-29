from django.db import models


# Create your models here.

# TODO: Scrap tweets with 280 characters

class Tweet(models.Model):
    id = models.DecimalField(primary_key=True, max_digits=64, decimal_places=0)
    username = models.CharField(max_length=50, blank=True, null=False)
    text = models.TextField(max_length=280, blank=True, null=False)
    retweets = models.IntegerField(blank=True, null=False)
    favorites = models.IntegerField(blank=True, null=False)
    date = models.DateTimeField(blank=True, null=False, db_index=True)
    bootstrapped = models.BooleanField(blank=True, default=False)

    class Meta:
        managed = True
        db_table = 'Tweet'
        verbose_name = 'Tweet'


class Day(models.Model):
    date = models.DateField(primary_key=True)
    tweet_number = models.DecimalField(max_digits=15, decimal_places=0,
                                       default=0)

    class Meta:
        managed = True
        db_table = 'Day'
        verbose_name = 'Day'