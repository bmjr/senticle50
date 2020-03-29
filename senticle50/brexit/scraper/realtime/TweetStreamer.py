import json
import time

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

from scraper.tasks import recieve_tweet

# Twitter Senticle50 API credentials
access_token = "access_token"
access_secret = "access_secret"
customer_key = "customer_key"
customer_secret = "customer_secret"

general_hashtags = ['#BREXIT', '#ARTICLE50', '#BREXITDEBATE',
                    '#BREXITMEANSBREXIT', '#EUREFERENDUM', '#EUREF']
leave_hashtags = ['#VOTELEAVE', '#BREXITEER', '#IVOTEDLEAVE', '#LEAVEEU',
                  '#TAKEBACKCONTROL', '#VOTEOUT']
remain_hashtags = ['#STRONGERIN', '#REMAIN', '#REMOANER', '#REMAININEU',
                   '#VOTEREMAIN', '#STRONGERTOGETHER']

tracked_hashtags = []
tracked_hashtags.extend(general_hashtags)
tracked_hashtags.extend(leave_hashtags)
tracked_hashtags.extend(remain_hashtags)


class TweepyStreamHandler(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        if 'text' in all_data:
            id = all_data['id']
            username = all_data["user"]["screen_name"]
            if ('extended_tweet' in all_data) and ('full_text' in all_data["extended_tweet"]):
                tweet = all_data["extended_tweet"]['full_text']
            else:
                tweet = all_data["text"]
            date = all_data["created_at"]
            retweets = all_data["retweet_count"]
            favourites = all_data["favorite_count"]

            recieve_tweet.delay(id, username, tweet, date, retweets,
                                favourites)

            return True

    def on_timeout(self):
        time.sleep(180)
        return True  # To carry on listening

    def on_error(self, status):
        print('ERROR: %s' % status)
        time.sleep(180)
        return False  # To carry on listening


def get_tweets():
    # Authorize
    auth = OAuthHandler(customer_key, customer_secret)
    auth.set_access_token(access_token, access_secret)

    # Initialise Stream
    twitter_stream = Stream(auth, TweepyStreamHandler(), tweet_mode='extended')
    while True:
        try:
            twitter_stream.filter(track=tracked_hashtags,
                                  languages=["en"], stall_warnings=True)
        except Exception:
            print(Exception)
        twitter_stream.disconnect()
        time.sleep(120)
