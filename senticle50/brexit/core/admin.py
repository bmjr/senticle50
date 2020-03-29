from django.contrib import admin

# Register your models here.
from scraper.models import Tweet
from classifiers.models import ClassificationType, ClassifiedDay


admin.site.register(Tweet)
admin.site.register(ClassificationType)
admin.site.register(ClassifiedDay)
