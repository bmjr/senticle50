import re
from datetime import datetime

from django.apps import apps

from brexit.celery import app
from tokenizer.TokenizedTweetTransformer import TokenizedTweetTransformer
from scraper.DayTransformer import DayTransformer
import redis


@app.task
def recieve_tweet(tweet_id, tweet_username, tweet_text, tweet_date,
                  tweet_retweets,
                  tweet_favourites):
    ############################################################
    ####             Create Tweet And Save it               ####
    ############################################################
    tweet, created = apps.get_model('scraper', 'Tweet').objects.get_or_create(
        id=tweet_id)
    bootstrapped = tweet.bootstrapped
    if created:
        bootstrapped = True
        regex_to_match = '(#voteleave|#strongerin|#brexit)'
        if re.search(r"(^|\W)" + regex_to_match + "\W", tweet_text.lower()):
            bootstrapped = False

    tweet.id = tweet_id
    tweet.username = tweet_username
    tweet.text = tweet_text
    tweet.retweets = tweet_retweets
    tweet.favorites = tweet_favourites

    tweet_datetime = datetime.strptime(tweet_date, '%a %b %d %H:%M:%S %z %Y')
    tweet.date = tweet_datetime.strftime(
        '%Y-%m-%d %H:%M:%S')
    tweet.bootstrapped = bootstrapped

    # Save Tweet
    tweet.save()

    ############################################################
    ####             Tokenize Tweet And Save it             ####
    ############################################################

    tokenized_tweet = TokenizedTweetTransformer.get_tokenized_tweet(tweet_id,
                                                                    tweet_text)

    if not tokenized_tweet:
        return

    tokenized_tweet.save()

    with redis.Redis().lock("day_lock"):
        day = DayTransformer.get_day(tweet_datetime.strftime('%Y-%m-%d'))
        day.tweet_number += 1
        day.save()

    return 'ok'

@app.task
def check(param):
    return 'The test task executed with argument "%s" ' % param
