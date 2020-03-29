# -*- coding: utf-8 -*-
import getopt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

# This should be the directory that contains the directory containing settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brexit.settings.production")
import django

django.setup()

print(os.path.join(os.path.dirname(__file__), ".."))
from scraper.api.TweetCriteria import TweetCriteria
from scraper.api.TweetCrawler import Scraper


def main(argv):
    if len(argv) == 0:
        print('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        f = open('exporter_help_text.txt', 'r')
        print(f.read())
        f.close()

        return

    try:
        opts, args = getopt.getopt(argv, "", (
            "username=", "near=", "within=", "since=", "until=",
            "querysearch=",
            "toptweets", "maxtweets=", "output="))

        tweetCriteria = TweetCriteria()
        outputFileName = "output_got.csv"

        for opt, arg in opts:
            if opt == '--username':
                tweetCriteria.username = arg

            elif opt == '--since':
                tweetCriteria.since = arg

            elif opt == '--until':
                tweetCriteria.until = arg

            elif opt == '--querysearch':
                tweetCriteria.querySearch = arg

            elif opt == '--toptweets':
                tweetCriteria.topTweets = True

            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)

            elif opt == '--near':
                tweetCriteria.near = '"' + arg + '"'

            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'

            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'

            elif opt == '--output':
                outputFileName = arg

        print('Searching...\n')

        tweets = Scraper.get_tweets(tweetCriteria)
        print(len(tweets))

    except arg:
        print('Arguments parser error, try -h' + arg)
    finally:
        print('Done. Output file generated "%s".' % outputFileName)


if __name__ == '__main__':
    main(sys.argv[1:])
