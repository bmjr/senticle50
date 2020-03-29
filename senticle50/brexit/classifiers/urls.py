from django.conf.urls import url

from . import views

app_name = 'classifiers'

urlpatterns = [
    url(r'api/classified_tweet_count_by_day', views.classified_tweet_count_by_day, name='classified_tweet_count_by_day'),
    url(r'(?P<classifier>[a-z-_]+)/year/$', views.preview_data_year),
    url(r'(?P<classifier>[a-z-_]+)/month/$', views.preview_data_month),
    url(r'(?P<classifier>[a-z-_]+)/week/$', views.preview_data_week),
    url(r'(?P<classifier>[a-z-_]+)/day/$', views.preview_data_day),
    url(r'^$', views.analysis, name='analysis'),
    url(r'^top_tweets$', views.top_tweets, name='top_tweets'),
]