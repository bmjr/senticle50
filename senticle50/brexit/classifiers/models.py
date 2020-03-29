from django.db import models

from classifiers.TrainingManager import TrainingManager
from scraper.models import Tweet


class ClassificationType(models.Model):
    id = models.DecimalField(primary_key=True, max_digits=2, decimal_places=0)
    name = models.CharField(max_length=50, blank=False, null=False)
    display_title = models.CharField(max_length=50, blank=False, null=False, default="")
    display_text = models.TextField(max_length=5000, blank=False, null=False, default="")
    is_previewable = models.BooleanField(blank=True, default=True)

    class Meta:
        managed = True
        db_table = 'Classification_Type'
        verbose_name = 'Classification_Type'


class Label(models.Model):
    id = models.DecimalField(primary_key=True, max_digits=2, decimal_places=0)
    classification_type = models.ForeignKey(ClassificationType,
                                            on_delete=models.CASCADE)
    classification_value = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=50, blank=False, null=False)
    color = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'Label'
        verbose_name = 'Label'


class ClassifiedDay(models.Model):
    date = models.DateField()
    classification_type = models.ForeignKey(ClassificationType,
                                            on_delete=models.CASCADE)
    classification_value = models.DecimalField(max_digits=10, decimal_places=0)
    amount_classified = models.DecimalField(max_digits=10, decimal_places=0,
                                            default=0)

    class Meta:
        unique_together = ('date', 'classification_type',
                           'classification_value')
        managed = True
        db_table = 'Classified_Day'
        verbose_name = 'Classified_Day'


class ClassifiedTweet(models.Model):
    id = models.AutoField(primary_key=True)
    tweet_id = models.ForeignKey(Tweet, on_delete=models.CASCADE,
                              blank=True, null=False)
    classification_type = models.ForeignKey(ClassificationType,
                                            on_delete=models.CASCADE)

    classification_value = models.DecimalField(max_digits=10,
                                               decimal_places=0)

    classification_probability = models.DecimalField(max_digits=10,
                                               decimal_places=9, db_index=True)

    is_training_set = models.BooleanField(blank=True, default=False)

    training_manager = TrainingManager()
    objects = models.Manager()

    class Meta:
        unique_together = ('tweet_id', 'classification_type')
        managed = True
        db_table = 'Classified_Tweet'
        verbose_name = 'Classified_Tweet'
