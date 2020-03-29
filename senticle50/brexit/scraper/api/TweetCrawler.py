import asyncio
import datetime
import json
import re
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from threading import Thread
import random

from pyquery import PyQuery

from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from scraper.managers.TweetManager import TweetManager
from scraper.models import Tweet


def start_tweet_worker(loop):
    """Switch to new event loop and run forever"""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def process_tweet(tweet_counter, tweet, worker_loop):
    tweetPQ = PyQuery(tweet)
    username_tweet = tweetPQ(
        "span:first.username.u-dir b").text()

    links = tweetPQ("a.twitter-timeline-link")

    for link in links.items():
        link_parsed = " " + re.sub(r"\s+", "", link.text()) + " "
        link.replace_with(link_parsed)

    txt = re.sub(r"\s+", " ",
                 tweetPQ("p.js-tweet-text").text().replace(
                     '# ', '#').replace('@ ', '@'))
    retweets = int(tweetPQ(
        "span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
        "data-tweet-stat-count").replace(",", ""))
    favorites = int(tweetPQ(
        "span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
        "data-tweet-stat-count").replace(",", ""))
    dateSec = int(
        tweetPQ("small.time span.js-short-timestamp").attr(
            "data-time"))
    id = tweetPQ.attr("data-tweet-id")

    tweet, created = Tweet.objects.get_or_create(id=id)
    bootstrapped = tweet.bootstrapped
    if created:
        bootstrapped = True
        regex_to_match = '(#voteleave|#strongerin|#brexit)'
        if re.search(r"(^|\W)" + regex_to_match + "\W", txt.lower()):
            bootstrapped = False

    tweet.id = id
    tweet.username = username_tweet
    tweet.text = txt
    tweet.retweets = retweets
    tweet.favorites = favorites
    tweet.date = datetime.datetime.fromtimestamp(dateSec)
    tweet.bootstrapped = bootstrapped

    if tweet.text:
        tweet_counter.add(tweet)

    tweet_counter.get_lock()
    if tweet_counter.get_size_thread_unsafe() >= 200:
        tweets_to_save = tweet_counter.get_list()
        print(tweets_to_save[0].date)
        # Clear list now it has been saved
        tweet_counter.clear()
        worker_loop.call_soon_threadsafe(TweetManager.save_tweets,
                                         tweets_to_save)
    tweet_counter.release_lock()


class Scraper:
    def __init__(self):
        pass

    @staticmethod
    def get_tweets(tweet_criteria, proxy=None):
        refresh_cursor = ''

        results = []
        results_aux = []
        cookie_jar = CookieJar()

        if hasattr(tweet_criteria, 'username') and (
                tweet_criteria.username.startswith(
                    "\'") or tweet_criteria.username.startswith("\"")) and (
                tweet_criteria.username.endswith(
                    "\'") or tweet_criteria.username.endswith("\"")):
            tweet_criteria.username = tweet_criteria.username[1:-1]

        active = True
        dead_requests = 0
        pool = ThreadPool(2)
        tweet_counter = SynchronizedList()

        # Create the new loop and worker thread
        worker_loop = asyncio.new_event_loop()
        worker = Thread(target=start_tweet_worker, args=(worker_loop,))
        worker.start()

        while active:
            #wait = random.randint(0, 5)
            #time.sleep(wait)
            json = Scraper.get_json_reponse(tweet_criteria, refresh_cursor,
                                            cookie_jar, proxy)

            if json is None:
                # Do nothing
                print("Retrying")
                time.sleep(2.5)
            else:
                refresh_cursor = json['min_position']
                if len(json['items_html'].strip()) == 0:
                    dead_requests = dead_requests + 1
                    print("\nNo Items Found > Trying Next Request\n")
                    next_request = Scraper.get_json_reponse(tweet_criteria,
                                                            refresh_cursor,
                                                            cookie_jar, proxy)
                    i = 1
                    while (len(next_request['items_html'].strip()) == 0) and \
                            (i <= 5):
                        refresh_cursor = json['min_position']
                        next_request = Scraper.get_json_reponse(tweet_criteria,
                                                                refresh_cursor,
                                                                cookie_jar,
                                                                proxy)
                        print(i)
                        i += 1

                    if len(next_request['items_html'].strip()) == 0:
                        break
                    else:
                        json = next_request

                refresh_cursor = json['min_position']
                scraped_tweets = PyQuery(json['items_html'])
                scraped_tweets.remove('div.withheld-tweet')
                tweets = scraped_tweets('div.js-stream-tweet')

                if len(tweets) == 0:
                    print("No Tweets")
                    break

                size = len(tweets)
                tweets_left = tweet_criteria.maxTweets - (
                        tweet_counter.get_size_thread_safe() +
                        size)
                if tweets_left <= 0:
                    tweets_to_add = []
                    tweets_to_gather = tweet_criteria.maxTweets - tweet_counter.get_size_thread_safe()
                    for tweet in tweets:
                        if tweets_to_gather == 0:
                            break
                        tweets_to_add.append(tweet)
                        tweets_to_gather -= 1
                    tweets = tweets_to_add

                for tweet in tweets:
                    pool.add_task(process_tweet, tweet_counter, tweet,
                                  worker_loop)

                pool.wait_completion()

                if 0 < tweet_criteria.maxTweets <= tweet_counter.get_size_thread_safe():
                    break

        # Exit program
        worker_loop.call_soon_threadsafe(worker_loop.stop)

        print("Dead Requests: %d" % dead_requests)
        if len(tweet_counter.get_list()) > 0:
            TweetManager.save_tweets(tweet_counter.get_list())

        return results

    @staticmethod
    def get_json_reponse(tweet_criteria, refresh_cursor, cookie_jar, proxy):
        url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&l=en&lang=en&max_position=%s"

        url_get_data = ''

        if hasattr(tweet_criteria, 'username'):
            url_get_data += ' from:' + tweet_criteria.username

        if hasattr(tweet_criteria, 'querySearch'):
            url_get_data += ' ' + tweet_criteria.querySearch

        if hasattr(tweet_criteria, 'near'):
            url_get_data += "&near:" + tweet_criteria.near + " within:" + tweet_criteria.within

        if hasattr(tweet_criteria, 'since'):
            url_get_data += ' since:' + tweet_criteria.since

        if hasattr(tweet_criteria, 'until'):
            url_get_data += ' until:' + tweet_criteria.until

        if hasattr(tweet_criteria, 'topTweets'):
            if tweet_criteria.topTweets:
                url = "https://twitter.com/i/search/timeline?q=%s&src=typd&max_position=%s"

        url = url % (urllib.parse.quote(url_get_data), refresh_cursor)

        headers = [
            ('Host', "twitter.com"),
            ('User-Agent',
             "Mozilla/5.0 (Tablet; rv:26.0) Gecko/26.0 Firefox/26.0"),
            ('Accept', "application/json, text/javascript, */*; q=0.01"),
            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
            ('X-Requested-With', "XMLHttpRequest"),
            ('Referer', url),
            ('Connection', "keep-alive")
        ]

        if proxy:
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({'http': proxy, 'https': proxy}),
                urllib.request.HTTPCookieProcessor(cookie_jar))
        else:
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(cookie_jar))
        opener.addheaders = headers

        try:
            print(url)
            response = opener.open(url)
            json_response = response.read()
        except:
            print("Twitter weird response. Try to see on browser: "
                  "https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(
                url_get_data))
            # sys.exit()
            return None

        dataJson = json.loads(json_response.decode())

        return dataJson
