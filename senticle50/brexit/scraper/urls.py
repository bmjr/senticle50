from django.conf.urls import url

from . import views

app_name = 'scraper'

urlpatterns = [
    url(r'^api/tweet_count_by_month', views.tweet_count_by_month, name='tweet_count_by_month'),
    url(r'^api/get_most_recent_tweets', views.get_most_recent_tweets, name='get_most_recent_tweets'),
    url(r'^data', views.data, name='data')
]